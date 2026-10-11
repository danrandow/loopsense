"""Adapter v2: disturbance independent of the design, body size affects yaw inertia, time term scaled to the run cap."""
from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

import yaml

from simulator.adapter import ADAPTER_VERSION, run_trial
from simulator.adapter.headless import DT, score_description

ROOT = Path(__file__).resolve().parents[1]
DESIGN = {
    "geometry": {"sensor_positions": [{"x": -0.05, "y": 0.04}, {"x": -0.025, "y": 0.04}, {"x": 0.0, "y": 0.05}, {"x": 0.025, "y": 0.04}, {"x": 0.05, "y": 0.04}],
                 "sensor_size": 0.016, "wheel_track": 0.14, "wheel_radius": 0.035, "body_width": 0.12, "body_length": 0.18, "mass": 0.8},
    "controller": {"base_speed": 1.3, "kp": 5.0, "ki": 0.5, "kd": 4.0, "line_loss": "search_left", "sensor_weights": [-1.5, -0.75, 0, 0.75, 1.5]},
    "observation_request": {"measurements": ["completion"]},
}


class SimValidityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / "config/experiment.yaml").read_text())
        cls.config["simulator"].update({"max_steps": 300, "stall_steps": 50, "stall_min_progress": 0.002})
        cls.track = json.loads((ROOT / "tracks/development/s-bend.json").read_text())

    def run_design(self, design, seed=41):
        return run_trial(design, self.track, seed, self.config)

    def test_version_is_v2(self) -> None:
        self.assertEqual(ADAPTER_VERSION, "robottracesim-native-v2")

    def test_disturbance_does_not_depend_on_the_design(self) -> None:
        other = deepcopy(DESIGN)
        other["observation_request"] = {"measurements": ["completion", "progress", "rms_error"]}
        a, b = self.run_design(DESIGN), self.run_design(other)
        self.assertNotEqual(a["run_id"], b["run_id"])
        self.assertEqual(a["telemetry"], b["telemetry"])
        self.assertEqual(a["score"], b["score"])

    def test_disturbance_still_varies_with_the_seed(self) -> None:
        self.assertNotEqual(self.run_design(DESIGN, 41)["telemetry"], self.run_design(DESIGN, 42)["telemetry"])

    def test_body_size_changes_the_outcome(self) -> None:
        big = deepcopy(DESIGN)
        big["geometry"].update(body_width=0.18, body_length=0.24)
        self.assertNotEqual(self.run_design(DESIGN)["telemetry"], self.run_design(big)["telemetry"])

    def test_time_term_is_scaled_to_the_run_cap(self) -> None:
        text = score_description({"completion": 500, "progress": 250, "robustness": 120, "time": 60, "precision": 70}, {"max_steps": 300})
        self.assertIn(f"completion_time/{300 * DT:g}", text)


if __name__ == "__main__":
    unittest.main()
