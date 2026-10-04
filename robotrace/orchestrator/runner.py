from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifacts import leaderboard, scenario_yaml, summary_svg, trajectory_svg, write_manifest
from .io import atomic_write, digest, read_json, safe_child, write_json
from .model_client import ModelClient, ModelResponse, make_client
from .validators import MEASUREMENTS, ValidationError, validate_controller, validate_geometry, validate_measurement_request, validate_package
from simulator.adapter import ADAPTER_VERSION, run_trial

ROOT = Path(__file__).resolve().parents[1]


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
        full_context = {**context, "constraints": self.constraints_for(actor)}
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
            except (ValidationError, KeyError, TypeError, ValueError) as error:
                invalid = output
                error_text = str(error)
                self.audit(condition, iteration, f"model:{actor}:invalid", {"attempt": attempt, "artifact_hash": digest(output), "validation": "invalid", "error": error_text})
                if attempt == repairs:
                    raise ValidationError(f"{actor} remained invalid after {repairs} repair call(s): {error_text}") from error
                continue
            self.audit(condition, iteration, f"model:{actor}:valid", {"attempt": attempt, "artifact_hash": digest(output), "validation": "valid"})
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
        prior = self.previous_returns("loopsense", iteration)
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
        geometry = self.validated_call("loopsense", iteration, "geometry_builder", {"iteration": iteration, "working_agreement": agreement, "private_expertise": (ROOT / "conditions/loopsense/private/geometry.md").read_text(), **prior}, budget, geometry_call, validate_geometry_output)
        entity0 = iteration_dir / "entity0"
        write_json(entity0 / "geometry.json", geometry["geometry"])
        atomic_write(entity0 / "intent.md", geometry["intent"] + "\n")
        write_json(entity0 / "feedback-request.json", geometry["feedback_request"])
        write_manifest(entity0, "entity0", ["geometry.json", "intent.md", "feedback-request.json"], sorted(prior))
        def validate_integrated(output: dict[str, Any]) -> None:
            if output["geometry"] != geometry["geometry"]:
                raise ValidationError("integrator mutated upstream geometry")
            self.validate_complete_output(output)
        integrated = self.validated_call("loopsense", iteration, "robot_integrator", {"iteration": iteration, "geometry": geometry["geometry"], "geometry_intent": geometry["intent"], "working_agreement": agreement, "private_expertise": (ROOT / "conditions/loopsense/private/integration.md").read_text(), "race_data_for_integration": prior.get("race_data_for_integration")}, budget, iteration_dir / "calls/robot-integrator", validate_integrated)
        package = self.package_entity(iteration_dir / "entity1", integrated)
        validate_package(package, self.config["design_bounds"])
        return package

    def control_build(self, iteration_dir: Path, iteration: int, budget: Budget) -> dict[str, Any]:
        blackboard = iteration_dir / "blackboard"
        prior = self.previous_returns("control", iteration)
        prior["initial_criteria"] = self.config.get("initial_conditions", {}).get("control_criteria") or (ROOT / "conditions/control/working-agreement-v0.md").read_text()
        feedback: dict[str, Any] | None = None
        maximum = int(self.config["budget"].get("max_control_cycles", 2))
        for cycle in range(maximum):
            def validate_candidate(output: dict[str, Any]) -> None:
                self.validate_complete_output(output)
            candidate = self.validated_call("control", iteration, "optimizer", {"iteration": iteration, "blackboard": prior, "evaluator_feedback": feedback, "private_expertise": (ROOT / "conditions/control/private/optimizer.md").read_text()}, budget, iteration_dir / f"calls/optimizer-{cycle}", validate_candidate)
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
            evaluation = self.validated_call("control", iteration, "evaluator", {"iteration": iteration, "candidate": package, "candidate_id": candidate_id, "rationale": candidate["notes"], "blackboard": prior, "private_expertise": (ROOT / "conditions/control/private/evaluator.md").read_text()}, budget, iteration_dir / f"calls/evaluator-{cycle}", validate_evaluation)
            write_json(blackboard / f"evaluation-{cycle}.json", evaluation)
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
        write_json(approved / "approval.json", evaluation)
        atomic_write(approved / "candidate-hash.txt", candidate_id + "\n")
        write_manifest(approved, "entity1", ["candidate", "approval.json", "candidate-hash.txt"], [str(candidate_dir.relative_to(iteration_dir))])
        if digest(package) != candidate_id:
            raise RuntimeError("approved candidate changed")
        return package

    def previous_returns(self, condition: str, iteration: int) -> dict[str, Any]:
        if iteration == 0:
            return {"race_data_for_geometry": None, "integration_feedback": None, "race_data_for_integration": None}
        previous = self.run_root / condition / f"iteration-{iteration - 1}"
        result: dict[str, Any] = {}
        for key, directory in (("race_data_for_geometry", "return-geometry"), ("race_data_for_integration", "return-integration"), ("integration_feedback", "entityR1")):
            path = previous / directory / ("measurements.json" if key.startswith("race_data") else "feedback.json")
            result[key] = read_json(path) if path.exists() else None
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
                    trajectory_svg({**trial, "telemetry": telemetry}, trial_dir / "trajectory.svg")
                    write_json(result_path, trial)
                    self.audit(condition, iteration, "trial_complete", {"trial_id": trial_id, "artifact_hash": digest(trial), "simulator_version": ADAPTER_VERSION})
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
                        trajectory_svg({**trial, "telemetry": telemetry}, trial_dir / "trajectory.svg")
                        write_json(result_path, trial)
                        self.audit(condition, iteration, "held_out_trial_complete", {"trial_id": trial_id, "artifact_hash": digest(trial), "simulator_version": ADAPTER_VERSION})
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
        for recipient in ("geometry", "integration"):
            target = iteration_dir / f"return-{recipient}"
            write_json(target / "measurements.json", measurements)
            atomic_write(target / "measurement-catalogue-version", self.config["simulator"]["measurement_catalogue_version"] + "\n")
            atomic_write(target / "source-run-id", self.config["experiment_id"] + "\n")
            write_json(target / "source-trial-ids", source_trials)
            requested = package["observation_request"]["measurements"]
            write_json(target / "request-coverage.json", {"requested": requested, "supplied": [item for item in requested if item in measurements]})
        if condition == "loopsense":
            def validate_feedback(output: dict[str, Any]) -> None:
                if not isinstance(output.get("summary"), str) or not isinstance(output.get("requests"), list):
                    raise ValidationError("integration feedback requires a string summary and a list of requests")
            feedback = self.validated_call(condition, iteration, "integration_feedback", {"iteration": iteration, "race_data_for_integration": measurements, "geometry": package["geometry"]}, budget, iteration_dir / "calls/integration-feedback", validate_feedback)
            write_json(iteration_dir / "entityR1/feedback.json", feedback)
            write_manifest(iteration_dir / "entityR1", "entityR1", ["feedback.json"], ["return-integration"])
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
        if self.resume and existing_manifest.exists():
            frozen = read_json(existing_manifest)
            if frozen.get("config_hash") != digest(self.config):
                raise RuntimeError("resume configuration differs from the frozen run configuration")
            if frozen.get("plan_hash") != digest((ROOT / "IMPLEMENTATION_PLAN.md").read_bytes()):
                raise RuntimeError("resume implementation plan differs from the frozen run plan")
        write_json(self.run_root / "manifest.json", {"experiment_id": self.config["experiment_id"], "config": self.config, "config_hash": digest(self.config), "plan_hash": digest((ROOT / "IMPLEMENTATION_PLAN.md").read_bytes()), "status": "running"})
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
                    saved_budget = read_json(checkpoint)["budget"]
                    budget.used = max(budget.used, int(saved_budget["used"]))
                    self.results.append(read_json(iteration_dir / "entity2/result.json"))
                    continue
                self.audit(condition, iteration, "iteration_started", {"simulator_version": self.config["simulator"]["version"]})
                package = self.loopsense_build(iteration_dir, iteration, budget) if condition == "loopsense" else self.control_build(iteration_dir, iteration, budget)
                result = self.evaluate(condition, iteration, iteration_dir, package, budget)
                public_base = self.config["publication"]["base_url"].rstrip("/") + f"/{self.config['experiment_id']}"
                initial_key = "loopsense_working_agreement" if condition == "loopsense" else "control_criteria"
                setup_notes = self.config.get("initial_conditions", {}).get(initial_key, "See the frozen race manifest.")
                scenario = scenario_yaml("base.yaml", condition, iteration, f"{public_base}/{condition}/iteration-{iteration}/entity2/iteration-summary.svg", f"{public_base}/leaderboard.svg", result, setup_notes)
                atomic_write(iteration_dir / "scenario.yaml", scenario)
                atomic_write(maps_root / ("loopsense" if condition == "loopsense" else "control") / f"iteration-{iteration}.yaml", scenario)
                write_json(checkpoint, {"complete": True, "result_hash": result["artifact_hash"], "budget": budget.record()})
                self.audit(condition, iteration, "iteration_complete", {"artifact_hash": result["artifact_hash"], "token_usage": budget.iteration_used, "validation": "valid", "simulator_version": self.config["simulator"]["version"]})
                self.results.append(result)
        leaderboard(self.run_root, self.results)
        manifest = read_json(self.run_root / "manifest.json")
        manifest["status"] = "complete"
        manifest["result_hashes"] = [result["artifact_hash"] for result in self.results]
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
