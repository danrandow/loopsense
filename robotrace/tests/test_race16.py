"""Race-16 harness changes: progress-gated scoring, stall ending, full evidence in R2A/R2B, objective in the prompt."""
from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import yaml

from orchestrator.executors import PackageExecutor, compact_telemetry, objective_for_prompt
from simulator.adapter import run_trial
from simulator.adapter.headless import _score, score_description


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "package-templates"
WEIGHTS = {"completion": 500, "progress": 250, "robustness": 120, "time": 60, "precision": 70}

# Design from race 15 (randow-maps, iteration 1): the line is lost at the start, and "stop" never moves.
STATIONARY = {
    "geometry": {"sensor_positions": [{"x": -0.05, "y": 0.05}, {"x": 0.05, "y": 0.05}, {"x": 0.0, "y": -0.05}], "sensor_size": 0.012, "wheel_track": 0.1, "wheel_radius": 0.04, "body_width": 0.15, "body_length": 0.2, "mass": 1.0},
    "controller": {"base_speed": 0.5, "kp": 1.0, "ki": 0.1, "kd": 0.01, "sensor_weights": [1.0, 1.0, 1.0], "line_loss": "stop"},
    "observation_request": {"measurements": ["completion", "progress"]},
}


def template_race(name: str) -> dict:
    return yaml.safe_load((TEMPLATES / name / "config/race.yaml").read_text())


class ScoreTests(unittest.TestCase):
    def metrics(self, **overrides):
        base = {"completion": False, "progress": 0.0, "completion_time": 3.0, "rms_error": 0.0, "line_loss_events": 1}
        return {**base, **overrides}

    def test_robot_that_does_not_move_scores_zero(self) -> None:
        self.assertEqual(_score(self.metrics(), WEIGHTS), 0.0)

    def test_moving_and_failing_beats_not_moving(self) -> None:
        failing = _score(self.metrics(progress=0.02, rms_error=0.025, line_loss_events=2), WEIGHTS)
        self.assertGreater(failing, 0.0)
        self.assertLess(failing, 20.0)

    def test_completed_run_keeps_the_ungated_formula(self) -> None:
        metrics = self.metrics(completion=True, progress=1.0, completion_time=30.0, rms_error=0.015, line_loss_events=0)
        expected = 500 + 250 + 120 * 1 + 60 * 0.5 + 70 * 0.9
        self.assertAlmostEqual(_score(metrics, WEIGHTS), expected, places=6)

    def test_description_is_generated_from_the_weights(self) -> None:
        text = score_description({**WEIGHTS, "completion": 777}, {"max_steps": 300, "stall_steps": 50, "stall_min_progress": 0.002})
        self.assertIn("777*completed", text)
        self.assertIn("stalls", text)
        self.assertIn("300 steps", text)


class StallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((ROOT / "config/experiment.yaml").read_text())
        cls.config["simulator"].update({"max_steps": 300, "stall_steps": 50, "stall_min_progress": 0.002})
        cls.track = json.loads((ROOT / "tracks/anchor/oval.json").read_text())

    def test_stationary_robot_ends_early_and_scores_zero(self) -> None:
        result = run_trial(STATIONARY, self.track, 17, self.config)
        self.assertEqual(result["termination_reason"], "stalled")
        self.assertEqual(len(result["telemetry"]), 51)
        self.assertEqual(result["score"], 0.0)

    def test_without_stall_detection_it_times_out_but_still_scores_zero(self) -> None:
        config = deepcopy(self.config)
        config["simulator"]["stall_steps"] = 0
        result = run_trial(STATIONARY, self.track, 17, config)
        self.assertEqual(result["termination_reason"], "timeout")
        self.assertEqual(len(result["telemetry"]), 300)
        self.assertEqual(result["score"], 0.0)

    def test_a_robot_that_follows_the_line_is_not_stalled(self) -> None:
        moving = {
            "geometry": {"sensor_positions": [{"x": x, "y": 0.05} for x in (-0.06, -0.03, 0, 0.03, 0.06)], "sensor_size": 0.012, "wheel_track": 0.12, "wheel_radius": 0.035, "body_width": 0.12, "body_length": 0.16, "mass": 0.8},
            "controller": {"base_speed": 0.42, "kp": 4.2, "ki": 0.03, "kd": 0.9, "sensor_weights": [-1, -0.5, 0, 0.5, 1], "line_loss": "last_direction"},
            "observation_request": {"measurements": ["completion"]},
        }
        config = deepcopy(self.config)
        config["simulator"]["max_steps"] = 1200
        self.assertEqual(run_trial(moving, self.track, 17, config)["termination_reason"], "finished")


