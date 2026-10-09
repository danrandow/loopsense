from __future__ import annotations

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path

from orchestrator.artifacts import track_view_svg
from orchestrator.io import digest, safe_child
from orchestrator.validators import ValidationError, validate_measurement_request, validate_observation, validate_package
from simulator.adapter import ADAPTER_VERSION, run_trial, to_robottrace_spec


ROOT = Path(__file__).resolve().parents[1]


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


















if __name__ == "__main__":
    unittest.main()
