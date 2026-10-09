from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import canonical
from .io import read_yaml, safe_child
from .validators import design_bounds_from_contract

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - source checkouts can run without installation
    Draft202012Validator = None


class PackageValidationError(ValueError):
    pass


RUNTIME_KINDS = {"model", "component"}
COMPONENTS = {"robotrace.simulator"}
REENTRY = {"never", "on_new_inputs", "once_per_iteration"}
SCENARIO_KEYS = {"map", "dimensions", "overrides", "measurements"}
OVERRIDE_FIELDS = {
    "actors": {"id", "label", "notes"},
    "actions": {"id", "label", "notes"},
    "entities": {"id", "label", "notes"},
    "edges": {"id", "notes", "confidence"},
}


def _object(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PackageValidationError(f"{name} must be an object")
    return value


@dataclass(frozen=True)
class ActionDefinition:
    id: str
    actor_id: str
    reads: frozenset[str]
    writes: frozenset[str]
    runtime: dict[str, Any]
    instructions: str | None
    required_inputs: frozenset[str]
    trigger_inputs: frozenset[str]


class MapPackage:
    """A validated race-specific team definition derived from its topology."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.base_path = safe_child(self.root, "base.yaml")
        self.workflow_path = safe_child(self.root, "config", "workflow.yaml")
        self.race_path = safe_child(self.root, "config", "race.yaml")
        self.topology = _object(read_yaml(self.base_path), "base.yaml")
        self.workflow = _object(read_yaml(self.workflow_path), "workflow.yaml")
        self.race = _object(read_yaml(self.race_path), "race.yaml")
        self.actors = self._indexed("actors")
        self.actions_data = self._indexed("actions")
        self.entities = self._indexed("entities")
        self.edges = self._indexed("edges")
        self.actions: dict[str, ActionDefinition] = {}
        # True when the design limits come from the design contract (the single source) rather than race.yaml.
        self.bounds_in_contract = False

    def _indexed(self, section: str) -> dict[str, dict[str, Any]]:
        values = self.topology.get(section)
        if not isinstance(values, list):
            raise PackageValidationError(f"base.yaml {section} must be a list")
        result: dict[str, dict[str, Any]] = {}
        for value in values:
            item = _object(value, section)
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                raise PackageValidationError(f"{section} item has no id")
            if item_id in result:
                raise PackageValidationError(f"duplicate {section} id: {item_id}")
            result[item_id] = item
        return result

    def path(self, *parts: str) -> Path:
        return safe_child(self.root, *parts)

    def validate(self) -> "MapPackage":
        allowed = {"base.yaml"}
        malformed: list[str] = []
        for path in self.root.glob("*.yaml"):
            if path.name == "base.yaml" or re.fullmatch(r"scenario-iteration-\d+\.yaml", path.name):
                allowed.add(path.name)
            else:
                malformed.append(path.name)
        if malformed:
            raise PackageValidationError(f"root YAML is not a map: {sorted(malformed)}")
        try:
            for map_file in [self.root / "base.yaml", *sorted(self.root.glob("scenario-iteration-*.yaml"))]:
                canonical.validate_map_file(map_file)
            map_file = self.root / "base.yaml"
            canonical.check_element_keys(self.topology)
        except ValueError as error:
            raise PackageValidationError(f"canonical Randow Maps validation failed for {map_file.name}: {error}") from error
        map_data = _object(self.topology.get("map"), "base.yaml map")
        if map_data.get("schema") != "v0.2" or map_data.get("is_moo") is not True:
            raise PackageValidationError("base.yaml must be a v0.2 Moving Parts topology")
        axes = map_data.get("dimension_axes")
        if not isinstance(axes, list) or "time_horizon" not in axes or "iteration" not in axes:
            raise PackageValidationError("topology dimensions must include time_horizon and iteration")

        all_ids: list[str] = [*self.actors, *self.actions_data, *self.entities, *self.edges]
        if len(all_ids) != len(set(all_ids)):
            raise PackageValidationError("topology element ids must be globally unique")

        actor_use: dict[str, int] = {actor: 0 for actor in self.actors}
        reads: dict[str, set[str]] = {action: set() for action in self.actions_data}
        writes: dict[str, set[str]] = {action: set() for action in self.actions_data}
        return_pairs: set[tuple[str, str]] = set()
        return_parts: dict[str, list[dict[str, Any]]] = {}
        for action_id, action in self.actions_data.items():
            actor = action.get("actor")
            if actor not in actor_use:
                raise PackageValidationError(f"{action_id} references unknown actor {actor}")
            actor_use[actor] += 1
        if any(count != 1 for count in actor_use.values()):
            raise PackageValidationError("every actor must own exactly one action")
        for edge_id, edge in self.edges.items():
            edge_type, source, target = edge.get("type"), edge.get("from"), edge.get("to")
            if edge_type == "used by" and source in self.entities and target in self.actions_data:
                reads[target].add(source)
            elif edge_type == "generates" and source in self.actions_data and target in self.entities:
                writes[source].add(target)
            else:
                raise PackageValidationError(f"invalid topology edge {edge_id}")
            if edge.get("direction") == "return":
                entity = source if source in self.entities else target
                return_parts.setdefault(entity, []).append(edge)
        for entity, parts in return_parts.items():
            if len(parts) != 2 or {part["type"] for part in parts} != {"generates", "used by"}:
                raise PackageValidationError(f"return entity {entity} must have one generates and one used-by edge")
            generated = next(part for part in parts if part["type"] == "generates")
            consumed = next(part for part in parts if part["type"] == "used by")
            pair = (generated["from"], consumed["to"])
            if pair in return_pairs:
                raise PackageValidationError(f"duplicate return path {pair[0]} -> {pair[1]}")
            return_pairs.add(pair)

        for action_id, action in self.actions_data.items():
            runtime_path = self.path("actions", action_id, "runtime.yaml")
            if not runtime_path.is_file():
                raise PackageValidationError(f"missing runtime binding for {action_id}")
            runtime = _object(read_yaml(runtime_path), f"{action_id} runtime")
            if set(runtime) - {"kind", "component", "output_contract", "output_contracts", "provider", "repair_attempts", "required_outputs"}:
                raise PackageValidationError(f"unsupported runtime fields for {action_id}")
            kind = runtime.get("kind")
            if kind not in RUNTIME_KINDS:
                raise PackageValidationError(f"unsupported runtime kind for {action_id}: {kind}")
            instructions = None
            if kind == "model":
                # The prompt lives in the topology: the action's notes. A legacy package may still carry instructions.md.
                instructions_path = self.path("actions", action_id, "instructions.md")
                if instructions_path.is_file():
                    instructions = instructions_path.read_text(encoding="utf-8")
                else:
                    instructions = str(action.get("notes") or "")
                if not instructions.strip():
                    raise PackageValidationError(f"empty model instructions for {action_id}")
            elif runtime.get("component") not in COMPONENTS:
                raise PackageValidationError(f"unsupported component for {action_id}")
            output_contract = runtime.get("output_contract")
            if output_contract is not None and output_contract not in writes[action_id]:
                raise PackageValidationError(f"{action_id} output_contract is not a topology-authorized write")
            required_outputs = runtime.get("required_outputs")
            if required_outputs is not None and (not isinstance(required_outputs, list) or not set(required_outputs) <= writes[action_id]):
                raise PackageValidationError(f"{action_id} required_outputs must be a list of topology-authorized writes")
            output_contracts = runtime.get("output_contracts")
            if output_contracts is not None:
                if not isinstance(output_contracts, list) or not output_contracts:
                    raise PackageValidationError(f"{action_id} output_contracts must be a non-empty list")
                unknown_outputs = set(output_contracts) - writes[action_id]
                if unknown_outputs:
                    raise PackageValidationError(
                        f"{action_id} output_contracts are not topology-authorized writes: {sorted(unknown_outputs)}"
                    )
            required_inputs = set(self.workflow.get("required_inputs", {}).get(action_id, reads[action_id]))
            if not required_inputs.issubset(reads[action_id]):
                raise PackageValidationError(f"{action_id} required_inputs must be topology-authorized reads")
            self.actions[action_id] = ActionDefinition(
                action_id, action["actor"], frozenset(reads[action_id]),
                frozenset(writes[action_id]), runtime, instructions, frozenset(required_inputs),
                frozenset(reads[action_id] - writes[action_id]),
            )

        for entity_id in self.entities:
            self.contract(entity_id)

        self._validate_workflow()
        self._validate_race()
        self._derive_design_bounds()
        if self.race.get("race_id") != "template":
            entrant = self.race.get("entrant")
            if self.root.name != f"{self.race['race_id']}-{entrant}":
                raise PackageValidationError("package directory identity does not match race metadata")
            if map_data.get("id") != self.root.name:
                raise PackageValidationError("topology identity does not match entrant metadata")
        self._validate_reachability()
        scenarios = sorted(self.root.glob("scenario-iteration-*.yaml"))
        if not scenarios:
            raise PackageValidationError("scenario-iteration-0.yaml is required")
        numbers = [int(re.fullmatch(r"scenario-iteration-(\d+)\.yaml", path.name).group(1)) for path in scenarios]
        if numbers != list(range(len(numbers))):
            raise PackageValidationError(f"iteration scenarios must be contiguous from zero: {numbers}")
        for scenario in scenarios:
            self.validate_scenario(scenario)
        return self

    def _validate_workflow(self) -> None:
        if self.workflow.get("version") != 1:
            raise PackageValidationError("workflow version must be 1")
        entries = self.workflow.get("entry_actions")
        if not isinstance(entries, list) or not entries:
            raise PackageValidationError("workflow requires entry_actions")
        unknown_actions = set(entries) - set(self.actions_data)
        reentry = _object(self.workflow.get("reentry", {}), "workflow reentry")
        unknown_actions |= set(reentry) - set(self.actions_data)
        stop = _object(self.workflow.get("stop_reentry_when_present", {}), "workflow stop_reentry_when_present")
        unknown_actions |= set(stop) - set(self.actions_data)
        for action_id, entity_ids in stop.items():
            if not isinstance(entity_ids, list) or not entity_ids or set(entity_ids) - set(self.entities):
                raise PackageValidationError(f"workflow stop_reentry_when_present for {action_id} must be a non-empty list of known entities")
        required_inputs = _object(self.workflow.get("required_inputs", {}), "workflow required_inputs")
        unknown_actions |= set(required_inputs) - set(self.actions_data)
        if unknown_actions:
            raise PackageValidationError(f"workflow references unknown actions: {sorted(unknown_actions)}")
        if set(reentry.values()) - REENTRY:
            raise PackageValidationError("workflow has unsupported re-entry policy")
        for action_id, entity_ids in required_inputs.items():
            if not isinstance(entity_ids, list):
                raise PackageValidationError(f"workflow required_inputs for {action_id} must be a list")
            if set(entity_ids) - set(self.entities):
                raise PackageValidationError(f"workflow required_inputs for {action_id} reference unknown entities")
        predicate = _object(self.workflow.get("iteration_complete_when"), "completion predicate")
        required = predicate.get("entities_present")
        if not isinstance(required, list) or not required:
            raise PackageValidationError("completion predicate requires entities_present")
        unknown_entities = set(required) - set(self.entities)
        initial = self.workflow.get("initial_entities", [])
        if not isinstance(initial, list):
            raise PackageValidationError("workflow initial_entities must be a list")
        unknown_entities |= set(initial) - set(self.entities)
        carry = self.workflow.get("carry_forward", [])
        if not isinstance(carry, list):
            raise PackageValidationError("workflow carry_forward must be a list")
        unknown_entities |= set(carry) - set(self.entities)
        if unknown_entities:
            raise PackageValidationError(f"workflow references unknown entities: {sorted(unknown_entities)}")

    def _validate_race(self) -> None:
        required = {"race_id", "model", "budget", "evaluation", "simulator"}
        missing = required - set(self.race)
        if missing:
            raise PackageValidationError(f"race.yaml missing keys: {sorted(missing)}")
        budget = _object(self.race["budget"], "race budget")
        if not isinstance(budget.get("max_action_runs"), int) or budget["max_action_runs"] < 1:
            raise PackageValidationError("budget.max_action_runs must be positive")
        for key in ("total_tokens_per_condition", "max_tokens_per_iteration"):
            if not isinstance(budget.get(key), int) or budget[key] < 1:
                raise PackageValidationError(f"budget.{key} must be positive")
        if budget["max_tokens_per_iteration"] > budget["total_tokens_per_condition"]:
            raise PackageValidationError("per-iteration token budget cannot exceed the total entrant budget")
        if "history" in self.race:
            history = _object(self.race["history"], "race history")
            if not isinstance(history.get("enabled", True), bool):
                raise PackageValidationError("history.enabled must be true or false")
            ceiling = history.get("telemetry_token_ceiling")
            if not isinstance(ceiling, int) or isinstance(ceiling, bool) or ceiling < 0:
                raise PackageValidationError("history.telemetry_token_ceiling must be a non-negative integer")
        model = _object(self.race["model"], "race model")
        if model.get("provider") not in {"mock", "openrouter"}:
            raise PackageValidationError("model.provider must be mock or openrouter")
        if not isinstance(model.get("id"), str) or not model["id"].strip():
            raise PackageValidationError("model.id must be a non-empty string")
        if not isinstance(model.get("max_output_tokens"), int) or model["max_output_tokens"] < 1:
            raise PackageValidationError("model.max_output_tokens must be positive")

    def design_contract(self) -> dict[str, Any] | None:
        """The public contract that describes a complete robot design (geometry and controller)."""
        for entity_id, entity in self.entities.items():
            if entity.get("system_boundary") != "public":
                continue
            contract = self.contract(entity_id)
            if contract and {"geometry", "controller"} <= set(contract.get("properties") or {}):
                return contract
        return None

    def _derive_design_bounds(self) -> None:
        """The design contract is the single source of design limits; race.yaml may not state different ones."""
        derived = design_bounds_from_contract(self.design_contract())
        declared = self.race.get("design_bounds")
        if derived is None:
            if declared is None and self.design_contract() is not None:
                raise PackageValidationError("no design limits: the design contract states no minimum/maximum and race.yaml has no design_bounds")
            return
        if declared is not None and declared != derived:
            raise PackageValidationError("race.yaml design_bounds disagree with the design contract; remove design_bounds from race.yaml, the contract is the single source of design limits")
        self.race["design_bounds"] = derived
        self.bounds_in_contract = True

    def _validate_reachability(self) -> None:
        available: set[str] = set(self.workflow.get("initial_entities", []))
        entries = set(self.workflow["entry_actions"])
        remaining = set(self.actions)
        changed = True
        while changed:
            changed = False
            for action_id in sorted(remaining):
                action = self.actions[action_id]
                if action_id in entries or action.required_inputs.issubset(available):
                    available.update(action.writes)
                    remaining.remove(action_id)
                    changed = True
                    break
        completion = set(self.workflow["iteration_complete_when"]["entities_present"])
        if not completion.issubset(available):
            raise PackageValidationError(f"completion predicate is unreachable: {sorted(completion - available)}")

    def validate_scenario(self, path: Path) -> None:
        scenario = _object(read_yaml(path), str(path))
        unexpected = set(scenario) - SCENARIO_KEYS
        if unexpected:
            raise PackageValidationError(f"scenario has structural/unknown keys: {sorted(unexpected)}")
        map_data = _object(scenario.get("map"), "scenario map")
        if map_data.get("inherits") != "base.yaml" or map_data.get("schema") != "v0.2":
            raise PackageValidationError("scenario must inherit base.yaml and use schema v0.2")
        if map_data.get("id") != self.topology["map"].get("id"):
            raise PackageValidationError("scenario map id must match topology map id")
        dimensions = _object(scenario.get("dimensions"), "scenario dimensions")
        axes = set(self.topology["map"]["dimension_axes"])
        if set(dimensions) != axes:
            raise PackageValidationError("scenario dimensions must exactly match topology axes")
        overrides = _object(scenario.get("overrides", {}), "scenario overrides")
        for section, items in overrides.items():
            if section not in OVERRIDE_FIELDS or not isinstance(items, list):
                raise PackageValidationError(f"invalid scenario override section {section}")
            ids = getattr(self, "actions_data" if section == "actions" else section)
            for item in items:
                value = _object(item, f"scenario {section} override")
                if value.get("id") not in ids or set(value) - OVERRIDE_FIELDS[section]:
                    raise PackageValidationError(f"invalid structural override in {section}")
        measurements = _object(scenario.get("measurements", {}), "scenario measurements")
        for element_id, values in measurements.items():
            element = next((group[element_id] for group in (self.actors, self.actions_data, self.entities, self.edges) if element_id in group), None)
            if element is None or not isinstance(values, list):
                raise PackageValidationError(f"invalid measurement element {element_id}")
            measures = {measure.get("id") for measure in element.get("measures", [])}
            for value in values:
                if not isinstance(value, dict) or value.get("measure") not in measures:
                    raise PackageValidationError(f"unknown measure on {element_id}")

    def require_read(self, action_id: str, entity_id: str) -> None:
        if entity_id not in self.actions[action_id].reads:
            raise PermissionError(f"{action_id} may not read {entity_id}")

    def require_write(self, action_id: str, entity_id: str) -> None:
        if entity_id not in self.actions[action_id].writes:
            raise PermissionError(f"{action_id} may not write {entity_id}")

    def contract(self, entity_id: str) -> dict[str, Any] | None:
        path = self.path("entities", entity_id, "contract.schema.json")
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise PackageValidationError(f"invalid contract for {entity_id}: {error}") from error
        if not isinstance(value, dict) or value.get("type") not in {None, "object"}:
            raise PackageValidationError(f"contract for {entity_id} must describe an object")
        if Draft202012Validator is not None:
            try:
                Draft202012Validator.check_schema(value)
            except Exception as error:
                raise PackageValidationError(f"invalid JSON Schema for {entity_id}: {error}") from error
        return value

    def validate_payload(self, entity_id: str, payload: dict[str, Any]) -> None:
        contract = self.contract(entity_id)
        if contract is None:
            return
        if Draft202012Validator is not None:
            errors = sorted(Draft202012Validator(contract).iter_errors(payload), key=lambda error: list(error.path))
            if errors:
                raise PackageValidationError(f"{entity_id} contract violation: {errors[0].message}")
            return
        self._validate_schema_value(contract, payload, entity_id)

    def _validate_schema_value(self, schema: dict[str, Any], value: Any, path: str) -> None:
        kinds = {"object": dict, "array": list, "string": str, "number": (int, float), "integer": int, "boolean": bool, "null": type(None)}
        kind = schema.get("type")
        if kind in kinds and (not isinstance(value, kinds[kind]) or kind in {"number", "integer"} and isinstance(value, bool)):
            raise PackageValidationError(f"{path} contract violation: expected {kind}")
        if "enum" in schema and value not in schema["enum"]:
            raise PackageValidationError(f"{path} contract violation: value is not in enum")
        if isinstance(value, dict):
            properties = schema.get("properties", {})
            missing = set(schema.get("required", [])) - set(value)
            if missing:
                raise PackageValidationError(f"{path} contract violation: missing {sorted(missing)}")
            if schema.get("additionalProperties") is False and set(value) - set(properties):
                raise PackageValidationError(f"{path} contract violation: unknown {sorted(set(value) - set(properties))}")
            for key, child in value.items():
                if key in properties:
                    self._validate_schema_value(properties[key], child, f"{path}.{key}")
        if isinstance(value, list) and isinstance(schema.get("items"), dict):
            for index, child in enumerate(value):
                self._validate_schema_value(schema["items"], child, f"{path}[{index}]")

    def ready_actions(self, available: set[str] | dict[str, str], invocations: dict[str, tuple[str, ...]]) -> list[str]:
        entity_ids = set(available)
        entries = set(self.workflow["entry_actions"])
        policies = self.workflow.get("reentry", {})
        stop = self.workflow.get("stop_reentry_when_present", {})
        ready: list[str] = []
        for action_id, action in self.actions.items():
            if action_id in invocations and action_id in stop and set(stop[action_id]) <= entity_ids:
                continue  # e.g. once the Evaluator has approved a build, the revision loop is over
            inputs = tuple(sorted(
                f"{entity}:{available[entity]}" if isinstance(available, dict) else entity
                for entity in action.trigger_inputs & entity_ids
            ))
            if action.required_inputs.issubset(entity_ids) or action_id in entries:
                previous = invocations.get(action_id)
                policy = policies.get(action_id, "on_new_inputs")
                if previous is None or (policy == "on_new_inputs" and previous != inputs):
                    ready.append(action_id)
        return sorted(ready)

    def definition_files(self) -> list[Path]:
        files = [self.base_path, self.workflow_path, self.race_path]
        files += sorted(self.root.glob("*.log.json"))
        files += sorted(self.root.glob("actions/*/instructions.md"))
        files += sorted(self.root.glob("actions/*/runtime.yaml"))
        files += sorted(self.root.glob("entities/*/contract.schema.json"))
        return files

    def hashes(self) -> dict[str, str]:
        return {
            str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.definition_files()
        }
