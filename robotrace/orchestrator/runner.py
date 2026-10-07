from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import leaderboard, race_report, scenario_yaml, summary_svg, track_view_svg, write_manifest
from .io import atomic_write, digest, read_json, safe_child, write_json
from .model_client import ModelClient, ModelResponse, ROLE_INSTRUCTION_PATHS, make_client, role_instructions
from .validators import MEASUREMENTS, ValidationError, validate_controller, validate_geometry, validate_measurement_request, validate_package
from simulator.adapter import ADAPTER_VERSION, run_trial

ROOT = Path(__file__).resolve().parents[1]


def repository_changes_since_previous_race(experiment_id: str, runs_root: Path) -> tuple[str | None, list[dict[str, str]]]:
    """Return linked non-race commits since the previous completed numbered race."""
    match = re.fullmatch(r"race-(\d+)", experiment_id)
    if not match:
        return None, []
    race_number = int(match.group(1))
    previous_race = None
    for number in range(race_number - 1, -1, -1):
        manifest_path = runs_root / f"race-{number}" / "manifest.json"
        if manifest_path.exists() and read_json(manifest_path).get("status") == "complete":
            previous_race = f"race-{number}"
            break
    if previous_race is None:
        return None, []
    previous_number = previous_race.removeprefix("race-")
    try:
        baseline = subprocess.run(
            ["git", "log", "--diff-filter=A", "-1", "--format=%H", "--", f"robotrace/iteration-{previous_number}.yaml", f"robotrace-control/iteration-{previous_number}.yaml"],
            cwd=ROOT.parent, check=True, capture_output=True, text=True,
        ).stdout.strip()
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=ROOT.parent,
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        if not baseline:
            return previous_race, []
        repository_url = re.sub(r"^git@github\.com:", "https://github.com/", remote).removesuffix(".git")
        log = subprocess.run(
            ["git", "log", "--format=%H%x09%h%x09%s", f"{baseline}..HEAD"],
            cwd=ROOT.parent, check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        changes = []
        race_only = re.compile(rf"^(?:robotrace/runs/{re.escape(experiment_id)}/|robotrace/race-definitions/{re.escape(experiment_id)}/|robotrace/iteration-{race_number}\.yaml$|robotrace-control/iteration-{race_number}\.yaml$)")
        for line in log:
            commit_hash, short_hash, subject = line.split("\t", 2)
            files = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                cwd=ROOT.parent, check=True, capture_output=True, text=True,
            ).stdout.splitlines()
            publishes_current_race = any(path in {f"robotrace/iteration-{race_number}.yaml", f"robotrace-control/iteration-{race_number}.yaml"} for path in files)
            if publishes_current_race or (files and all(race_only.match(path) for path in files)):
                continue
            changes.append({"subject": subject, "short_hash": short_hash, "url": f"{repository_url}/commit/{commit_hash}"})
        return previous_race, changes
    except (OSError, subprocess.CalledProcessError):
        return previous_race, []


def publish_race_scenarios(
    run_root: Path,
    experiment_id: str,
    iterations: int,
    publication_roots: dict[str, Path] | None = None,
) -> dict[str, Path]:
    """Publish one immutable final-state scenario per condition and race."""
    match = re.fullmatch(r"race-(\d+)", experiment_id)
    if not match:
        return {}
    roots = publication_roots or {
        "loopsense": ROOT,
        "control": ROOT.parent / "robotrace-control",
    }
    source_iteration = iterations - 1
    published: dict[str, Path] = {}
    for condition, target_root in roots.items():
        source = run_root / "maps" / condition / f"iteration-{source_iteration}.yaml"
        if not source.exists():
            raise FileNotFoundError(f"final scenario missing: {source}")
        target = target_root / f"iteration-{match.group(1)}.yaml"
        if not target.exists():
            scenario, replacements = re.subn(
                r'^  scenario:.*$',
                f'  scenario: "Race {match.group(1)}"',
                source.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE,
            )
            if replacements != 1:
                raise ValueError(f"scenario name missing from final scenario: {source}")
            atomic_write(target, scenario)
        published[condition] = target
    return published


@dataclass
class Budget:
    total: int
    iteration_limit: int
    used: int = 0
    iteration_used: int = 0

    def charge(self, response: ModelResponse) -> None:
        amount = response.input_tokens + response.output_tokens
        if self.used + amount > self.total or self.iteration_used + amount > self.iteration_limit:
            raise RuntimeError("token budget exhausted")
        self.used += amount
        self.iteration_used += amount

    def next_iteration(self) -> None:
        self.iteration_used = 0

    def record(self) -> dict[str, int]:
        return {"allocated": self.total, "used": self.used, "remaining": self.total - self.used, "iteration_used": self.iteration_used, "iteration_limit": self.iteration_limit}


