"""Agent outputs carry a meaningful label and notes, and the scenario links their artefacts."""
from __future__ import annotations

import unittest

from orchestrator.executors import full_notes, validate_presentation


class PresentationTests(unittest.TestCase):
    GOOD = {"entity0": {"label": "Wider sensor array", "notes": "Seven sensors to recover the line earlier on the hairpin."}}

    def test_specific_label_and_notes_are_accepted(self) -> None:
        self.assertEqual(validate_presentation({"entity0"}, self.GOOD), self.GOOD)

    def test_generic_label_is_rejected(self) -> None:
        bad = {"entity0": {**self.GOOD["entity0"], "label": "Updated"}}
        with self.assertRaisesRegex(ValueError, "generic"):
            validate_presentation({"entity0"}, bad)

    def test_overlong_label_is_rejected(self) -> None:
        bad = {"entity0": {**self.GOOD["entity0"], "label": "x" * 26}}
        with self.assertRaisesRegex(ValueError, "limit is 25"):
            validate_presentation({"entity0"}, bad)

    def test_missing_entity_and_thin_notes_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_presentation({"entity0", "entity3"}, self.GOOD)
        with self.assertRaisesRegex(ValueError, "notes"):
            validate_presentation({"entity0"}, {"entity0": {"label": "Wider sensors", "notes": "ok"}})


if __name__ == "__main__":
    unittest.main()


class FullNotesTests(unittest.TestCase):
    def test_map_note_carries_rationale_and_feedback_verbatim(self) -> None:
        note = full_notes("Wider array.", {"rationale": "Sensors never saw the line.\n\n- so widen"})
        self.assertTrue(note.startswith("Wider array."))
        self.assertIn("### Rationale\n\nSensors never saw the line.", note)
        fb = full_notes("Critique.", {"feedback": "Weights give no steering signal.", "requested_changes": ["weights -> [-1,0,1]", " "]})
        self.assertIn("### Feedback\n\nWeights give no steering signal.", fb)
        self.assertIn("### Requested changes\n\n- weights -> [-1,0,1]", fb)
        self.assertEqual(full_notes("Only summary.", {"geometry": {}}), "Only summary.")
