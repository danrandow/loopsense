from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from simulator.adapter import ADAPTER_VERSION, run_trial
from simulator.adapter.headless import score_description

from .controller import ActionResult
from .history import CHARS_PER_TOKEN, build_history
from .io import digest
from .map_package import ActionDefinition, MapPackage
from .validators import validate_geometry


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
SYSTEM_PROMPT = "Return one JSON object keyed by the entity IDs you update. Every value must match that entity's supplied contract. You are one member of a small team that shares a single score; the team only does well if every member does their own job fully and well. your_role says who you are and what each of your outputs is for. Every entity in required_outputs MUST be present, or the team cannot be scored. Your other authorized outputs are how you help your teammates: downstream_dependents shows who reads each one and what they use it for. Feedback outputs exist so your teammate can do better next time; fill them with specific, concrete, evidence-based content (cite numbers from the telemetry or from your teammate's work, and name the exact values you want changed), never generic advice. Do your best work: diagnose from the evidence you are given, change something that addresses what you found, and say why. Where an output has a rationale field, write it first, before the other fields: think it through there (what the evidence shows, what you decided to change and why, what result you expect). You have a token allowance for this (see remaining_budget, which also shows how many teammates' model calls are still to run this iteration, how many iterations follow this one, and the size of this call's own prompt, already spent); a careful rationale is worth spending it on. The label and notes you give each output in _presentation should then name and explain the change your rationale describes; write the notes as a short Markdown summary, because the map shows your full rationale (or feedback and requested changes) verbatim beneath it, so do not repeat it there. Use only supplied inputs. Also include a top-level '_presentation' object with one entry per entity you write: {'<entity_id>': {'label': '<=25 chars naming what this output is or what changed, e.g. Wider sensor array; never Updated', 'notes': 'one to three sentences describing what you produced and why, and the evidence it rests on'}}. The label and notes appear on the team's map for people reviewing the race; links to the artefact itself are added for you. public_contracts give the exact shape of what you must produce; race_constraints give allowed ranges for numeric fields as [min, max] and, where a field is a list of options (e.g. sensor_sizes), the only allowed values; choose concrete values inside them."

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
            raise ValueError(f"{PRESENTATION_KEY}.{entity_id}.label is {len(label)} characters; the limit is {MAX_LABEL_CHARS}")
        if len(notes) < 20:
            raise ValueError(f"{PRESENTATION_KEY}.{entity_id}.notes must describe what you produced and why, in a sentence or two")
        cleaned[entity_id] = {"label": label, "notes": notes}
    return cleaned

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


