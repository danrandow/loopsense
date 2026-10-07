from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

from orchestrator.artifacts import leaderboard, race_report, scenario_yaml, track_view_svg
from orchestrator.io import digest, safe_child
from orchestrator.model_client import ModelResponse
from orchestrator.runner import Budget, ExperimentRunner, ROOT, initialise_race, publish_race_scenarios, validate_config
from orchestrator.validators import MEASUREMENTS, ValidationError, validate_geometry, validate_measurement_request, validate_observation, validate_package
from simulator.adapter import ADAPTER_VERSION, run_trial, to_robottrace_spec


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
        self.assertEqual(first["adapter_version"], ADAPTER_VERSION)
        self.assertEqual(first["run_id"], repeated["run_id"])

    def test_canonical_package_translates_to_robottrace_without_duplication(self) -> None:
        spec = to_robottrace_spec(self.package)
        self.assertEqual(spec["geometric_mechanical"]["track_mm"], 120.0)
        self.assertEqual(spec["geometric_mechanical"]["wheel_radius_mm"], 35.0)
        self.assertEqual(spec["sensors"][0]["yMM"], -60.0)
        self.assertEqual(spec["sensors"][0]["xMM"], 50.0)
        self.assertEqual(spec["controller"]["policy"], self.package["controller"])
        spec["controller"]["policy"]["kp"] = 999
        self.assertEqual(self.package["controller"]["kp"], 4.2)

    def test_maximum_step_count_forces_timeout(self) -> None:
        config = deepcopy(self.config)
        config["simulator"]["max_steps"] = 5
        result = run_trial(self.package, self.track, 17, config)
        self.assertEqual(result["termination_reason"], "timeout")
        self.assertEqual(len(result["telemetry"]), 5)

    def test_track_view_is_deterministic_safe_and_complete(self) -> None:
        trial = run_trial(self.package, self.track, 17, self.config)
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.svg"
            second = Path(directory) / "second.svg"
            args = dict(experiment="race-test", condition="loopsense", iteration=2)
            track_view_svg(trial, self.package, self.track, first, **args)
            track_view_svg(trial, self.package, self.track, second, **args)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            source = first.read_text()
            self.assertNotIn("<script", source.lower())
            self.assertNotIn("foreignObject", source)
            self.assertNotIn("http://", source.replace("http://www.w3.org/2000/svg", ""))
            root = ET.fromstring(source)
            namespace = {"svg": "http://www.w3.org/2000/svg"}
            ids = [child.attrib.get("id") for child in root if child.tag.endswith("g")]
            self.assertEqual(ids, [
                "background", "track-envelope", "track-centreline", "start-finish",
                "trajectory", "robot-snapshots", "events", "legend", "trial-metadata",
            ])
            metadata_node = root.find("svg:metadata", namespace)
            self.assertIsNotNone(metadata_node)
            metadata = json.loads(metadata_node.text)
            self.assertEqual(metadata["package_hash"], digest(self.package))
            self.assertEqual(metadata["track_hash"], digest(self.track))
            self.assertEqual(metadata["telemetry_hash"], digest(trial["telemetry"]))
            self.assertEqual(metadata["termination_reason"], trial["termination_reason"])
            self.assertEqual(set(metadata["snapshot_steps"]), {"start", "25%", "50%", "75%", "finish"})
            self.assertIn('class="body"', source)
            self.assertIn('class="wheel left"', source)
            self.assertIn('class="sensor"', source)
            self.assertIn('data-error-band="green"', source)
            self.assertIn('data-event="finish-crossing"', source)

    def test_completed_iteration_backfills_missing_track_views(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = deepcopy(self.config)
            config["experiment_id"] = "repair-test"
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config))
            runner = ExperimentRunner(config_path, root / "runs")
            iteration_dir = runner.run_root / "loopsense/iteration-0"
            package_dir = iteration_dir / "entity1"
            package_dir.mkdir(parents=True)
            (package_dir / "geometry.json").write_text(json.dumps(self.package["geometry"]))
            (package_dir / "controller.json").write_text(json.dumps(self.package["controller"]))
            (package_dir / "observation-request.json").write_text(json.dumps(self.package["observation_request"]))
            trial = run_trial(self.package, self.track, 17, config)
            telemetry = trial.pop("telemetry")
            trial_dir = iteration_dir / "entity2/trials/oval-17"
            trial_dir.mkdir(parents=True)
            (trial_dir / "result.json").write_text(json.dumps(trial))
            (trial_dir / "telemetry.json").write_text(json.dumps(telemetry))

            runner.ensure_track_views("loopsense", 0, iteration_dir)

            view = trial_dir / "track-view.svg"
            self.assertTrue(view.exists())
            self.assertIn("robotrace-track-view-v1", view.read_text())

    def test_track_view_has_timeout_and_off_track_markers(self) -> None:
        timeout_config = deepcopy(self.config)
        timeout_config["simulator"]["max_steps"] = 5
        timeout = run_trial(self.package, self.track, 17, timeout_config)
        off_track_package = deepcopy(self.package)
        for sensor in off_track_package["geometry"]["sensor_positions"]:
            sensor["x"] = 0
        off_track_package["controller"].update({"base_speed": 2, "kp": 0, "kd": 0})
        off_track = run_trial(off_track_package, self.track, 17, self.config)
        with tempfile.TemporaryDirectory() as directory:
            timeout_path = Path(directory) / "timeout.svg"
            off_track_path = Path(directory) / "off-track.svg"
            track_view_svg(timeout, self.package, self.track, timeout_path, experiment="test", condition="control", iteration=0)
            track_view_svg(off_track, off_track_package, self.track, off_track_path, experiment="test", condition="control", iteration=0)
            self.assertIn('data-event="timeout"', timeout_path.read_text())
            self.assertIn('data-event="off-track"', off_track_path.read_text())

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
        timeout_config = deepcopy(self.config)
        timeout_config["simulator"]["max_steps"] = 5
        timeout_result = run_trial(self.package, self.track, 17, timeout_config)
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
        budget = Budget(3, 3)
        with self.assertRaises(RuntimeError):
            budget.charge(ModelResponse({}, "id", 2, 2))

    def test_constraints_are_supplied_and_one_repair_is_bounded_and_charged(self) -> None:
        invalid = {
            "geometry": {**self.package["geometry"], "sensor_positions": [{"x": 9, "y": 0.05}] * 5},
            "intent": "invalid first attempt",
            "feedback_request": {"measurements": ["completion"], "questions": []},
            "learning": "invalid attempt",
        }
        valid = {
            "geometry": deepcopy(self.package["geometry"]),
            "intent": "valid repaired attempt",
            "feedback_request": {"measurements": ["completion"], "questions": []},
            "learning": "valid repaired learning",
        }

        class ScriptedClient:
            def __init__(self) -> None:
                self.outputs = [invalid, valid]
                self.contexts: list[dict] = []

            def call(self, actor: str, context: dict) -> ModelResponse:
                self.contexts.append(context)
                return ModelResponse(self.outputs.pop(0), f"request-{len(self.contexts)}", 10, 10)

        with tempfile.TemporaryDirectory() as directory:
            config = deepcopy(self.config)
            config["experiment_id"] = "repair-test"
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config))
            runner = ExperimentRunner(config_path, Path(directory) / "runs")
            client = ScriptedClient()
            runner.client = client
            budget = Budget(1000, 1000)

            def validator(output: dict) -> None:
                validate_geometry(output["geometry"], config["design_bounds"])
                validate_measurement_request(output["feedback_request"])

            result = runner.validated_call("loopsense", 0, "geometry_builder", {"iteration": 0}, budget, runner.run_root / "call", validator)
            self.assertEqual(result, valid)
            self.assertEqual(budget.used, 40)
            self.assertEqual(client.contexts[0]["constraints"]["design_bounds"], config["design_bounds"])
            self.assertEqual(client.contexts[0]["constraints"]["supported_measurements"], sorted(MEASUREMENTS))
            self.assertEqual(client.contexts[1]["invalid_artifact"], invalid)
            self.assertIn("sensor 0 x", client.contexts[1]["validation_errors"][0])

    def test_terminal_invalid_artifact_marks_run_failed(self) -> None:
        invalid = {
            "geometry": {**self.package["geometry"], "body_length": 9},
            "intent": "still invalid",
            "feedback_request": {"measurements": ["completion"], "questions": []},
            "learning": "still invalid",
        }

        class InvalidClient:
            calls = 0

            def call(self, actor: str, context: dict) -> ModelResponse:
                self.calls += 1
                return ModelResponse(invalid, f"invalid-{self.calls}", 10, 10)

        with tempfile.TemporaryDirectory() as directory:
            config = deepcopy(self.config)
            config.update({"experiment_id": "failed-test", "iterations": 1})
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config))
            runner = ExperimentRunner(config_path, Path(directory) / "runs")
            client = InvalidClient()
            runner.client = client
            with self.assertRaises(ValidationError):
                runner.run()
            manifest = json.loads((runner.run_root / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "failed")
            self.assertEqual(manifest["failed_actor"], "geometry_builder")
            self.assertEqual(client.calls, 2)
            self.assertIn("run_failed", (runner.run_root / "audit.jsonl").read_text())

    def test_complete_output_reports_geometry_and_controller_errors_together(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = deepcopy(self.config)
            config["experiment_id"] = "aggregate-errors"
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config))
            runner = ExperimentRunner(config_path, Path(directory) / "runs")
            malformed = {
                "geometry": {"sensor_count": 5, "sensor_positions": [[0, 0]]},
                "controller": {"sensor_weight": 1},
                "observation_request": {"measurements": ["completion"], "questions": []},
                "notes": "malformed",
            }
            with self.assertRaises(ValidationError) as raised:
                runner.validate_complete_output(malformed)
            self.assertIn("geometry:", str(raised.exception))
            self.assertIn("controller:", str(raised.exception))
            self.assertIn("sensor_weights", str(raised.exception))

    def test_config_rejects_unknown_measurement_catalogue_and_impossible_iteration_budget(self) -> None:
        invalid = deepcopy(self.config)
        invalid["simulator"]["measurement_catalogue_version"] = "unknown"
        with self.assertRaises(ValueError):
            validate_config(invalid)
        invalid = deepcopy(self.config)
        invalid["budget"].update({"total_tokens_per_condition": 100, "max_tokens_per_iteration": 101})
        with self.assertRaises(ValueError):
            validate_config(invalid)

    def test_race_definition_is_created_once(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = initialise_race("race-7", root)
            self.assertEqual(json.loads(path.read_text())["experiment_id"], "race-7")
            with self.assertRaises(FileExistsError):
                initialise_race("race-7", root)
            with self.assertRaises(ValueError):
                initialise_race("../escape", root)

    def test_scenario_uses_local_artifact_links_as_a_markdown_list(self) -> None:
        scenario = scenario_yaml(
            "base.yaml", "loopsense", 0,
            "runs/race-7/loopsense/iteration-0/entity2/iteration-summary.svg",
            "runs/race-7/leaderboard.svg", {"score": 1}, "",
            [("anchor: oval-17 track view", "runs/race-7/loopsense/iteration-0/entity2/trials/oval-17/track-view.svg")],
        )
        self.assertIn("notes: |", scenario)
        self.assertIn("- [Open iteration race summary](runs/race-7/", scenario)
        self.assertIn("- [anchor: oval-17 track view](runs/race-7/", scenario)
        self.assertNotIn("github.com", scenario)

    def test_scenario_links_race_report_after_initial_conditions(self) -> None:
        scenario = scenario_yaml(
            "base.yaml", "loopsense", 0,
            "runs/race-7/loopsense/iteration-0/entity2/iteration-summary.svg",
            "runs/race-7/leaderboard.svg", {"score": 1}, "frozen setup",
            race_report_url="runs/race-7/race-report.md",
        )
        setup = scenario.index("frozen setup")
        report = scenario.index("[Read the race report](runs/race-7/race-report.md)")
        overrides = scenario.index("overrides:")
        self.assertLess(setup, report)
        self.assertLess(report, overrides)

    def test_race_report_covers_both_teams_and_repository_changes(self) -> None:
        results = [
            {"condition": "loopsense", "iteration": 0, "score": 10},
            {"condition": "control", "iteration": 0, "score": 12},
            {"condition": "loopsense", "iteration": 1, "score": 15, "held_out": {"score": 14}},
            {"condition": "control", "iteration": 1, "score": 13, "held_out": {"score": 11}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            race_report(path, "race-7", results, {"conditions": ["loopsense", "control"]}, [{
                "subject": "Improve harness", "short_hash": "abc1234",
                "url": "https://github.com/example/repo/commit/abc1234",
            }], "race-6")
            report = (path / "race-report.md").read_text()
            self.assertIn("loopsense finished ahead of control by 2.000 points", report)
            self.assertIn("| loopsense | 10.000 | 15.000 | 15.000 | 14.000 |", report)
            self.assertIn("Repository changes since race-6 completed", report)
            self.assertIn("[Improve harness](https://github.com/example/repo/commit/abc1234)", report)

    def test_scenario_uses_maps_override_schema(self) -> None:
        scenario = scenario_yaml(
            "base.yaml", "loopsense", 2,
            "runs/race-7/loopsense/iteration-2/entity2/iteration-summary.svg",
            "runs/race-7/leaderboard.svg",
            {"score": 12.5}, "agreement",
        )
        self.assertIn("id: iteration-7.2", scenario)
        self.assertIn('inherits: "base.yaml"', scenario)
        self.assertIn('scenario: "Race 7 iteration 2"', scenario)
        self.assertIn("overrides:\n  entities:\n    - id: entity2", scenario)
        self.assertNotIn("ANALYSIS.md", scenario)
        self.assertNotIn("extends:", scenario)

    def test_completed_race_publishes_one_final_scenario_per_team(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_root = root / "runs/race-5"
            roots = {"loopsense": root / "robotrace", "control": root / "robotrace-control"}
            for condition in roots:
                source = run_root / "maps" / condition / "iteration-1.yaml"
                source.parent.mkdir(parents=True)
                source.write_text(f'map:\n  scenario: "Race 5 iteration 1"\n  notes: {condition} final\n')
            published = publish_race_scenarios(run_root, "race-5", 2, roots)
            self.assertIn('scenario: "Race 5"', (roots["loopsense"] / "iteration-5.yaml").read_text())
            self.assertIn('scenario: "Race 5"', (roots["control"] / "iteration-5.yaml").read_text())
            self.assertEqual(published, {condition: root / f"{'robotrace' if condition == 'loopsense' else 'robotrace-control'}/iteration-5.yaml" for condition in roots})
            self.assertEqual(publish_race_scenarios(run_root, "race-5", 2, roots), published)
            (run_root / "maps/loopsense/iteration-1.yaml").write_text("scenario: changed\n")
            self.assertEqual(publish_race_scenarios(run_root, "race-5", 2, roots), published)
            self.assertIn('scenario: "Race 5"', (roots["loopsense"] / "iteration-5.yaml").read_text())

    def test_non_numbered_run_does_not_publish_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(publish_race_scenarios(Path(directory), "robotrace-smoke", 1), {})

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
            final_result = json.loads((run_root / "loopsense/iteration-0/entity2/result.json").read_text())
            self.assertEqual({trial["track"] for trial in final_result["held_out"]["trials"]}, {"hairpin"})
            for manifest in run_root.glob("**/context-manifest.json"):
                self.assertNotIn("held_out_tracks", json.loads(manifest.read_text())["keys"])
            calls_before = len(list(run_root.glob("**/response.json")))
            lines_before = len((run_root / "audit.jsonl").read_text().splitlines())
            ExperimentRunner(config_path, output, resume=True).run()
            self.assertEqual(calls_before, len(list(run_root.glob("**/response.json"))))
            self.assertEqual(lines_before, len((run_root / "audit.jsonl").read_text().splitlines()))
            self.assertEqual(json.loads((run_root / "manifest.json").read_text())["status"], "complete")


if __name__ == "__main__":
    unittest.main()
