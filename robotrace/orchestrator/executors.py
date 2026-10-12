from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from simulator.adapter import ADAPTER_VERSION, run_trial
from simulator.adapter.headless import score_description
from orchestrator.evidence import keep_telemetry, mode_of, summarise_payload

from .controller import ActionResult
from .history import CHARS_PER_TOKEN, build_history
from .io import digest
from .map_package import ActionDefinition, MapPackage
from .validators import CUT_OFF_MARKER, BudgetExhausted, ContractFailure, validate_controller, validate_geometry


def _design(iteration: int) -> dict[str, Any]:
    return {
        "geometry": {
            "sensor_positions": [{"x": x, "y": 0.05} for x in (-0.06, -0.03, 0.0, 0.03, 0.06)],
            "sensor_size": 0.012, "wheel_track": 0.12, "wheel_radius": 0.035,
            "body_width": 0.12, "body_length": 0.16, "mass": 0.8,
        },
        "controller": {
            "base_speed": round(0.42 + iteration * 0.02, 3), "kp": 4.2,
            "ki": 0.03, "kd": 0.9, "sensor_weights": [-1, -0.5, 0, 0.5, 1],
            "line_loss": "last_direction",
        },
        "observation_request": {"measurements": ["completion", "progress", "completion_time", "rms_error", "line_loss_events"]},
    }


DESIGN_FIELDS = ("geometry", "controller", "observation_request")

# Room reserved for the fixed system message when sizing a history pack from the remaining token budget.
SYSTEM_PROMPT_ALLOWANCE = 1500
MIN_OUTPUT_TOKENS = 500  # a call that cannot leave at least this much for the answer is not made
SYSTEM_PROMPT = ("Return one JSON object keyed by the entity IDs you update. Every value must match that entity's supplied contract. Every entity in required_outputs MUST be present, or the team cannot be scored. "
    "Your role, your work and your team are described in instructions and your_role; downstream_dependents shows who reads each of your other authorized outputs and what they use it for. Use only supplied inputs. "
    "You have a token allowance for this. remaining_budget shows the action runs this iteration has used, is allowed and has left (an action run is one call to one role, or the race itself), how many iterations follow this one, the tokens left in this iteration and in total, the size of this call's own prompt (already spent), output_limit_tokens_this_call (everything you generate in this call counts toward it, and an answer that reaches it is cut off and cannot be used) and your_previous_calls (what your last calls in this role spent, how many attempts they took, and how many were cut off by the limit); a careful rationale is worth spending it on. "
    "The label and notes you give each output in _presentation should name and explain the change your rationale describes; write the notes as a short Markdown summary, because the map shows your full rationale (or feedback and requested changes) verbatim beneath it, so do not repeat it there. "
    "You may also include a top-level '_presentation' object (optional; the orchestrator labels any output you leave out) with one entry per entity you write: {'<entity_id>': {'label': '<=25 chars naming what this output is or what changed, e.g. Wider sensor array; never Updated', 'notes': 'one to three sentences describing what you produced and why, and the evidence it rests on'}}. "
    "The label and notes appear on the team's map for people reviewing the race; links to the artefact itself are added for you. public_contracts give the exact shape of what you must produce, the allowed range (minimum and maximum) or the only allowed options of every field, and a description of what each field does in the simulator; choose concrete values inside them.")

# Every model action describes what it produced, per output entity, under this reserved key. The controller
# strips it before contract validation and writes it into the scenario as the entity's label and notes.
PRESENTATION_KEY = "_presentation"
MAX_LABEL_CHARS = 25
GENERIC_LABELS = {"updated", "update", "done", "complete", "completed", "new", "ok", "changed", "revised", "v2", "output"}


