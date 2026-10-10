"""Misplaced fields are moved, not rejected; an unmovable stray key is named in the error."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from orchestrator.executors import PackageExecutor


class _Package:
    def contract(self, entity_id):
        return {"properties": {"rationale": {}, "geometry": {}, "learning": {}}}


class ShapeTidyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = PackageExecutor.__new__(PackageExecutor)
        self.executor.package = _Package()

    def test_stray_top_level_field_moves_into_the_single_entity(self) -> None:
        output = {"entity0": {"rationale": "r"}, "learning": "l"}
        self.executor._tidy_shape(output, {"entity0"}, None)
        self.assertEqual(output, {"entity0": {"rationale": "r", "learning": "l"}})

    def test_nested_presentation_is_lifted_and_top_level_one_wins(self) -> None:
        pres = {"entity0": {"label": "x", "notes": "y"}}
        output = {"entity0": {"rationale": "r", "_presentation": pres}}
        self.assertEqual(self.executor._tidy_shape(output, {"entity0"}, None), pres)
        self.assertNotIn("_presentation", output["entity0"])
        output = {"entity0": {"_presentation": pres}}
        self.assertEqual(self.executor._tidy_shape(output, {"entity0"}, "top"), "top")

    def test_unknown_key_is_left_alone_for_the_contract_to_name(self) -> None:
        output = {"entity0": {"rationale": "r"}, "mystery": 1}
        self.executor._tidy_shape(output, {"entity0"}, None)
        self.assertIn("mystery", output)

    def test_race_32_rejected_outputs_now_tidy_to_valid_shape(self) -> None:
        root = Path(__file__).resolve().parents[2] / "race-32-randow-maps"
        files = sorted(root.glob("iteration-*/rejected-attempts/action0-attempt-*.json"))
        if not files:
            self.skipTest("race-32 outputs not present")
        for file in files:
            output = json.loads(json.loads(file.read_text())["raw_output"])
            output.pop("_presentation", None)
            self.executor._tidy_shape(output, {"entity0"}, None)
            self.assertEqual(set(output), {"entity0"}, file.name)
            self.assertNotIn("_presentation", output["entity0"], file.name)


if __name__ == "__main__":
    unittest.main()