class ExperimentRunner:
    def __init__(self, config_path: Path, output_root: Path, resume: bool = False):
        self.config_path = config_path.resolve()
        self.config = read_json(self.config_path)
        self.run_root = safe_child(output_root.resolve(), self.config["experiment_id"])
        if self.run_root.exists() and not resume:
            raise FileExistsError(f"run already exists: {self.run_root}; pass --resume or choose another experiment_id")
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.client: ModelClient = make_client(self.config)
        self.resume = resume
        self.results: list[dict[str, Any]] = []
        self.current_condition = "run"
        self.current_iteration = -1
        self.current_actor = "initialisation"

    @staticmethod
    def learning_actor(actor: str) -> str:
        return "robot_integrator" if actor == "integration_feedback" else actor

    def learning_path(self, condition: str, actor: str) -> Path:
        return self.run_root / condition / "learning" / f"{self.learning_actor(actor)}.md"

    def learning_for(self, condition: str, actor: str) -> str:
        path = self.learning_path(condition, actor)
        return path.read_text(encoding="utf-8") if path.exists() else "No race-specific learning recorded yet."

    def ensure_track_views(self, condition: str, iteration: int, iteration_dir: Path, *, overwrite: bool = False) -> None:
        """Backfill canonical trial views for completed iterations without rerunning trials."""
        package_dir = iteration_dir / "entity1"
        if condition == "control":
            package_dir /= "candidate"
        package = {
            "geometry": read_json(package_dir / "geometry.json"),
            "controller": read_json(package_dir / "controller.json"),
            "observation_request": read_json(package_dir / ("measurement-request.json" if condition == "control" else "observation-request.json")),
        }
        tracks = {path.stem: read_json(path) for path in (ROOT / "tracks").glob("*/*.json")}
        for trials_dir in (iteration_dir / "entity2/trials", iteration_dir / "entity2/held-out/trials"):
            if not trials_dir.exists():
                continue
            for trial_dir in sorted(path for path in trials_dir.iterdir() if path.is_dir()):
                view_path = trial_dir / "track-view.svg"
                if view_path.exists() and not overwrite:
                    continue
                trial = read_json(trial_dir / "result.json")
                telemetry = read_json(trial_dir / "telemetry.json")
                track_view_svg(
                    {**trial, "telemetry": telemetry}, package, tracks[trial["track"]], view_path,
                    experiment=self.config["experiment_id"], condition=condition, iteration=iteration,
                )

    def audit(self, condition: str, iteration: int, state: str, details: dict[str, Any]) -> None:
        event = {"timestamp": datetime.now(timezone.utc).isoformat(), "condition": condition, "iteration": iteration, "state": state, **details}
        path = self.run_root / "audit.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

    def call(self, condition: str, iteration: int, actor: str, context: dict[str, Any], budget: Budget, call_dir: Path) -> dict[str, Any]:
        forbidden = {"entity2", "held_out_tracks", "run_root"}.intersection(context)
        if forbidden:
            raise RuntimeError(f"forbidden model context: {sorted(forbidden)}")
        context_with_budget = {**context, "budget": budget.record()}
        response_path = call_dir / "response.json"
        ledger_path = call_dir / "budget-ledger.json"
        if self.resume and response_path.exists():
            if not ledger_path.exists():
                raise RuntimeError(f"incomplete saved model call: {call_dir}")
            ledger = read_json(ledger_path)
            budget.used = max(budget.used, int(ledger["used"]))
            budget.iteration_used = max(budget.iteration_used, int(ledger["iteration_used"]))
            return read_json(response_path)
        context_manifest = {"actor": actor, "keys": sorted(context_with_budget), "hashes": {key: digest(value) for key, value in context_with_budget.items()}}
        write_json(call_dir / "context-manifest.json", context_manifest)
        response = self.client.call(actor, context_with_budget)
        budget.charge(response)
        write_json(call_dir / "response.json", response.output)
        write_json(call_dir / "budget-ledger.json", budget.record())
        self.audit(condition, iteration, f"model:{actor}", {"model_request_identifier": response.request_id, "token_usage": response.input_tokens + response.output_tokens, "artifact_hash": digest(response.output), "validation": "pending"})
        return response.output

    def constraints_for(self, actor: str) -> dict[str, Any]:
        constraints: dict[str, Any] = {"supported_measurements": sorted(MEASUREMENTS)}
        if actor in {"geometry_builder", "robot_integrator", "optimizer"}:
            constraints["design_bounds"] = self.config["design_bounds"]
        if actor in {"robot_integrator", "optimizer"}:
            constraints["controller_bounds"] = {
                "base_speed": [0.05, 2], "kp": [0, 20], "ki": [0, 5], "kd": [0, 10],
                "sensor_weight": [-2, 2], "line_loss": ["stop", "search_left", "search_right", "last_direction"],
            }
        return constraints

    def validate_complete_output(self, output: dict[str, Any]) -> None:
        errors: list[str] = []
        geometry = output.get("geometry")
        controller = output.get("controller")
        request = output.get("observation_request")
        if not isinstance(geometry, dict):
            errors.append("geometry must be an object")
        else:
            try:
                validate_geometry(geometry, self.config["design_bounds"])
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                errors.append(f"geometry: {error}")
        if not isinstance(controller, dict):
            errors.append("controller must be an object")
        elif isinstance(geometry, dict) and isinstance(geometry.get("sensor_positions"), list):
            try:
                validate_controller(controller, len(geometry["sensor_positions"]))
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                errors.append(f"controller: {error}")
        else:
            errors.append("controller cannot be validated until geometry.sensor_positions is a list")
        if not isinstance(request, dict):
            errors.append("observation_request must be an object")
        else:
            try:
                validate_measurement_request(request)
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                errors.append(f"observation_request: {error}")
        if not isinstance(output.get("notes"), str):
            errors.append("notes must be a string")
        if errors:
            raise ValidationError("; ".join(errors))

    def validated_call(self, condition: str, iteration: int, actor: str, context: dict[str, Any], budget: Budget, call_dir: Path, validator: Any) -> dict[str, Any]:
        full_context = {**context, "learning": self.learning_for(condition, actor), "constraints": self.constraints_for(actor)}
        repairs = int(self.config["budget"].get("repair_calls_per_artifact", 0))
        invalid: dict[str, Any] | None = None
        error_text = ""
        for attempt in range(repairs + 1):
            attempt_context = full_context
            attempt_dir = call_dir if attempt == 0 else call_dir / f"repair-{attempt}"
            if attempt:
                attempt_context = {
                    **full_context,
                    "invalid_artifact": invalid,
                    "validation_errors": [error_text],
                    "repair_attempt": attempt,
                    "repair_instruction": "Return a corrected replacement artifact. Preserve valid intent and change only what is needed to satisfy every error and constraint.",
                }
            self.current_condition, self.current_iteration, self.current_actor = condition, iteration, actor
            output = self.call(condition, iteration, actor, attempt_context, budget, attempt_dir)
            try:
                validator(output)
                if not isinstance(output.get("learning"), str) or not output["learning"].strip():
                    raise ValidationError("learning must be a non-empty string")
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                invalid = output
                error_text = str(error)
                self.audit(condition, iteration, f"model:{actor}:invalid", {"attempt": attempt, "artifact_hash": digest(output), "validation": "invalid", "error": error_text})
                if attempt == repairs:
                    raise ValidationError(f"{actor} remained invalid after {repairs} repair call(s): {error_text}") from error
                continue
            self.audit(condition, iteration, f"model:{actor}:valid", {"attempt": attempt, "artifact_hash": digest(output), "validation": "valid"})
            atomic_write(self.learning_path(condition, actor), output["learning"].strip() + "\n")
            return output
        raise AssertionError("unreachable validation loop")

    def package_entity(self, directory: Path, output: dict[str, Any], control: bool = False) -> dict[str, Any]:
        write_json(directory / "geometry.json", output["geometry"])
        write_json(directory / "controller.json", output["controller"])
        request_name = "measurement-request.json" if control else "observation-request.json"
        write_json(directory / request_name, output["observation_request"])
        notes_name = "optimization-notes.md" if control else "integration-notes.md"
        atomic_write(directory / notes_name, output["notes"] + "\n")
        files = ["geometry.json", "controller.json", request_name, notes_name]
        write_manifest(directory, directory.name, files, [])
        return {"geometry": output["geometry"], "controller": output["controller"], "observation_request": output["observation_request"]}

    def loopsense_build(self, iteration_dir: Path, iteration: int, budget: Budget) -> dict[str, Any]:
        builder_returns = self.previous_returns("loopsense", iteration, "geometry_builder")
        integrator_returns = self.previous_returns("loopsense", iteration, "robot_integrator")
        agreement = self.config.get("initial_conditions", {}).get("loopsense_working_agreement") or (ROOT / "conditions/loopsense/working-agreement-v0.md").read_text()
        geometry_call = iteration_dir / "calls/geometry-builder"
        def validate_geometry_output(output: dict[str, Any]) -> None:
            errors: list[str] = []
            try:
                validate_geometry(output["geometry"], self.config["design_bounds"])
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                errors.append(f"geometry: {error}")
            try:
                validate_measurement_request(output["feedback_request"])
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                errors.append(f"feedback_request: {error}")
            if not isinstance(output["intent"], str):
                errors.append("intent must be a string")
            if errors:
                raise ValidationError("; ".join(errors))
        geometry = self.validated_call("loopsense", iteration, "geometry_builder", {"iteration": iteration, "working_agreement": agreement, "private_expertise": (ROOT / "conditions/loopsense/private/geometry.md").read_text(), "race_data_for_geometry": builder_returns["race_data"], "integration_feedback": builder_returns["integration_feedback"]}, budget, geometry_call, validate_geometry_output)
        entity0 = iteration_dir / "entity0"
        write_json(entity0 / "geometry.json", geometry["geometry"])
        atomic_write(entity0 / "intent.md", geometry["intent"] + "\n")
        write_json(entity0 / "feedback-request.json", geometry["feedback_request"])
        write_manifest(entity0, "entity0", ["geometry.json", "intent.md", "feedback-request.json"], ["entityR1", "entityR2A", "entityTeam0", "entityPrv0"])
        def validate_integrated(output: dict[str, Any]) -> None:
            if output["geometry"] != geometry["geometry"]:
                raise ValidationError("integrator mutated upstream geometry")
            self.validate_complete_output(output)
        integrated = self.validated_call("loopsense", iteration, "robot_integrator", {"iteration": iteration, "geometry": geometry["geometry"], "geometry_intent": geometry["intent"], "working_agreement": agreement, "private_expertise": (ROOT / "conditions/loopsense/private/integration.md").read_text(), "race_data_for_integration": integrator_returns["race_data"]}, budget, iteration_dir / "calls/robot-integrator", validate_integrated)
        package = self.package_entity(iteration_dir / "entity1", integrated)
        validate_package(package, self.config["design_bounds"])
        return package

    def control_build(self, iteration_dir: Path, iteration: int, budget: Budget) -> dict[str, Any]:
        blackboard = self.run_root / "control" / "blackboard" / f"iteration-{iteration}"
        optimizer_returns = self.previous_returns("control", iteration, "optimizer")
        evaluator_returns = self.previous_returns("control", iteration, "evaluator")
        initial_criteria = self.config.get("initial_conditions", {}).get("control_criteria") or (ROOT / "conditions/control/working-agreement-v0.md").read_text()
        feedback: dict[str, Any] | None = None
        maximum = int(self.config["budget"].get("max_control_cycles", 2))
        for cycle in range(maximum):
            def validate_candidate(output: dict[str, Any]) -> None:
                self.validate_complete_output(output)
            candidate = self.validated_call("control", iteration, "optimizer", {"iteration": iteration, "initial_criteria": initial_criteria, "blackboard_history": self.control_blackboard_history(), "race_data_for_optimizer": optimizer_returns["race_data"], "evaluator_feedback": feedback, "private_expertise": (ROOT / "conditions/control/private/optimizer.md").read_text()}, budget, iteration_dir / f"calls/optimizer-{cycle}", validate_candidate)
            candidate_dir = blackboard / f"candidate-{cycle}"
            package = self.package_entity(candidate_dir, candidate, control=True)
            validate_package(package, self.config["design_bounds"])
            candidate_id = digest(package)
            def validate_evaluation(output: dict[str, Any]) -> None:
                if output.get("decision") not in {"ship", "revise"}:
                    raise ValidationError("decision must be ship or revise")
                if not isinstance(output.get("rationale"), str):
                    raise ValidationError("rationale must be a string")
                if output["decision"] == "ship" and output.get("selected_candidate") != candidate_id:
                    raise ValidationError("shipping must select the exact current candidate")
                if output["decision"] == "revise" and not isinstance(output.get("feedback"), list):
                    raise ValidationError("revision feedback must be a list")
            evaluation = self.validated_call("control", iteration, "evaluator", {"iteration": iteration, "initial_criteria": initial_criteria, "blackboard_history": self.control_blackboard_history(), "candidate": package, "candidate_id": candidate_id, "rationale": candidate["notes"], "race_data_for_evaluator": evaluator_returns["race_data"], "private_expertise": (ROOT / "conditions/control/private/evaluator.md").read_text()}, budget, iteration_dir / f"calls/evaluator-{cycle}", validate_evaluation)
            public_evaluation = {key: value for key, value in evaluation.items() if key != "learning"}
            write_json(blackboard / f"evaluation-{cycle}.json", public_evaluation)
            if evaluation.get("decision") == "ship":
                if evaluation.get("selected_candidate") != candidate_id:
                    raise RuntimeError("evaluator did not select the exact current candidate")
                break
            feedback = {"rationale": evaluation.get("rationale", ""), "feedback": evaluation.get("feedback", [])}
            write_json(iteration_dir / "entityR1" / f"feedback-{cycle}.json", feedback)
        else:
            evaluation = {"decision": "ship", "selected_candidate": candidate_id, "rationale": "Budget policy selected the latest valid candidate.", "feedback": []}
        approved = iteration_dir / "entity1"
        shutil.copytree(candidate_dir, approved / "candidate")
        write_json(approved / "approval.json", {key: value for key, value in evaluation.items() if key != "learning"})
        atomic_write(approved / "candidate-hash.txt", candidate_id + "\n")
        write_manifest(approved, "entity1", ["candidate", "approval.json", "candidate-hash.txt"], [f"../blackboard/iteration-{iteration}/candidate-{cycle}"])
        if digest(package) != candidate_id:
            raise RuntimeError("approved candidate changed")
        return package

    def control_blackboard_history(self) -> list[dict[str, Any]]:
        root = self.run_root / "control" / "blackboard"
        history: list[dict[str, Any]] = []
        for path in sorted(root.glob("iteration-*/*")):
            if path.is_dir() and path.name.startswith("candidate-"):
                record: dict[str, Any] = {"path": str(path.relative_to(root)), "kind": "candidate"}
                for name in ("geometry.json", "controller.json", "measurement-request.json"):
                    if (path / name).exists():
                        record[name.removesuffix(".json")] = read_json(path / name)
                notes = path / "optimization-notes.md"
                if notes.exists():
                    record["notes"] = notes.read_text(encoding="utf-8")
                history.append(record)
            elif path.is_file() and path.name.startswith("evaluation-") and path.suffix == ".json":
                history.append({"path": str(path.relative_to(root)), "kind": "evaluation", "evaluation": read_json(path)})
        return history

    def previous_returns(self, condition: str, iteration: int, recipient: str) -> dict[str, Any]:
        if iteration == 0:
            return {"race_data": None, **({"integration_feedback": None} if recipient == "geometry_builder" else {})}
        previous = self.run_root / condition / f"iteration-{iteration - 1}"
        return_id = "entityR2A" if recipient in {"geometry_builder", "optimizer"} else "entityR2B"
        measurement_path = previous / return_id / "measurements.json"
        result: dict[str, Any] = {"race_data": read_json(measurement_path) if measurement_path.exists() else None}
        if recipient == "geometry_builder":
            feedback_path = previous / "entityR1/feedback.json"
            result["integration_feedback"] = read_json(feedback_path) if feedback_path.exists() else None
        return result

    def evaluate(self, condition: str, iteration: int, iteration_dir: Path, package: dict[str, Any], budget: Budget) -> dict[str, Any]:
        trials: list[dict[str, Any]] = []
        track_ids = [self.config["evaluation"]["anchor_track"], *self.config["evaluation"]["development_tracks"]]
        track_ids = list(dict.fromkeys(track_ids))
        tracks = {path.stem: read_json(path) for path in (ROOT / "tracks").glob("*/*.json")}
        for track_id in track_ids:
            for seed in self.config["evaluation"]["seeds"]:
                trial_id = f"{track_id}-{seed}"
                trial_dir = iteration_dir / "entity2/trials" / trial_id
                result_path = trial_dir / "result.json"
                telemetry_path = trial_dir / "telemetry.json"
                if self.resume and result_path.exists() and telemetry_path.exists():
                    trial = read_json(result_path)
                    telemetry = read_json(telemetry_path)
                else:
                    trial = run_trial(package, tracks[track_id], seed, self.config)
                    telemetry = trial.pop("telemetry", [])
                    write_json(telemetry_path, telemetry)
                    write_json(result_path, trial)
                    track_view_svg(
                        {**trial, "telemetry": telemetry}, package, tracks[track_id], trial_dir / "track-view.svg",
                        experiment=self.config["experiment_id"], condition=condition, iteration=iteration,
                    )
                    self.audit(condition, iteration, "trial_complete", {"trial_id": trial_id, "artifact_hash": digest(trial), "simulator_version": ADAPTER_VERSION})
                if not (trial_dir / "track-view.svg").exists():
                    track_view_svg(
                        {**trial, "telemetry": telemetry}, package, tracks[track_id], trial_dir / "track-view.svg",
                        experiment=self.config["experiment_id"], condition=condition, iteration=iteration,
                    )
                trials.append({**trial, "trial_id": trial_id, "telemetry": telemetry})
        valid = [trial for trial in trials if "metrics" in trial]
        aggregate = {key: round(sum(t["metrics"][key] for t in valid) / len(valid), 6) for key in valid[0]["metrics"]} if valid else {}
        score = round(sum(trial["score"] for trial in trials) / len(trials), 6)
        result = {"condition": condition, "iteration": iteration, "score": score, "trials": [{key: value for key, value in trial.items() if key != "telemetry"} for trial in trials], "aggregate": aggregate}
        if iteration == self.config["iterations"] - 1:
            held_out_trials: list[dict[str, Any]] = []
            for track_id in self.config["evaluation"]["held_out_tracks"]:
                for seed in self.config["evaluation"]["seeds"]:
                    trial_id = f"{track_id}-{seed}"
                    trial_dir = iteration_dir / "entity2/held-out/trials" / trial_id
                    result_path = trial_dir / "result.json"
                    telemetry_path = trial_dir / "telemetry.json"
                    if self.resume and result_path.exists() and telemetry_path.exists():
                        trial = read_json(result_path)
                        telemetry = read_json(telemetry_path)
                    else:
                        trial = run_trial(package, tracks[track_id], seed, self.config)
                        telemetry = trial.pop("telemetry", [])
                        write_json(telemetry_path, telemetry)
                        write_json(result_path, trial)
                        track_view_svg(
                            {**trial, "telemetry": telemetry}, package, tracks[track_id], trial_dir / "track-view.svg",
                            experiment=self.config["experiment_id"], condition=condition, iteration=iteration,
                        )
                        self.audit(condition, iteration, "held_out_trial_complete", {"trial_id": trial_id, "artifact_hash": digest(trial), "simulator_version": ADAPTER_VERSION})
                    if not (trial_dir / "track-view.svg").exists():
                        track_view_svg(
                            {**trial, "telemetry": telemetry}, package, tracks[track_id], trial_dir / "track-view.svg",
                            experiment=self.config["experiment_id"], condition=condition, iteration=iteration,
                        )
                    held_out_trials.append({**trial, "trial_id": trial_id, "telemetry": telemetry})
            held_out_valid = [trial for trial in held_out_trials if "metrics" in trial]
            held_out_aggregate = {key: round(sum(t["metrics"][key] for t in held_out_valid) / len(held_out_valid), 6) for key in held_out_valid[0]["metrics"]} if held_out_valid else {}
            held_out_score = round(sum(trial["score"] for trial in held_out_trials) / len(held_out_trials), 6) if held_out_trials else 0.0
            result["held_out"] = {
                "score": held_out_score,
                "aggregate": held_out_aggregate,
                "trials": [{key: value for key, value in trial.items() if key != "telemetry"} for trial in held_out_trials],
            }
        result["artifact_hash"] = digest(result)
        write_json(iteration_dir / "entity2/result.json", result)
        atomic_write(iteration_dir / "entity2/summary.md", f"# {condition} iteration {iteration}\n\nComposite score: {score:.4f}\n")
        summary_svg(condition, iteration, trials, iteration_dir / "entity2/iteration-summary.svg")
        write_manifest(iteration_dir / "entity2", "entity2", ["result.json", "summary.md", "iteration-summary.svg", "trials"], ["entity1"])
        measurements = aggregate | {"score": score}
        source_trials = [trial["trial_id"] for trial in trials]
        for return_id in ("entityR2A", "entityR2B"):
            target = iteration_dir / return_id
            write_json(target / "measurements.json", measurements)
            atomic_write(target / "measurement-catalogue-version", self.config["simulator"]["measurement_catalogue_version"] + "\n")
            atomic_write(target / "source-run-id", self.config["experiment_id"] + "\n")
            write_json(target / "source-trial-ids", source_trials)
            requested = package["observation_request"]["measurements"]
            write_json(target / "request-coverage.json", {"requested": requested, "supplied": [item for item in requested if item in measurements]})
            write_manifest(target, return_id, ["measurements.json", "measurement-catalogue-version", "source-run-id", "source-trial-ids", "request-coverage.json"], ["entity2"])
        if condition == "loopsense":
            def validate_feedback(output: dict[str, Any]) -> None:
                if not isinstance(output.get("summary"), str) or not isinstance(output.get("requests"), list):
                    raise ValidationError("integration feedback requires a string summary and a list of requests")
            feedback = self.validated_call(condition, iteration, "integration_feedback", {"iteration": iteration, "race_data_for_integration": measurements, "geometry": package["geometry"]}, budget, iteration_dir / "calls/integration-feedback", validate_feedback)
            write_json(iteration_dir / "entityR1/feedback.json", {"summary": feedback["summary"], "requests": feedback["requests"]})
            write_manifest(iteration_dir / "entityR1", "entityR1", ["feedback.json"], ["entityR2B"])
        return result

    def run(self) -> Path:
        try:
            return self._run()
        except Exception as error:
            manifest_path = self.run_root / "manifest.json"
            manifest = read_json(manifest_path) if manifest_path.exists() else {"experiment_id": self.config["experiment_id"], "config": self.config}
            manifest.update({
                "status": "failed",
                "failed_condition": self.current_condition,
                "failed_iteration": self.current_iteration,
                "failed_actor": self.current_actor,
                "error_type": type(error).__name__,
                "error": str(error),
                "failed_at": datetime.now(timezone.utc).isoformat(),
            })
            write_json(manifest_path, manifest)
            self.audit(self.current_condition, self.current_iteration, "run_failed", {"actor": self.current_actor, "error_type": type(error).__name__, "error": str(error)})
            raise

    def _run(self) -> Path:
        existing_manifest = self.run_root / "manifest.json"
        instruction_hashes = {actor: digest(role_instructions(actor)) for actor in sorted(ROLE_INSTRUCTION_PATHS)}
        if self.resume and existing_manifest.exists():
            frozen = read_json(existing_manifest)
            if frozen.get("config_hash") != digest(self.config):
                raise RuntimeError("resume configuration differs from the frozen run configuration")
            if frozen.get("plan_hash") != digest((ROOT / "IMPLEMENTATION_PLAN.md").read_bytes()):
                raise RuntimeError("resume implementation plan differs from the frozen run plan")
            if frozen.get("role_instruction_hashes") != instruction_hashes:
                raise RuntimeError("resume role instructions differ from the frozen run instructions")
        write_json(self.run_root / "manifest.json", {"experiment_id": self.config["experiment_id"], "config": self.config, "config_hash": digest(self.config), "plan_hash": digest((ROOT / "IMPLEMENTATION_PLAN.md").read_bytes()), "role_instruction_hashes": instruction_hashes, "status": "running"})
        maps_root = self.run_root / "maps"
        (maps_root / "loopsense").mkdir(parents=True, exist_ok=True)
        (maps_root / "control").mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "base.yaml", maps_root / "loopsense/base.yaml")
        shutil.copy2(ROOT.parent / "robotrace-control/base.yaml", maps_root / "control/base.yaml")
        budgets = {condition: Budget(self.config["budget"]["total_tokens_per_condition"], self.config["budget"]["max_tokens_per_iteration"]) for condition in self.config["conditions"]}
        for iteration in range(self.config["iterations"]):
            for condition in self.config["conditions"]:
                budget = budgets[condition]
                budget.next_iteration()
                self.current_condition, self.current_iteration, self.current_actor = condition, iteration, "iteration"
                iteration_dir = self.run_root / condition / f"iteration-{iteration}"
                checkpoint = iteration_dir / "checkpoint.json"
                if checkpoint.exists() and read_json(checkpoint).get("complete"):
                    self.ensure_track_views(condition, iteration, iteration_dir)
                    saved_budget = read_json(checkpoint)["budget"]
                    budget.used = max(budget.used, int(saved_budget["used"]))
                    self.results.append(read_json(iteration_dir / "entity2/result.json"))
                    continue
                self.audit(condition, iteration, "iteration_started", {"simulator_version": self.config["simulator"]["version"]})
                package = self.loopsense_build(iteration_dir, iteration, budget) if condition == "loopsense" else self.control_build(iteration_dir, iteration, budget)
                result = self.evaluate(condition, iteration, iteration_dir, package, budget)
                artifact_base = f"runs/{self.config['experiment_id']}"
                report_base = self.config["publication"]["base_url"].removesuffix("/runs")
                report_url = f"{report_base}/{self.config['experiment_id'].upper().replace('-', '_')}_REPORT.md"
                initial_key = "loopsense_working_agreement" if condition == "loopsense" else "control_criteria"
                setup_notes = self.config.get("initial_conditions", {}).get(initial_key, "See the frozen race manifest.")
                view_urls: list[tuple[str, str]] = []
                anchor = self.config["evaluation"]["anchor_track"]
                for trial in result["trials"]:
                    group = "anchor" if trial["track"] == anchor else "development"
                    url = f"{artifact_base}/{condition}/iteration-{iteration}/entity2/trials/{trial['trial_id']}/track-view.svg"
                    view_urls.append((f"{group}: {trial['trial_id']} track view", url))
                for trial in result.get("held_out", {}).get("trials", []):
                    url = f"{artifact_base}/{condition}/iteration-{iteration}/entity2/held-out/trials/{trial['trial_id']}/track-view.svg"
                    view_urls.append((f"held-out: {trial['trial_id']} track view", url))
                scenario = scenario_yaml("base.yaml", condition, iteration, f"{artifact_base}/{condition}/iteration-{iteration}/entity2/iteration-summary.svg", f"{artifact_base}/leaderboard.svg", result, setup_notes, view_urls, report_url)
                atomic_write(iteration_dir / "scenario.yaml", scenario)
                atomic_write(maps_root / ("loopsense" if condition == "loopsense" else "control") / f"iteration-{iteration}.yaml", scenario)
                write_json(checkpoint, {"complete": True, "result_hash": result["artifact_hash"], "budget": budget.record()})
                self.audit(condition, iteration, "iteration_complete", {"artifact_hash": result["artifact_hash"], "token_usage": budget.iteration_used, "validation": "valid", "simulator_version": self.config["simulator"]["version"]})
                self.results.append(result)
        leaderboard(self.run_root, self.results)
        previous_race, repo_changes = repository_changes_since_previous_race(self.config["experiment_id"], self.run_root.parent)
        race_report(self.run_root, self.config["experiment_id"], self.results, self.config, repo_changes, previous_race)
        match = re.fullmatch(r"race-(\d+)", self.config["experiment_id"])
        if match:
            race_report(ROOT, self.config["experiment_id"], self.results, self.config, repo_changes, previous_race, f"runs/{self.config['experiment_id']}/", f"RACE_{match.group(1)}_REPORT.md")
        published_scenarios = publish_race_scenarios(
            self.run_root,
            self.config["experiment_id"],
            self.config["iterations"],
        )
        manifest = read_json(self.run_root / "manifest.json")
        manifest["status"] = "complete"
        manifest["result_hashes"] = [result["artifact_hash"] for result in self.results]
        manifest["published_scenarios"] = {condition: str(path) for condition, path in published_scenarios.items()}
        write_json(self.run_root / "manifest.json", manifest)
        return self.run_root


