"""Replicate races: distinct development seeds, shared held-out seeds, and a comparison across them."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import replicates  # noqa: E402


class ReplicateTests(unittest.TestCase):
    def test_mock_replicates_use_own_dev_seed_and_shared_held_out_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            replicates.run(argparse.Namespace(base="rep", n=2, iterations=2, provider="mock", model="deterministic-mock-v1", max_output_tokens=700,
                                              total_tokens=900000, iteration_tokens=300000, workspace=workspace))
            for race, seed in (("rep-a", 17), ("rep-b", 29)):
                for entrant in replicates.ENTRANTS:
                    package = workspace / f"{race}-{entrant}"
                    trials = json.loads((package / "final-evaluation.json").read_text())["trials"]
                    self.assertEqual(sorted({t["seed"] for t in trials}), replicates.HELD_OUT_SEEDS)
                    dev = json.loads((package / "iteration-0" / "summary.json").read_text())["trials"]
                    self.assertEqual({t["seed"] for t in dev}, {seed})
            report = (workspace / "rep-replicates.md").read_text()
        self.assertIn("**mean (n=2)**", report)
        self.assertIn("rep-a", report)

    def test_slope_is_per_iteration_over_raced_iterations_only(self) -> None:
        self.assertAlmostEqual(replicates._slope([10.0, None, 30.0, 40.0]), 10.0)
        self.assertIsNone(replicates._slope([5.0, None, None]))


if __name__ == "__main__":
    unittest.main()
