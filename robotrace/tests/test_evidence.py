from __future__ import annotations

import json
import unittest

from orchestrator.evidence import keep_telemetry, summarise_payload, summarise_trials


def trial(track: str, seed: int, reason: str, score: float, telemetry: bool = True) -> dict:
    return {"track": track, "seed": seed, "termination_reason": reason, "score": score,
            "metrics": {"progress": 1.0 if reason == "finished" else 0.4, "completion_time": 2.0, "rms_error": 0.01, "max_error": 0.03, "line_loss_events": 0, "steering_oscillation": 0.2, "control_effort": 9.0},
            "telemetry": [{"step": 0, "progress": 0.0}] if telemetry else []}


TRIALS = [trial("oval", 1, "finished", 980), trial("oval", 2, "finished", 990), trial("slalom", 1, "finished", 990), trial("slalom", 2, "off_track", 150), trial("slalom", 3, "off_track", 130)]


class EvidenceTests(unittest.TestCase):
    def test_summary_counts_finishes_and_endings_per_track(self) -> None:
        summary = summarise_trials(TRIALS)
        self.assertEqual(summary["oval"]["finish_rate"], 1.0)
        self.assertEqual(summary["slalom"]["finished"], 1)
        self.assertEqual(summary["slalom"]["ended_by"], {"finished": 1, "off_track": 2})
        self.assertEqual(summary["slalom"]["min_score"], 130.0)
        self.assertEqual(summary["slalom"]["mean_finish_time_s"], 2.0)

    def test_payload_summary_drops_trials_and_telemetry_but_keeps_other_keys(self) -> None:
        shown = summarise_payload({"entityR2A": {"score": 640.0, "summary": "x", "trials": TRIALS}, "other": {"a": 1}})
        text = json.dumps(shown)
        self.assertNotIn('"step"', text)  # no per-step rows
        self.assertNotIn('"seed"', text)  # no per-trial rows survive
        self.assertEqual(shown["entityR2A"]["score"], 640.0)
        self.assertEqual(shown["entityR2A"]["trials_summary"]["n_trials"], 5)
        self.assertEqual(shown["other"], {"a": 1})

    def test_keep_telemetry_limits_recorded_trials_per_track_and_keeps_scores(self) -> None:
        kept = keep_telemetry([dict(t) for t in TRIALS], 1)
        self.assertEqual([bool(t["telemetry"]) for t in kept], [True, False, True, False, False])
        self.assertEqual([t["score"] for t in kept], [t["score"] for t in TRIALS])
        self.assertIs(keep_telemetry(TRIALS, None), TRIALS)


if __name__ == "__main__":
    unittest.main()
