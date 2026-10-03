from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from orchestrator.artifacts import leaderboard, scenario_yaml
from orchestrator.io import digest, safe_child
from orchestrator.runner import Budget, ExperimentRunner, ROOT, initialise_race, validate_config
from orchestrator.validators import ValidationError, validate_measurement_request, validate_observation, validate_package
from simulator.adapter import run_trial


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / "config/experiment.yaml").read_text())
        cls.package = {
            "geometry": {"sensor_positions": [{"x": x, "y": 0.05} for x in (-0.06, -0.03, 0, 0.03, 0.06)], "sensor_size": 0.012, "wheel_track": 0.12, "wheel_radius": 0.035, "body_width": 0.12, "body_length": 0.16, "mass": 0.8},
            "controller": {"base_speed": 0.42, "kp": 4.2, "ki": 0.03, "kd": 0.9, "sensor_weights": [-1, -0.5, 0, 0.5, 1], "line_loss": "last_direction"},
            "observation_request": {"measurements": ["completion", "progress"]},
        }
        cls.track = json.loads((ROOT / "tracks/anchor/oval.json").read_text())

    def test_configuration_and_package_validate(self) -> None:
        validate_config(self.config)
        validate_package(self.package, self.config["design_bounds"])

    def test_geometry_bounds_are_enforced(self) -> None:
        invalid = deepcopy(self.package)
        invalid["geometry"]["wheel_track"] = 9
        with self.assertRaises(ValidationError):
            validate_package(invalid, self.config["design_bounds"])

    def test_measurements_are_allowlisted(self) -> None:
        with self.assertRaises(ValidationError):
            validate_measurement_request({"measurements": ["read_arbitrary_file"]})

    def test_pose_is_not_an_observation(self) -> None:
        with self.assertRaises(ValidationError):
            validate_observation({"sensors": [1], "heading": 1.2})

    def test_seed_is_deterministic_and_distinct_seeds_vary(self) -> None:
        first = run_trial(self.package, self.track, 17, self.config)
        repeated = run_trial(self.package, self.track, 17, self.config)
        other = run_trial(self.package, self.track, 29, self.config)
        self.assertEqual(first, repeated)
        self.assertNotEqual(first["telemetry"], other["telemetry"])

    def test_invalid_design_classification(self) -> None:
        invalid = deepcopy(self.package)
        invalid["geometry"]["sensor_positions"] = []
        self.assertEqual(run_trial(invalid, self.track, 1, self.config)["termination_reason"], "invalid_design")

    def test_finish_off_track_timeout_and_controller_error_classification(self) -> None:
        self.assertEqual(run_trial(self.package, self.track, 17, self.config)["termination_reason"], "finished")
        off_track = deepcopy(self.package)
        for sensor in off_track["geometry"]["sensor_positions"]:
            sensor["x"] = 0
        off_track["controller"].update({"base_speed": 2, "kp": 0, "kd": 0})
        self.assertEqual(run_trial(off_track, self.track, 17, self.config)["termination_reason"], "off_track")
        timeout = deepcopy(self.package)
        for sensor, x in zip(timeout["geometry"]["sensor_positions"], (-0.02, -0.01, 0, 0.01, 0.02)):
            sensor["x"] = x
        timeout["controller"].update({"base_speed": 1.7, "kp": 0, "kd": 0})
        timeout_result = run_trial(timeout, self.track, 17, self.config)
        self.assertEqual(timeout_result["termination_reason"], "timeout")
        broken = deepcopy(self.package)
        broken["controller"]["sensor_weights"] = [0, 0, 0, 0, 0]
        self.assertEqual(run_trial(broken, self.track, 17, self.config)["termination_reason"], "controller_error")

    def test_paths_cannot_escape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                safe_child(root, "..", "escape")

    def test_budget_hard_stop(self) -> None:
        from orchestrator.model_client import ModelResponse
        budget = Budget(3, 3)
        with self.assertRaises(RuntimeError):
            budget.charge(ModelResponse({}, "id", 2, 2))

    def test_race_definition_is_created_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = initialise_race("race-7", root)
            self.assertEqual(json.loads(path.read_text())["experiment_id"], "race-7")
            with self.assertRaises(FileExistsError):
                initialise_race("race-7", root)
            with self.assertRaises(ValueError):
                initialise_race("../escape", root)

    def test_publication_rejects_local_urls(self) -> None:
        with self.assertRaises(ValueError):
            scenario_yaml("base.yaml", "loopsense", 0, "/tmp/a.svg", "https://example/a.svg", {"score": 1})

    def test_leaderboard_rejects_tampered_result(self) -> None:
        result = {"condition": "loopsense", "iteration": 0, "score": 1.0, "trials": [], "aggregate": {}}
        result["artifact_hash"] = digest(result)
        result["score"] = 2.0
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            leaderboard(Path(directory), [result])

    def test_smoke_run_and_resume_do_not_duplicate_calls(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = deepcopy(self.config)
            config["experiment_id"] = "test"
            config["iterations"] = 1
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config))
            output = Path(directory) / "runs"
            run_root = ExperimentRunner(config_path, output).run()
            calls_before = len(list(run_root.glob("**/response.json")))
            lines_before = len((run_root / "audit.jsonl").read_text().splitlines())
            ExperimentRunner(config_path, output, resume=True).run()
            self.assertEqual(calls_before, len(list(run_root.glob("**/response.json"))))
            self.assertEqual(lines_before, len((run_root / "audit.jsonl").read_text().splitlines()))
            self.assertEqual(json.loads((run_root / "manifest.json").read_text())["status"], "complete")


if __name__ == "__main__":
    unittest.main()