def validate_presentation(output_ids: set[str], presentation: Any) -> dict[str, dict[str, str]]:
    """A meaningful map label (what changed, <=25 chars) and a descriptive note for every entity written."""
    if not isinstance(presentation, dict):
        raise ValueError(f"response must include {PRESENTATION_KEY}: {{entity_id: {{label, notes}}}} for every entity you write")
    missing = sorted(output_ids - set(presentation))
    if missing:
        raise ValueError(f"{PRESENTATION_KEY} is missing entries for {missing}")
    cleaned: dict[str, dict[str, str]] = {}
    for entity_id in sorted(output_ids):
        entry = presentation[entity_id]
        label = str(entry.get("label", "")).strip() if isinstance(entry, dict) else ""
        notes = str(entry.get("notes", "")).strip() if isinstance(entry, dict) else ""
        if not label or label.lower().strip(". ") in GENERIC_LABELS:
            raise ValueError(f"{PRESENTATION_KEY}.{entity_id}.label must say what this output is or what changed (e.g. 'Wider sensor array'), not a generic word like 'Updated'")
        if len(label) > MAX_LABEL_CHARS:
            # Cosmetic field: shorten at a word boundary rather than failing the whole race over it.
            cut = label[:MAX_LABEL_CHARS]
            label = (cut.rsplit(" ", 1)[0] if " " in cut and label[MAX_LABEL_CHARS] != " " else cut).rstrip(" .,-")
        if len(notes) < 20:
            raise ValueError(f"{PRESENTATION_KEY}.{entity_id}.notes must describe what you produced and why, in a sentence or two")
        cleaned[entity_id] = {"label": label, "notes": notes}
    return cleaned