def validate_config(config: dict[str, Any]) -> None:
    required = {"experiment_id", "iterations", "conditions", "model", "budget", "simulator", "evaluation", "publication", "design_bounds", "score"}
    missing = required - set(config)
    if missing:
        raise ValueError(f"missing config keys: {sorted(missing)}")
    if set(config["conditions"]) != {"loopsense", "control"}:
        raise ValueError("both and only loopsense and control conditions are required")
    if config["iterations"] < 1:
        raise ValueError("iterations must be positive")
    budget = config["budget"]
    for key in ("total_tokens_per_condition", "max_tokens_per_iteration", "max_control_cycles"):
        if not isinstance(budget.get(key), int) or budget[key] < 1:
            raise ValueError(f"budget.{key} must be a positive integer")
    repairs = budget.get("repair_calls_per_artifact", 0)
    if not isinstance(repairs, int) or repairs < 0:
        raise ValueError("budget.repair_calls_per_artifact must be a non-negative integer")
    if budget["max_tokens_per_iteration"] > budget["total_tokens_per_condition"]:
        raise ValueError("per-iteration token budget cannot exceed the total per-condition budget")
    if config["simulator"].get("measurement_catalogue_version") != "v1":
        raise ValueError("unsupported measurement catalogue version")


def initialise_race(race_id: str, definitions_root: Path = ROOT / "race-definitions") -> Path:
    if not re.fullmatch(r"race-\d+", race_id):
        raise ValueError("race ID must look like race-0")
    target = definitions_root / race_id / "config.json"
    if target.exists():
        raise FileExistsError(f"race definition already exists: {target}")
    config = read_json(ROOT / "config/experiment.yaml")
    config["experiment_id"] = race_id
    config["mode"] = "pilot"
    write_json(target, config)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the LoopSense robot-race experiment")
    parser.add_argument("--config", type=Path, default=ROOT / "config/experiment.yaml")
    parser.add_argument("--output", type=Path, default=ROOT / "runs")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--init-race", metavar="RACE_ID", help="create an editable race definition, for example race-0")
    args = parser.parse_args(argv)
    if args.init_race:
        path = initialise_race(args.init_race)
        print(path)
        return 0
    config = read_json(args.config)
    validate_config(config)
    if args.validate_only:
        print("configuration valid")
        return 0
    run_root = ExperimentRunner(args.config, args.output, args.resume).run()
    print(run_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
