"""Replicate races: distinct development seeds, shared held-out seeds, and a comparison across them."""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import replicates  # noqa: E402

# Replicates never override held_out_seeds (see replicates.run), so the template's own list is what every replicate uses.
TEMPLATE_HELD_OUT_SEEDS = sorted(yaml.safe_load((replicates.ROOT / "robotrace" / "package-templates" / "randow-maps" / "config" / "race.yaml").read_text())["evaluation"]["held_out_seeds"])


class ReplicateTests(unittest.TestCase):
    def test_mock_replicates_use_own_dev_seed_and_shared_held_out_seeds(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            replicates.run(argparse.Namespace(base="rep", n=2, iterations=2, provider="mock", model="deterministic-mock-v1", max_output_tokens=700,
                                              total_tokens=900000, iteration_tokens=300000, workspace=workspace))
            for index, race in enumerate(("rep-a", "rep-b")):
                own_dev_seeds = set(range(index * replicates.SEEDS_PER_REPLICATE + 1, (index + 1) * replicates.SEEDS_PER_REPLICATE + 1))
                for entrant in replicates.ENTRANTS:
                    package = workspace / f"{race}-{entrant}"
                    trials = json.loads((package / "final-evaluation.json").read_text())["trials"]
                    self.assertEqual(sorted({t["seed"] for t in trials}), TEMPLATE_HELD_OUT_SEEDS)
                    dev = json.loads((package / "iteration-0" / "summary.json").read_text())["trials"]
                    self.assertEqual({t["seed"] for t in dev}, own_dev_seeds)
            report = (workspace / "rep-replicates.md").read_text()
        self.assertIn("**mean (n=2)**", report)
        self.assertIn("rep-a", report)

    def test_slope_is_per_iteration_over_raced_iterations_only(self) -> None:
        self.assertAlmostEqual(replicates._slope([10.0, None, 30.0, 40.0]), 10.0)
        self.assertIsNone(replicates._slope([5.0, None, None]))


if __name__ == "__main__":
    unittest.main()