def fallback_presentation(output: dict[str, dict[str, Any]], entities: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Orchestrator-written label and note for when the model never supplied a valid _presentation; the note says so, and the map still shows the agent's full rationale or feedback verbatim."""
    presentation: dict[str, dict[str, str]] = {}
    for entity_id in output:
        name = str((entities.get(entity_id) or {}).get("label", entity_id)).strip() or entity_id
        label = name if len(name) <= MAX_LABEL_CHARS else (name[:MAX_LABEL_CHARS].rsplit(" ", 1)[0] if " " in name[:MAX_LABEL_CHARS] else name[:MAX_LABEL_CHARS]).rstrip(" .,-")
        presentation[entity_id] = {"label": label, "notes": f"{name}. The model did not supply a valid label and summary, so the orchestrator wrote this one."}
    return presentation


def resolve_presentation(output: dict[str, dict[str, Any]], presentation: Any, entities: dict[str, Any]) -> dict[str, dict[str, str]]:
    """The model's label and note when valid, otherwise the orchestrator's own. Cosmetic, so never a reason to reject, retry or lose an agent's work."""
    try:
        return validate_presentation(set(output), presentation)
    except ValueError:
        return fallback_presentation(output, entities)


def full_notes(summary: str, payload: dict[str, Any]) -> str:
    """The map note carries the full reasoning (Markdown): the agent's short summary, then its rationale or feedback verbatim."""
    parts = [summary.strip()]
    if isinstance(payload.get("rationale"), str) and payload["rationale"].strip():
        parts.append("### Rationale\n\n" + payload["rationale"].strip())
    if isinstance(payload.get("feedback"), str) and payload["feedback"].strip():
        parts.append("### Feedback\n\n" + payload["feedback"].strip())
        changes = [str(item).strip() for item in payload.get("requested_changes", []) if str(item).strip()]
        if changes:
            parts.append("### Requested changes\n\n" + "\n".join(f"- {item}" for item in changes))
    return "\n\n".join(part for part in parts if part)


TELEMETRY_COLUMNS = ("progress", "error", "speed", "x", "y", "heading", "sensors", "line_lost")
TELEMETRY_FORMAT = (
    "Each trial's telemetry is column-packed to save tokens, losslessly: telemetry = {columns, rows}; "
    "row i is simulator step i (the step index is the row position); line_lost is 1 or 0; "
    "sensors is the list of sensor readings in the order of your sensor_positions."
)


def compact_telemetry(value: Any) -> tuple[Any, bool]:
    """Column-pack every per-step telemetry list found in a payload; returns (packed copy, found)."""
    if isinstance(value, dict):
        found = False
        packed: dict[str, Any] = {}
        for key, item in value.items():
            if key == "telemetry" and isinstance(item, list) and item and all(isinstance(row, dict) for row in item):
                packed[key] = {"columns": list(TELEMETRY_COLUMNS), "rows": [[int(row[c]) if c == "line_lost" else row[c] for c in TELEMETRY_COLUMNS] for row in item]}
                found = True
            else:
                packed[key], inner = compact_telemetry(item)
                found = found or inner
        return packed, found
    if isinstance(value, list):
        results = [compact_telemetry(item) for item in value]
        return [item for item, _ in results], any(flag for _, flag in results)
    return value, False


def objective_for_prompt(race: dict[str, Any]) -> dict[str, Any]:
    """Scoring facts every model action is told; generated from the frozen race config. The goal itself is in each action's notes."""
    objective = race.get("objective") or {}
    return {
        **({"goal": str(objective["statement"]).strip()} if objective.get("statement") else {}),
        "scoring": score_description(race["score"], race["simulator"]),
        "development_tracks": list(race["evaluation"]["development_tracks"]),
        "final_evaluation": "Raced once, after the last iteration, on unseen track(s) of a different shape. The final track, its shape and its seeds are never shown.",
    }


def notes_summary(notes: Any) -> Any:
    """An action's notes open with a one-paragraph description; the rest is that action's prompt."""
    return str(notes).split("\n\n", 1)[0].strip() if notes else notes


def downstream_dependents(package: MapPackage, action: ActionDefinition, targets: list[str]) -> dict[str, list[dict[str, Any]]]:
    """For each output this action may write: the other actions that read it, from the topology's `used by` edges."""
    result: dict[str, list[dict[str, Any]]] = {}
    for target in targets:
        consumers = []
        for other in package.actions.values():
            if other.id == action.id or target not in other.reads:
                continue
            consumers.append({
                "action": other.id,
                "does": (package.actions_data.get(other.id) or {}).get("label"),
                "actor": (package.actors.get(other.actor_id) or {}).get("label"),
                "cannot_run_without_it": target in other.required_inputs,
                "what_they_do": notes_summary((package.actions_data.get(other.id) or {}).get("notes")),
                "what_this_output_is_for": (package.entities.get(target) or {}).get("notes"),
            })
        if consumers:
            result[target] = consumers
    return result


def role_brief(package: MapPackage, action: ActionDefinition, targets: list[str]) -> dict[str, Any]:
    """Who this model action is, what its work involves, and what each output it may write is for; from the topology."""
    actor = package.actors.get(action.actor_id) or {}
    own = package.actions_data.get(action.id) or {}
    return {
        "you_are": actor.get("label"), "about_you": actor.get("notes"),
        "your_action": own.get("label"), "what_your_action_involves": notes_summary(own.get("notes")),
        "your_outputs": {t: {"label": (package.entities.get(t) or {}).get("label"), "purpose": (package.entities.get(t) or {}).get("notes")} for t in targets},
    }


def iteration_guidance(plan: dict[str, Any] | None, completes_when: list[str]) -> dict[str, Any] | None:
    """Where this iteration sits in the race and what happens if it does not finish."""
    if not plan:
        return None
    guidance = {
        **plan, "iteration_completes_when_present": completes_when,
        "if_incomplete": "An iteration that ends without every required output is not scored; its development race is not run. Later iterations still run.",
    }
    if plan["final_iteration"]:
        guidance["final_iteration_warning"] = "This is the final iteration. If it ends without a delivered design, the final unseen-track race is scored 0, and you will not see that score. Watch remaining_budget."
    return guidance


def project_design(entity: dict[str, Any]) -> dict[str, Any]:
    """Return only the fields validate_package accepts; entity metadata (notes, learning, approval) is dropped."""
    return {key: entity[key] for key in DESIGN_FIELDS if key in entity}


class PackageExecutor:
    """Production executor selected only by runtime bindings, never entrant name."""

    def __init__(self, package: MapPackage):
        self.package = package
        self.evidence_mode = mode_of(package.race)

    def _shown(self, value: Any) -> Any:
        """The form race evidence takes in a prompt (see evidence.py); stored payloads and artefacts are never changed."""
        return summarise_payload(value) if self.evidence_mode == "summary" else value

    def __call__(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any]) -> ActionResult:
        if action.runtime["kind"] == "model":
            return self._model(action, inputs, context)
        if action.runtime.get("component") == "robotrace.simulator":
            return self._simulator(action, inputs, context)
        raise RuntimeError(f"unsupported runtime for {action.id}")

    def _model(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any]) -> ActionResult:
        targets = list(action.runtime.get("output_contracts") or ([action.runtime["output_contract"]] if action.runtime.get("output_contract") else sorted(action.writes)))
        provider = self.package.race["model"]["provider"]
        if provider == "mock":
            output = self._mock_outputs(action, targets, inputs, int(context["iteration"]))
            released = self._apply_release(action, output, inputs)
            presentation = {**self._mock_presentation(output, int(context["iteration"])), **released}
            history = self._history(action, inputs, context, base_tokens=0)
            self._history_tokens = -(-len(json.dumps(history, separators=(",", ":"))) // CHARS_PER_TOKEN) if history else 0
            request_id = "mock-" + digest({"instructions": action.instructions, "inputs": inputs, "iteration": context["iteration"], **({"history": history} if history else {})})[:16]
            # Estimate from the packed form the real prompt uses (see compact_telemetry), at the same ~3 chars/token the history sizing assumes.
            packed_inputs, _ = compact_telemetry(self._shown(inputs))
            packed_history = compact_telemetry(history)[0] if history else {}
            input_tokens, output_tokens = max(1, (len(json.dumps(packed_inputs, separators=(",", ":"))) + len(json.dumps(packed_history, separators=(",", ":")))) // CHARS_PER_TOKEN), max(1, len(json.dumps(output)) // 4)
        elif provider == "openrouter":
            self._history_tokens = 0
            output, request_id, input_tokens, output_tokens, presentation = self._openrouter(action, targets, inputs, context)
            presentation = {**presentation, **self._apply_release(action, output, inputs)}
        else:
            raise RuntimeError(f"unsupported model provider: {provider}")
        unexpected = set(output) - set(targets) - ({action.runtime["release"]["release_entity"]} if action.runtime.get("release") else set())
        if unexpected or not output:
            raise ContractFailure(f"model returned invalid output entities: {sorted(unexpected)}", action.id, [f"invalid output entities: {sorted(unexpected)}"], input_tokens, output_tokens)
        for entity_id, payload in output.items():
            try:
                self.package.validate_payload(entity_id, payload)
            except Exception as error:
                raise ContractFailure(f"{entity_id} failed its contract: {error}", action.id, [str(error)], input_tokens, output_tokens) from error
        return ActionResult(output, {entity: presentation[entity]["label"] for entity in output}, {entity: full_notes(presentation[entity]["notes"], output[entity]) for entity in output}, {
            "provider": provider, "request_id": request_id,
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "history_tokens_estimate": getattr(self, "_history_tokens", 0),
            **(getattr(self, "_call_summary", None) or {}),
        })

    def _apply_release(self, action: ActionDefinition, output: dict[str, dict[str, Any]], inputs: dict[str, dict[str, Any]]) -> dict[str, dict[str, str]]:
        """An agent's decision releases a recorded candidate: when its required decision field says approve, the orchestrator writes the
        release entity as an unchanged copy of the candidate it reviewed. The agent never has to re-emit the build, so approving costs
        it no extra output and the approved build cannot differ from the one reviewed. Returns the presentation for what it wrote."""
        release = action.runtime.get("release")
        if not release:
            return {}
        decision = output.get(release["decision_entity"], {}).get(release["field"])
        candidate = inputs.get(release["from_entity"])
        if decision != release["approve_value"] or not candidate:
            return {}
        entity = release["release_entity"]
        output[entity] = {**project_design(candidate), "approval": {"decision": "ship", "candidate_id": digest(project_design(candidate))[:16]}}
        for key in ("rationale", "learning", "notes"):  # keep the candidate's own reasoning if the release contract asks for it
            if key in (self.package.contract(entity) or {}).get("required", []) and key in candidate:
                output[entity][key] = candidate[key]
        return fallback_presentation({entity: output[entity]}, self.package.entities)

    def _history(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any], base_tokens: int) -> dict[str, Any] | None:
        """This actor's history pack (see history.py), sized to what the token budget leaves for this call; None when the race has no history setting."""
        settings = self.package.race.get("history")
        if not settings:
            return None
        model_actions = max(1, sum(1 for other in self.package.actions.values() if other.runtime.get("kind") == "model"))
        budget = context["budget"]
        share = min(int(budget["iteration_tokens_remaining"]), int(budget["total_tokens_remaining"])) // model_actions
        cap = max(0, share - int(self.package.race["model"]["max_output_tokens"]) - base_tokens - SYSTEM_PROMPT_ALLOWANCE)
        return build_history(self.package.root, reads=action.reads, writes=action.writes, iteration=int(context["iteration"]), inputs=inputs, settings={**settings, "evidence": self.evidence_mode}, pack=compact_telemetry, pack_cap=cap)

    def _mock_presentation(self, output: dict[str, dict[str, Any]], iteration: int) -> dict[str, dict[str, str]]:
        """Deterministic, specific labels and notes so mock races exercise the same path as real ones."""
        presentation: dict[str, dict[str, str]] = {}
        for entity_id, payload in output.items():
            name = str((self.package.entities.get(entity_id) or {}).get("label", entity_id))
            label = name[:25]
            detail = next((str(payload[key]) for key in ("intent", "notes", "agreement", "learning", "feedback") if isinstance(payload.get(key), str)), "")
            presentation[entity_id] = {"label": label, "notes": f"{name}, iteration {iteration} (mock model). {detail}".strip()}
        return presentation

    def _mock_outputs(self, action: ActionDefinition, targets: list[str], inputs: dict[str, dict[str, Any]], iteration: int) -> dict[str, dict[str, Any]]:
        design = next((value for value in inputs.values() if "geometry" in value and "controller" in value), _design(iteration))
        geometry = next((value["geometry"] for value in inputs.values() if "geometry" in value), design["geometry"])
        approval_flow = any("approval" in set((self.package.contract(target) or {}).get("required", [])) for target in targets)
        outputs: dict[str, dict[str, Any]] = {}
        for target in targets:
            schema = self.package.contract(target) or {}
            required = set(schema.get("required", []))
            if {"geometry", "controller", "observation_request"}.issubset(required):
                outputs[target] = {
                    "geometry": geometry,
                    "controller": design["controller"],
                    "observation_request": design["observation_request"],
                    **({"rationale": "Deterministic mock rationale."} if "rationale" in required else {}),
                    **({"notes": "Deterministic mock integration."} if "notes" in required else {}),
                    **({"learning": "Deterministic mock learning state."} if "learning" in required else {}),
                    **({"approval": {"decision": "ship", "candidate_id": "mock-candidate"}} if "approval" in required else {}),
                }
            elif "geometry" in required:
                outputs[target] = {
                    "geometry": geometry,
                    **({"rationale": "Deterministic mock rationale."} if "rationale" in required else {}),
                    **({"intent": "Improve robust line following."} if "intent" in required else {}),
                    **({"feedback_request": design["observation_request"]} if "feedback_request" in required else {}),
                    **({"learning": "Deterministic mock geometry learning."} if "learning" in required else {}),
                }
            elif "agreement" in required:
                outputs[target] = {"agreement": "Use explicit handoffs and addressed evidence.", "revision": iteration}
            elif "learning" in required:
                outputs[target] = {"learning": "Deterministic private learning state.", "revision": iteration}
            elif "entries" in required:
                outputs[target] = {"entries": [{"kind": "mock", "iteration": iteration}]}
            elif "feedback" in required:
                if "decision" in required:  # decision-gated evaluator: the mock always approves, so the loop ends
                    outputs[target] = {"feedback": "Use addressed race evidence in the next revision.", "requested_changes": [], "decision": "approve"}
                elif not approval_flow and any(key.endswith("R2B") for key in inputs):
                    outputs[target] = {"feedback": "Use addressed race evidence in the next revision.", "requested_changes": []}
            else:
                outputs[target] = {key: "mock" for key in required}
        return outputs

    def _openrouter(self, action: ActionDefinition, targets: list[str], inputs: dict[str, dict[str, Any]], context: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], str, int, int, dict[str, dict[str, str]]]:
        key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not key:
            raise RuntimeError("OPENROUTER_API_KEY is not set")
        config = self.package.race["model"]
        contracts = {target: self.package.contract(target) or {"type": "object"} for target in targets}
        public_contracts = {entity_id: self.package.contract(entity_id) for entity_id in sorted(action.reads - set(inputs)) if (self.package.entities.get(entity_id) or {}).get("system_boundary") == "public" and self.package.contract(entity_id)}
        prompt_inputs, has_telemetry = compact_telemetry(self._shown(inputs))
        base_prompt = {"instructions": action.instructions, "authorized_inputs": prompt_inputs, "authorized_output_contracts": contracts, "public_contracts": public_contracts, "remaining_budget": context["budget"], "iteration": context["iteration"]}
        if not getattr(self.package, "bounds_in_contract", False):  # legacy packages: limits live in race.yaml, not in the contract
            base_prompt["race_constraints"] = self.package.race.get("design_bounds", {})
        required = [t for t in action.runtime.get("required_outputs", []) if t in targets]
        base_prompt["your_role"] = role_brief(self.package, action, targets)
        base_prompt["required_outputs"] = required
        # Models often drop the reserved key, so show its exact shape in the user message too (not only the system prompt).
        base_prompt["response_shape"] = {"<entity_id>": "the entity's payload, matching its contract", PRESENTATION_KEY: {t: {"label": "<=25 chars, what this output is or what changed", "notes": "1-3 sentences: what you produced and the evidence it rests on"} for t in targets}, "key_order": "Write each entity's keys in the order its contract lists them: reasoning fields (rationale, intent) come first, so you have worked out the limits before you write the numbers.", "reminder": f"{PRESENTATION_KEY} is optional: if you leave it out the orchestrator writes the map label and note, and nothing is rejected."}
        dependents = downstream_dependents(self.package, action, targets)
        if dependents:
            base_prompt["downstream_dependents"] = dependents
        guidance = iteration_guidance(context.get("iteration_plan"), sorted(self.package.workflow["iteration_complete_when"]["entities_present"]))
        if guidance:
            base_prompt["iteration_plan"] = guidance
        if context.get("previous_iteration"):
            base_prompt["previous_iteration_incomplete"] = context["previous_iteration"]
        base_prompt["objective"] = objective_for_prompt(self.package.race)
        history = self._history(action, inputs, context, base_tokens=-(-len(json.dumps(base_prompt, sort_keys=True, separators=(",", ":"))) // CHARS_PER_TOKEN))
        if history:
            base_prompt["history"], history_has_telemetry = compact_telemetry(history)
            self._history_tokens = -(-len(json.dumps(base_prompt["history"], sort_keys=True, separators=(",", ":"))) // CHARS_PER_TOKEN)
            has_telemetry = has_telemetry or history_has_telemetry
        if has_telemetry:
            base_prompt["telemetry_format"] = TELEMETRY_FORMAT
        # This call's own input size (estimate, ~3 chars/token): the prompt is spent before the model writes a word.
        base_prompt["remaining_budget"] = {**base_prompt["remaining_budget"], "this_call_input_tokens_estimate": 0, "output_limit_tokens_this_call": 0}
        size = -(-(len(SYSTEM_PROMPT) + len(json.dumps(base_prompt, separators=(",", ":")))) // CHARS_PER_TOKEN)
        base_prompt["remaining_budget"]["this_call_input_tokens_estimate"] = size
        # The most this call can generate: the race's per-call cap, or less when the iteration or total budget is the tighter limit.
        base_prompt["remaining_budget"]["output_limit_tokens_this_call"] = max(0, min(int(config["max_output_tokens"]), min(int(context["budget"]["iteration_tokens_remaining"]), int(context["budget"]["total_tokens_remaining"])) - size))
        error = ""
        errors: list[str] = []
        spent_in = spent_out = 0  # every attempt is paid for, including the ones the contract rejects
        cut_off_attempts = 0
        self._call_summary = {}
        attempts = int(action.runtime.get("repair_attempts", 0)) + 1
        for _ in range(attempts):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": json.dumps({**base_prompt, "previous_validation_error": error}, separators=(",", ":"))}]  # no sort_keys: the model copies the key order it is shown, so contract order (rationale before numbers) must survive
            available_tokens = min(
                int(context["budget"]["iteration_tokens_remaining"]),
                int(context["budget"]["total_tokens_remaining"]),
            ) - spent_in - spent_out
            prompt_estimate = -(-sum(len(m["content"]) for m in messages) // CHARS_PER_TOKEN)
            room = available_tokens - prompt_estimate  # what is left for the model's answer once the prompt is paid for
            if room < MIN_OUTPUT_TOKENS:
                raise BudgetExhausted(f"{action.id} needs about {prompt_estimate} input tokens plus at least {MIN_OUTPUT_TOKENS} to answer, but {max(0, available_tokens)} remain", getattr(action, "id", None), spent_in, spent_out)
            body = {"model": config["id"], "messages": messages, "temperature": config.get("temperature", 0), "max_tokens": min(config["max_output_tokens"], room), "response_format": {"type": "json_object"}}
            request = Request(config.get("base_url", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=config.get("timeout_seconds", 120)) as response:
                response_data = json.loads(response.read())
            usage = response_data.get("usage", {})
            spent_in += int(usage.get("prompt_tokens", 0))
            spent_out += int(usage.get("completion_tokens", 0))
            generated = int(usage.get("completion_tokens", 0))
            finish_reason = ((response_data.get("choices") or [{}])[0] or {}).get("finish_reason")
            # An answer that ran into the output limit is unreadable JSON; say so, rather than showing the model a bare parse error it
            # cannot act on (and would repeat). max_tokens is the limit this call actually had: the cap, or less if the budget was tighter.
            cut_off = finish_reason == "length" or generated >= int(body["max_tokens"])
            content = ""
            try:
                content = response_data["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0]
                output = json.loads(content)
                presentation = output.pop(PRESENTATION_KEY, None) if isinstance(output, dict) else None
                if isinstance(output, dict):
                    presentation = self._tidy_shape(output, targets, presentation)
                if not isinstance(output, dict) or not output:
                    raise ValueError("response must be a JSON object keyed by the entity IDs you write")
                stray = sorted(set(output) - set(targets))
                if stray:
                    raise ValueError(f"unknown top-level keys {stray}; the only keys allowed at the top level are your authorized output entity IDs {sorted(targets)} and the optional {PRESENTATION_KEY}")
                missing = [t for t in required if t not in output]
                if missing:
                    raise ValueError(f"required outputs are missing: {missing}. You must produce every entity in required_outputs, each matching its contract.")
                for entity_id, payload in output.items():
                    self.package.validate_payload(entity_id, payload)
                    if isinstance(payload, dict) and isinstance(payload.get("geometry"), dict):
                        validate_geometry(payload["geometry"], self.package.race["design_bounds"])
                        if isinstance(payload.get("controller"), dict):  # an out-of-range controller would otherwise only surface as a 0-scoring invalid design
                            validate_controller(payload["controller"], len(payload["geometry"]["sensor_positions"]), self.package.race["design_bounds"])
                presentation = resolve_presentation(output, presentation, self.package.entities)
                self._call_summary = {"attempts": _ + 1, "attempts_cut_off": cut_off_attempts}
                return output, response_data.get("id", "openrouter-unknown"), spent_in, spent_out, presentation
            except Exception as validation_error:
                error = str(validation_error)
                if cut_off:
                    cut_off_attempts += 1
                    error = (f"Your previous answer was {CUT_OFF_MARKER} ({int(body['max_tokens']):,} tokens; {generated:,} generated) before the JSON was complete, "
                             f"so none of it could be used. The limit covers everything you generate in one call. Answer again so that the complete JSON fits within it. (Parser: {validation_error})")
                errors.append(error)
                self._record_rejected_attempt(action, context, _ + 1, content, error, {"finish_reason": finish_reason, "completion_tokens": generated, "max_tokens": int(body["max_tokens"]), "cut_off": cut_off})
        raise ContractFailure(f"model output failed contract after {attempts} attempts: {error}", getattr(action, "id", None), errors, spent_in, spent_out)

    def _tidy_shape(self, output: dict[str, Any], targets: Any, presentation: Any) -> Any:
        """Put misplaced fields where they belong instead of rejecting the output (a retry resends the whole prompt). Moves only placement,
        never content: a nested '_presentation' becomes the top-level one, and a stray top-level key that is a field of the single entity
        being written moves into that entity. Anything else is left for the contract to reject, with the offending key named."""
        for payload in output.values():
            if isinstance(payload, dict) and PRESENTATION_KEY in payload:
                nested = payload.pop(PRESENTATION_KEY)
                if presentation is None:
                    presentation = nested
        entities = [key for key in output if key in targets]
        if len(entities) == 1 and isinstance(output[entities[0]], dict):
            fields = (self.package.contract(entities[0]) or {}).get("properties", {})
            for key in [key for key in output if key not in targets]:
                if key in fields and key not in output[entities[0]]:
                    output[entities[0]][key] = output.pop(key)
        return presentation

    def _record_rejected_attempt(self, action: ActionDefinition, context: dict[str, Any], attempt: int, raw_output: str, error: str, detail: dict[str, Any] | None = None) -> None:
        """Keep every rejected model output so a failed contract can be diagnosed afterwards (best effort)."""
        try:
            directory = self.package.root / f"iteration-{int(context['iteration'])}" / "rejected-attempts"
            directory.mkdir(parents=True, exist_ok=True)
            record = {"action": getattr(action, "id", None), "attempt": attempt, "error": error, **(detail or {}), "raw_output": raw_output}
            (directory / f"{record['action']}-attempt-{attempt}.json").write_text(json.dumps(record, indent=2))
        except Exception:
            pass

    def _simulator(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any]) -> ActionResult:
        design = project_design(next(value for value in inputs.values() if "geometry" in value and "controller" in value))
        evaluation = self.package.race["evaluation"]
        root = Path(__file__).resolve().parents[1]
        tracks = [json.loads((root / "tracks" / "development" / f"{name}.json").read_text()) if name != "oval" else json.loads((root / "tracks/anchor/oval.json").read_text()) for name in evaluation["development_tracks"]]
        trials = keep_telemetry([run_trial(design, track, seed, self.package.race) for track in tracks for seed in evaluation["seeds"]], evaluation.get("recorded_seeds_per_track"))
        score = round(sum(float(trial["score"]) for trial in trials) / len(trials), 4)
        invalid = [trial for trial in trials if trial.get("termination_reason") == "invalid_design"]
        invalid_note = {"invalid_trials": len(invalid), "total_trials": len(trials), "first_error": invalid[0].get("error")} if invalid else {}
        evidence: dict[str, Any] = {"summary": "Development simulator evidence", "score": score, "trials": trials}
        if invalid_note:
            evidence["error"] = str(invalid_note["first_error"])
        writes: dict[str, dict[str, Any]] = {}
        for entity in action.writes:
            properties = (self.package.contract(entity) or {}).get("properties")
            writes[entity] = {key: value for key, value in evidence.items() if key in properties} if properties else dict(evidence)
        per_trial = "; ".join(f"{trial['track']}-{trial['seed']}: {float(trial['score']):.1f} ({trial.get('termination_reason')})" for trial in trials)
        sim_notes = f"Development race of the integrated design on {len(trials)} trial(s); mean score {score:.2f}. Per trial — {per_trial}."
        return ActionResult(writes, {entity: f"Score {score:.2f}" for entity in writes}, {entity: sim_notes for entity in writes}, {"component": "robotrace.simulator", "simulator_version": ADAPTER_VERSION, **invalid_note, "trial_ids": [trial.get("run_id") for trial in trials]})