def objective_for_prompt(race: dict[str, Any]) -> dict[str, Any] | None:
    """What every model action is told about the goal; generated from the frozen race config."""
    objective = race.get("objective")
    if not objective:
        return None
    return {
        "goal": str(objective["statement"]).strip(),
        "scoring": score_description(race["score"], race["simulator"]),
        "development_tracks": list(race["evaluation"]["development_tracks"]),
        "final_evaluation": "Raced once, after the last iteration, on unseen track(s) of a different shape. The final track, its shape and its seeds are never shown.",
    }


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
                "what_they_do": (package.actions_data.get(other.id) or {}).get("notes"),
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
        "your_action": own.get("label"), "what_your_action_involves": own.get("notes"),
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
            presentation = self._mock_presentation(output, int(context["iteration"]))
            history = self._history(action, inputs, context, base_tokens=0)
            self._history_tokens = -(-len(json.dumps(history, separators=(",", ":"))) // CHARS_PER_TOKEN) if history else 0
            request_id = "mock-" + digest({"instructions": action.instructions, "inputs": inputs, "iteration": context["iteration"], **({"history": history} if history else {})})[:16]
            # Estimate from the packed form the real prompt uses (see compact_telemetry), at the same ~3 chars/token the history sizing assumes.
            packed_inputs, _ = compact_telemetry(inputs)
            packed_history = compact_telemetry(history)[0] if history else {}
            input_tokens, output_tokens = max(1, (len(json.dumps(packed_inputs, separators=(",", ":"))) + len(json.dumps(packed_history, separators=(",", ":")))) // CHARS_PER_TOKEN), max(1, len(json.dumps(output)) // 4)
        elif provider == "openrouter":
            self._history_tokens = 0
            output, request_id, input_tokens, output_tokens, presentation = self._openrouter(action, targets, inputs, context)
        else:
            raise RuntimeError(f"unsupported model provider: {provider}")
        unexpected = set(output) - set(targets)
        if unexpected or not output:
            raise RuntimeError(f"model returned invalid output entities: {sorted(unexpected)}")
        for entity_id, payload in output.items():
            self.package.validate_payload(entity_id, payload)
        return ActionResult(output, {entity: presentation[entity]["label"] for entity in output}, {entity: full_notes(presentation[entity]["notes"], output[entity]) for entity in output}, {
            "provider": provider, "request_id": request_id,
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "history_tokens_estimate": getattr(self, "_history_tokens", 0),
        })

    def _history(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any], base_tokens: int) -> dict[str, Any] | None:
        """This actor's history pack (see history.py), sized to what the token budget leaves for this call; None when the race has no history setting."""
        settings = self.package.race.get("history")
        if not settings:
            return None
        model_actions = max(1, sum(1 for other in self.package.actions.values() if other.runtime.get("kind") == "model"))
        budget = context["budget"]
        share = min(int(budget["iteration_tokens_remaining"]), int(budget["total_tokens_remaining"])) // model_actions
        cap = max(0, share - int(self.package.race["model"]["max_output_tokens"]) - base_tokens - SYSTEM_PROMPT_ALLOWANCE)
        return build_history(self.package.root, reads=action.reads, writes=action.writes, iteration=int(context["iteration"]), inputs=inputs, settings=settings, pack=compact_telemetry, pack_cap=cap)

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
                if not approval_flow and any(key.endswith("R2B") for key in inputs):
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
        prompt_inputs, has_telemetry = compact_telemetry(inputs)
        base_prompt = {"instructions": action.instructions, "authorized_inputs": prompt_inputs, "authorized_output_contracts": contracts, "public_contracts": public_contracts, "race_constraints": self.package.race.get("design_bounds", {}), "remaining_budget": context["budget"], "iteration": context["iteration"]}
        required = [t for t in action.runtime.get("required_outputs", []) if t in targets]
        base_prompt["your_role"] = role_brief(self.package, action, targets)
        base_prompt["required_outputs"] = required
        dependents = downstream_dependents(self.package, action, targets)
        if dependents:
            base_prompt["downstream_dependents"] = dependents
        guidance = iteration_guidance(context.get("iteration_plan"), sorted(self.package.workflow["iteration_complete_when"]["entities_present"]))
        if guidance:
            base_prompt["iteration_plan"] = guidance
        if context.get("previous_iteration"):
            base_prompt["previous_iteration_incomplete"] = context["previous_iteration"]
        objective = objective_for_prompt(self.package.race)
        if objective:
            base_prompt["objective"] = objective
        history = self._history(action, inputs, context, base_tokens=-(-len(json.dumps(base_prompt, sort_keys=True, separators=(",", ":"))) // CHARS_PER_TOKEN))
        if history:
            base_prompt["history"], history_has_telemetry = compact_telemetry(history)
            self._history_tokens = -(-len(json.dumps(base_prompt["history"], sort_keys=True, separators=(",", ":"))) // CHARS_PER_TOKEN)
            has_telemetry = has_telemetry or history_has_telemetry
        if has_telemetry:
            base_prompt["telemetry_format"] = TELEMETRY_FORMAT
        # This call's own input size (estimate, ~3 chars/token): the prompt is spent before the model writes a word.
        base_prompt["remaining_budget"] = {**base_prompt["remaining_budget"], "this_call_input_tokens_estimate": 0}
        size = -(-(len(SYSTEM_PROMPT) + len(json.dumps(base_prompt, sort_keys=True, separators=(",", ":")))) // CHARS_PER_TOKEN)
        base_prompt["remaining_budget"]["this_call_input_tokens_estimate"] = size
        error = ""
        attempts = int(action.runtime.get("repair_attempts", 0)) + 1
        for _ in range(attempts):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": json.dumps({**base_prompt, "previous_validation_error": error}, sort_keys=True, separators=(",", ":"))}]
            available_tokens = min(
                int(context["budget"]["iteration_tokens_remaining"]),
                int(context["budget"]["total_tokens_remaining"]),
            )
            body = {"model": config["id"], "messages": messages, "temperature": config.get("temperature", 0), "max_tokens": min(config["max_output_tokens"], available_tokens), "response_format": {"type": "json_object"}}
            request = Request(config.get("base_url", "https://openrouter.ai/api/v1").rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
            with urlopen(request, timeout=config.get("timeout_seconds", 120)) as response:
                response_data = json.loads(response.read())
            content = ""
            try:
                content = response_data["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = content.split("\n", 1)[1].rsplit("```", 1)[0]
                output = json.loads(content)
                presentation = output.pop(PRESENTATION_KEY, None) if isinstance(output, dict) else None
                if not isinstance(output, dict) or not output or set(output) - set(targets):
                    raise ValueError("response must contain one or more authorized output entity keys")
                missing = [t for t in required if t not in output]
                if missing:
                    raise ValueError(f"required outputs are missing: {missing}. You must produce every entity in required_outputs, each matching its contract.")
                presentation = validate_presentation(set(output), presentation)
                for entity_id, payload in output.items():
                    self.package.validate_payload(entity_id, payload)
                    if isinstance(payload, dict) and isinstance(payload.get("geometry"), dict):
                        validate_geometry(payload["geometry"], self.package.race["design_bounds"])
                usage = response_data.get("usage", {})
                return output, response_data.get("id", "openrouter-unknown"), int(usage.get("prompt_tokens", 0)), int(usage.get("completion_tokens", 0)), presentation
            except Exception as validation_error:
                error = str(validation_error)
                self._record_rejected_attempt(action, context, _ + 1, content, error)
        raise RuntimeError(f"model output failed contract after {attempts} attempts: {error}")

    def _record_rejected_attempt(self, action: ActionDefinition, context: dict[str, Any], attempt: int, raw_output: str, error: str) -> None:
        """Keep every rejected model output so a failed contract can be diagnosed afterwards (best effort)."""
        try:
            directory = self.package.root / f"iteration-{int(context['iteration'])}" / "rejected-attempts"
            directory.mkdir(parents=True, exist_ok=True)
            record = {"action": getattr(action, "id", None), "attempt": attempt, "error": error, "raw_output": raw_output}
            (directory / f"{record['action']}-attempt-{attempt}.json").write_text(json.dumps(record, indent=2))
        except Exception:
            pass

    def _simulator(self, action: ActionDefinition, inputs: dict[str, dict[str, Any]], context: dict[str, Any]) -> ActionResult:
        design = project_design(next(value for value in inputs.values() if "geometry" in value and "controller" in value))
        evaluation = self.package.race["evaluation"]
        root = Path(__file__).resolve().parents[1]
        tracks = [json.loads((root / "tracks" / "development" / f"{name}.json").read_text()) if name != "oval" else json.loads((root / "tracks/anchor/oval.json").read_text()) for name in evaluation["development_tracks"]]
        trials = [run_trial(design, track, seed, self.package.race) for track in tracks for seed in evaluation["seeds"]]
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
