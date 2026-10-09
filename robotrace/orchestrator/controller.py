from __future__ import annotations

import re
import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .io import atomic_write, digest, read_yaml, write_json
from .map_package import ActionDefinition, MapPackage
from .transactions import ScenarioTransaction, recover_transactions
import yaml


CONTROLLER_VERSION = "map-driven-v2"


@dataclass(frozen=True)
class ActionResult:
    writes: dict[str, dict[str, Any]]
    labels: dict[str, str]
    notes: dict[str, str]
    event: dict[str, Any]


ActionExecutor = Callable[[ActionDefinition, dict[str, dict[str, Any]], dict[str, Any]], ActionResult]


class MapDrivenController:
    """Generic topology scheduler; team identity is never consulted."""

    def __init__(self, package: MapPackage, executor: ActionExecutor, simulator_version: str):
        self.package = package.validate()
        self.executor = executor
        self.simulator_version = simulator_version

    def freeze(self, manifest_path: Path) -> dict[str, Any]:
        if manifest_path.exists():
            raise FileExistsError(f"package already frozen: {manifest_path}")
        manifest = {
            "status": "frozen", "frozen_at": datetime.now(timezone.utc).isoformat(),
            "package": self.package.topology["map"]["id"], "files": self.package.hashes(),
            "controller_version": CONTROLLER_VERSION, "simulator_version": self.simulator_version,
        }
        manifest["manifest_hash"] = digest(manifest)
        write_json(manifest_path, manifest)
        return manifest

    def verify_frozen(self, manifest_path: Path) -> dict[str, Any]:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("files") != self.package.hashes():
            raise RuntimeError("frozen package definition changed")
        expected = manifest.pop("manifest_hash")
        if digest(manifest) != expected:
            raise RuntimeError("race manifest hash mismatch")
        manifest["manifest_hash"] = expected
        return manifest

    def run_iteration(self, iteration: int) -> Path:
        scenario = self.package.path(f"scenario-iteration-{iteration}.yaml")
        self.package.validate_scenario(scenario)
        iteration_dir = self.package.path(f"iteration-{iteration}")
        iteration_dir.mkdir(parents=True, exist_ok=True)
        recover_transactions(iteration_dir)
        available = {
            path.name: (path / "current").read_text(encoding="utf-8").strip()
            for path in iteration_dir.iterdir()
            if path.is_dir() and not path.name.startswith(".") and (path / "current").is_file()
        }
        invocations: dict[str, tuple[str, ...]] = {}
        run_counts: dict[str, int] = {}
        events_path = iteration_dir / "events.jsonl"
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                if event.get("type") == "action_completed":
                    invocations[event["action"]] = tuple(event.get("input_versions", []))
                    run_counts[event["action"]] = run_counts.get(event["action"], 0) + 1
        runs = sum(run_counts.values())
        input_tokens = output_tokens = 0
        if events_path.exists():
            for line in events_path.read_text(encoding="utf-8").splitlines():
                prior = json.loads(line)
                input_tokens += int(prior.get("input_tokens", 0))
                output_tokens += int(prior.get("output_tokens", 0))
        budget_config = self.package.race["budget"]
        maximum = budget_config["max_action_runs"]
        iteration_token_limit = budget_config["max_tokens_per_iteration"]
        total_token_limit = budget_config["total_tokens_per_condition"]
        prior_total_tokens = 0
        for prior_events in self.package.root.glob("iteration-*/events.jsonl"):
            if prior_events == events_path:
                continue
            for line in prior_events.read_text(encoding="utf-8").splitlines():
                prior = json.loads(line)
                prior_total_tokens += int(prior.get("input_tokens", 0)) + int(prior.get("output_tokens", 0))
        complete = set(self.package.workflow["iteration_complete_when"]["entities_present"])
        total_iterations = int(self.package.race.get("iterations", 1))
        plan = {
            "iteration": iteration, "iterations_total": total_iterations,
            "iterations_remaining_after_this": total_iterations - iteration - 1,
            "final_iteration": iteration == total_iterations - 1,
        }
        previous = self._previous_incomplete(iteration)
        while not complete.issubset(available):
            eligible = self.package.ready_actions(available, invocations)
            if not eligible:
                return self._close_incomplete(iteration, scenario, iteration_dir, available, invocations, complete, "workflow stalled: no action can run")
            action_id = eligible[0]
            action = self.package.actions[action_id]
            iteration_tokens = input_tokens + output_tokens
            remaining_iteration_tokens = iteration_token_limit - iteration_tokens
            remaining_total_tokens = total_token_limit - prior_total_tokens - iteration_tokens
            if action.runtime.get("kind") == "model" and min(remaining_iteration_tokens, remaining_total_tokens) < 1:
                return self._close_incomplete(iteration, scenario, iteration_dir, available, invocations, complete, "token budget exhausted")
            inputs: dict[str, dict[str, Any]] = {}
            for entity_id in sorted(action.reads & set(available)):
                self.package.require_read(action_id, entity_id)
                root = iteration_dir / entity_id
                current = (root / "current").read_text(encoding="utf-8").strip()
                inputs[entity_id] = json.loads((root / "versions" / current / "payload.json").read_text(encoding="utf-8"))
            context = {
                "iteration": iteration, "race": self.package.race,
                "iteration_plan": plan, "previous_iteration": previous,
                "instructions": action.instructions,
                "budget": {
                    "runs": runs, "maximum": maximum,
                    "iteration_tokens_used": iteration_tokens,
                    "iteration_tokens_remaining": remaining_iteration_tokens,
                    "total_tokens_used": prior_total_tokens + iteration_tokens,
                    "total_tokens_remaining": remaining_total_tokens,
                    "iterations_remaining_after_this": plan["iterations_remaining_after_this"],
                    "model_actions_still_to_run_this_iteration": sum(1 for other_id, other in self.package.actions.items() if other.runtime.get("kind") == "model" and other_id != action_id and not run_counts.get(other_id)),
                },
            }
            result = self.executor(action, inputs, context)
            unexpected = set(result.writes) - action.writes
            if unexpected:
                raise PermissionError(f"{action_id} attempted undeclared writes: {sorted(unexpected)}")
            transaction = ScenarioTransaction(self.package, scenario, iteration_dir, action_id)
            input_links = ", ".join(
                f"[{entity_id}](iteration-{iteration}/{entity_id}/versions/{available[entity_id]}/payload.json)" for entity_id in sorted(inputs)
            )
            for entity_id, payload in result.writes.items():
                transaction.write_entity(entity_id, payload)
                description = (result.notes.get(entity_id) or "").strip()
                links = f"- [Open this output](iteration-{iteration}/{entity_id}/versions/{transaction.id}/payload.json)"
                if input_links:
                    links += f"\n- Based on: {input_links}"
                transaction.update("entities", entity_id, label=result.labels.get(entity_id), notes=(description + "\n\n" if description else "") + links)
            transaction.update("actions", action_id, label=result.labels.get(action_id), notes=result.notes.get(action_id))
            input_versions = tuple(sorted(f"{entity}:{available[entity]}" for entity in action.trigger_inputs & set(available)))
            transaction.append_event("action_completed", {**result.event, "input_versions": list(input_versions), "runtime": action.runtime})
            input_tokens += int(result.event.get("input_tokens", 0))
            output_tokens += int(result.event.get("output_tokens", 0))
            iteration_tokens = input_tokens + output_tokens
            if iteration_tokens > iteration_token_limit or prior_total_tokens + iteration_tokens > total_token_limit:
                raise RuntimeError("model response exceeded the configured token budget")
            transaction.update_budget({
                "action_runs": runs + 1, "maximum_action_runs": maximum,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "iteration_tokens": iteration_tokens,
                "maximum_iteration_tokens": iteration_token_limit,
                "total_tokens": prior_total_tokens + iteration_tokens,
                "maximum_total_tokens": total_token_limit,
            })
            transaction.commit()
            for entity_id in result.writes:
                available[entity_id] = (iteration_dir / entity_id / "current").read_text(encoding="utf-8").strip()
            invocations[action_id] = input_versions
            run_counts[action_id] = run_counts.get(action_id, 0) + 1
            runs += 1
            if runs >= maximum and not complete.issubset(available):
                return self._close_incomplete(iteration, scenario, iteration_dir, available, invocations, complete, f"action-run budget exhausted: {runs} of {maximum} runs used before completion")
        write_json(iteration_dir / "outcome.json", {"complete": True})
        self._seed_next_iteration(iteration, scenario, iteration_dir)
        return scenario

    def _previous_incomplete(self, iteration: int) -> dict[str, Any] | None:
        """What the previous iteration failed to deliver, if anything; shown to the actors so they can learn from it."""
        path = self.package.path(f"iteration-{iteration - 1}", "outcome.json")
        if iteration < 1 or not path.is_file():
            return None
        outcome = json.loads(path.read_text(encoding="utf-8"))
        if outcome.get("complete"):
            return None
        return {key: outcome[key] for key in ("reason", "undelivered", "blocked_actions") if key in outcome}

    def _close_incomplete(self, iteration: int, scenario: Path, iteration_dir: Path, available: dict[str, str],
                          invocations: dict[str, tuple[str, ...]], complete: set[str], reason: str) -> Path:
        """An iteration that cannot finish is a race outcome, not a harness fault: record it, then move on."""
        blocked = {
            action_id: sorted(action.required_inputs - set(available))
            for action_id, action in self.package.actions.items()
            if action_id not in invocations and action.required_inputs - set(available)
        }
        write_json(iteration_dir / "outcome.json", {
            "complete": False, "reason": reason,
            "missing_completion_entities": sorted(complete - set(available)),
            "undelivered": sorted({entity for missing in blocked.values() for entity in missing}),
            "blocked_actions": blocked,
        })
        self._seed_next_iteration(iteration, scenario, iteration_dir)
        return scenario

    def _seed_next_iteration(self, iteration: int, scenario: Path, iteration_dir: Path) -> None:
        next_scenario = self.package.path(f"scenario-iteration-{iteration + 1}.yaml")
        if not next_scenario.exists() and iteration + 1 < int(self.package.race.get("iterations", 1)):
            data = read_yaml(scenario)
            data["map"]["scenario"] = f"Iteration {iteration + 1}"
            data["map"]["notes"] = f"Authoritative state carried forward after iteration {iteration}."
            data["dimensions"]["iteration"] = str(iteration + 1)
            atomic_write(next_scenario, yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
            next_dir = self.package.path(f"iteration-{iteration + 1}")
            carried: dict[str, str] = {}
            for entity_id in self.package.workflow.get("carry_forward", []):
                source = iteration_dir / entity_id
                if not (source / "current").exists():
                    continue
                source_version = (source / "current").read_text().strip()
                payload = json.loads((source / "versions" / source_version / "payload.json").read_text())
                version = "carried-" + digest(payload)[:16]
                write_json(next_dir / entity_id / "versions" / version / "payload.json", payload)
                write_json(next_dir / entity_id / "versions" / version / "version.json", {"source_iteration": iteration, "source_version": source_version, "hash": digest(payload)})
                atomic_write(next_dir / entity_id / "current", version + "\n")
                carried[entity_id] = version
            event = {"type": "scenario_created", "scenario": next_scenario.name, "from_iteration": iteration, "carried_entities": carried}
            write_json(iteration_dir / "scenario-created.json", event)
            write_json(next_dir / "checkpoint.json", {"state": "seeded", "from_iteration": iteration, "carried_entities": carried})


def race_title(template_title: str, race_id: str) -> str:
    """Insert the race label after "Robot Race": race-9 -> "Robot Race 9", dry-run-x -> "Robot Race dry-run-x"."""
    match = re.fullmatch(r"race-(\d+)", race_id)
    label = match.group(1) if match else race_id
    prefix = "Robot Race"
    if template_title.startswith(prefix):
        return f"{prefix} {label}{template_title[len(prefix):]}"
    return f"{prefix} {label} — {template_title}"


def clone_package(source: Path, destination: Path, race_id: str) -> Path:
    """Create a race-owned editable copy while preserving the source package."""
    if destination.exists():
        raise FileExistsError(destination)
    shutil.copytree(source, destination)
    race_path = destination / "config" / "race.yaml"
    race = read_yaml(race_path)
    race["race_id"] = race_id
    atomic_write(race_path, yaml.safe_dump(race, sort_keys=False))
    map_id = destination.name
    base_path = destination / "base.yaml"
    base = read_yaml(base_path)
    base["map"]["id"] = map_id
    base["map"]["title"] = race_title(str(base["map"].get("title", "")), race_id)
    atomic_write(base_path, yaml.safe_dump(base, sort_keys=False, allow_unicode=True))
    for scenario_path in destination.glob("scenario-iteration-*.yaml"):
        scenario = read_yaml(scenario_path)
        scenario["map"]["id"] = map_id
        atomic_write(scenario_path, yaml.safe_dump(scenario, sort_keys=False, allow_unicode=True))
    old_logs = list(destination.glob("*.log.json"))
    if old_logs:
        log = json.loads(old_logs[0].read_text(encoding="utf-8"))
        log.update({"map_id": map_id, "status": "draft", "description": f"Race-owned package for {race_id}."})
        new_log = destination / f"{map_id}.log.json"
        write_json(new_log, log)
        if old_logs[0] != new_log:
            old_logs[0].unlink()
    write_json(destination / "provenance.json", {"source": str(source.resolve()), "source_hashes": MapPackage(source).validate().hashes()})
    return destination


def definition_diff(previous: MapPackage, current: MapPackage) -> dict[str, dict[str, str | None]]:
    """Return an inspectable hash-level definition diff between race packages."""
    before, after = previous.validate().hashes(), current.validate().hashes()
    return {
        name: {"before": before.get(name), "after": after.get(name)}
        for name in sorted(set(before) | set(after))
        if before.get(name) != after.get(name)
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate, compare, and freeze map-driven race packages")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("package", type=Path)
    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("package", type=Path)
    freeze.add_argument("--manifest", type=Path)
    compare = subparsers.add_parser("diff")
    compare.add_argument("previous", type=Path)
    compare.add_argument("current", type=Path)
    args = parser.parse_args(argv)
    if args.command == "validate":
        package = MapPackage(args.package).validate()
        ready = package.ready_actions(set(package.workflow.get("initial_entities", [])), {})
        print(json.dumps({"status": "ready", "package": package.topology["map"]["id"], "initial_actions": ready}, indent=2))
        return 0
    if args.command == "diff":
        print(json.dumps(definition_diff(MapPackage(args.previous), MapPackage(args.current)), indent=2, sort_keys=True))
        return 0
    package = MapPackage(args.package).validate()
    manifest = args.manifest or package.path("race-manifest.json")
    controller = MapDrivenController(package, lambda *_: (_ for _ in ()).throw(RuntimeError("execution unavailable while freezing")), package.race["simulator"]["version"])
    print(json.dumps(controller.freeze(manifest), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