class EvidenceTests(unittest.TestCase):
    def test_r2a_and_r2b_carry_full_trials_and_entity2_stays_minimal(self) -> None:
        race = template_race("randow-maps")
        race["design_bounds"] = json.loads((ROOT / "config/experiment.yaml").read_text())["design_bounds"]
        contracts = {e: json.loads((TEMPLATES / "randow-maps/entities" / e / "contract.schema.json").read_text()) for e in ("entity2", "entityR2A", "entityR2B")}
        package = SimpleNamespace(race=race, contract=lambda entity: contracts.get(entity))
        action = SimpleNamespace(writes={"entity2", "entityR2A", "entityR2B"})
        result = PackageExecutor(package)._simulator(action, {"entity1": STATIONARY}, {})
        self.assertEqual(set(result.writes["entity2"]), {"score", "trials"})
        for entity in ("entityR2A", "entityR2B"):
            self.assertEqual(set(result.writes[entity]), {"summary", "score", "trials"})
            self.assertEqual(result.writes[entity]["trials"][0]["telemetry"], result.writes["entity2"]["trials"][0]["telemetry"])
            self.assertEqual(result.writes[entity]["trials"][0]["termination_reason"], "stalled")

    def test_both_templates_require_trials_in_race_data(self) -> None:
        for template in ("randow-maps", "opt-eval"):
            for entity in ("entityR2A", "entityR2B"):
                contract = json.loads((TEMPLATES / template / "entities" / entity / "contract.schema.json").read_text())
                self.assertIn("trials", contract["required"])
                self.assertIn("trials", contract["properties"])


class PromptTests(unittest.TestCase):
    def test_compact_telemetry_is_lossless_apart_from_the_boolean_flag(self) -> None:
        telemetry = [{"step": i, "progress": i / 100, "error": 0.001 * i, "speed": 0.1 * i, "x": 0.01 * i, "y": -0.001 * i, "heading": 0.0, "sensors": [0.0, 0.5, 0.1], "line_lost": i % 2 == 0} for i in range(5)]
        packed, found = compact_telemetry({"trials": [{"score": 1, "telemetry": telemetry}]})
        self.assertTrue(found)
        table = packed["trials"][0]["telemetry"]
        rebuilt = [{"step": i, **dict(zip(table["columns"], row))} for i, row in enumerate(table["rows"])]
        for original, got in zip(telemetry, rebuilt):
            self.assertEqual({**original, "line_lost": int(original["line_lost"])}, got)
        self.assertLess(len(json.dumps(packed, separators=(",", ":"))), len(json.dumps(telemetry, separators=(",", ":"))))

    def test_inputs_without_telemetry_are_unchanged(self) -> None:
        payload = {"entity0": {"geometry": {"mass": 1.0}}}
        self.assertEqual(compact_telemetry(payload), (payload, False))

    def test_every_template_tells_agents_the_objective_without_naming_held_out_tracks(self) -> None:
        for template in ("randow-maps", "opt-eval"):
            race = template_race(template)
            objective = objective_for_prompt(race)
            text = json.dumps(objective)
            self.assertIn("maximise", objective["goal"])
            self.assertIn("unseen", objective["goal"])
            self.assertIn("progress*(", objective["scoring"])
            self.assertEqual(objective["development_tracks"], race["evaluation"]["development_tracks"])
            for held_out in race["evaluation"]["held_out_tracks"]:
                self.assertNotIn(held_out, text)

    def test_templates_agree_on_objective_and_stall_settings(self) -> None:
        first, second = template_race("randow-maps"), template_race("opt-eval")
        for key in ("objective", "score", "simulator", "budget", "iterations", "evaluation"):
            self.assertEqual(first[key], second[key], key)
        self.assertGreater(first["simulator"]["stall_steps"], 0)

    def test_no_objective_block_means_nothing_is_added(self) -> None:
        race = template_race("randow-maps")
        race.pop("objective")
        self.assertIsNone(objective_for_prompt(race))


if __name__ == "__main__":
    unittest.main()
