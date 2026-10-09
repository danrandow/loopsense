from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from orchestrator import progress

T0 = datetime(2026, 10, 9, 10, 0, 0, tzinfo=timezone.utc).timestamp()


def stamp(offset: float) -> str:
    return datetime.fromtimestamp(T0 + offset, timezone.utc).isoformat()


def write(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")


def make_race(root: Path, status: str = "running", done: int = 2, running: bool = True) -> None:
    package = root / "race-1-randow-maps"
    write(root / "race-1-pair.json", {"race_id": "race-1", "status": status, "packages": [str(package)]})
    write(package / "config/race.yaml", "entrant: randow-maps\niterations: 4\nmodel: {provider: mock, id: m}\nbudget: {max_action_runs: 6, total_tokens_per_condition: 1000, max_tokens_per_iteration: 400}\n")
    for i in range(done + (1 if running else 0)):
        base = i * 20
        lines = [{"action": "action0", "timestamp": stamp(base), "input_tokens": 100, "output_tokens": 10}]
        d = package / f"iteration-{i}"
        if i < done:
            lines.append({"action": "action2", "component": "sim", "timestamp": stamp(base + 10)})
            write(d / "outcome.json", {"complete": True})
            write(d / "summary.json", {"trials": [{"track": "oval", "score": 10.0 * (i + 1), "termination_reason": "off_track"}, {"track": "s-bend", "score": 20.0 * (i + 1), "termination_reason": "off_track"}]})
        write(d / "events.jsonl", "\n".join(json.dumps(x) for x in lines) + '\n{"truncated"')  # half-written last line must be tolerated
        write(d / "budget-ledger.json", {"action_runs": len(lines), "iteration_tokens": 110, "total_tokens": 110 * (i + 1)})
    if done:
        write(package / "iteration-0/rejected-attempts/action0-attempt-1.json", {"action": "action0", "attempt": 1, "error": "bad shape"})


class ProgressTests(unittest.TestCase):
    def test_running_race_reports_real_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); make_race(root)
            s = progress.snapshot("race-1", root, now=T0 + 60)
            e = s["entrants"][0]
            self.assertEqual((s["units_done"], s["units_total"]), (2, 5))
            self.assertEqual(e["phase"], "iterating")
            self.assertEqual(e["current_iteration"], 2)
            self.assertEqual([i["score"] for i in e["iterations"] if i["state"] == "raced"], [15.0, 30.0])
            self.assertEqual(e["budget"]["total_used"], 330)
            self.assertEqual(e["problem_count"], 1)
            self.assertEqual(s["health"], "active")
            self.assertIsNotNone(e["eta_s"])

    def test_quiet_running_race_is_flagged_stalled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); make_race(root)
            s = progress.snapshot("race-1", root, now=T0 + 40 + progress.QUIET_AFTER_S + 600)
            self.assertEqual(s["health"], "stalled")

    def test_complete_and_incomplete_final(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); make_race(root, "complete", done=4, running=False)
            write(root / "race-1-randow-maps/final-evaluation.json", {"incomplete": True, "reason": "workflow stalled", "trials": []})
            s = progress.snapshot("race-1", root, now=T0 + 9999)
            self.assertEqual(s["fraction"], 1.0)
            self.assertTrue(s["entrants"][0]["final"]["incomplete"])
            self.assertEqual(s["health"], "complete")

    def test_not_raced_iteration_and_bad_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); make_race(root, done=1, running=False)
            write(root / "race-1-randow-maps/iteration-0/outcome.json", {"complete": False, "reason": "budget spent", "undelivered": ["entity1"]})
            it = progress.snapshot("race-1", root, now=T0 + 5)["entrants"][0]["iterations"][0]
            self.assertEqual((it["state"], it["reason"]), ("not_raced", "budget spent"))
            with self.assertRaises(ValueError):
                progress.snapshot("../etc", root)
            with self.assertRaises(FileNotFoundError):
                progress.snapshot("race-9", root)
            self.assertEqual(progress.handle("/progress.json?race_id=race-9", root)[0], 404)


if __name__ == "__main__":
    unittest.main()
