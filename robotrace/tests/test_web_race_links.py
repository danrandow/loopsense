from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator import web
from orchestrator.race_service import MapDrivenRaceService


class RaceArtifactLinkTests(unittest.TestCase):
    SETTINGS = {
        "iterations": "1", "provider": "mock", "model_id": "deterministic-mock-v1",
        "max_output_tokens": "700", "max_action_runs": "6",
        "total_tokens_per_condition": "900000", "max_tokens_per_iteration": "300000",
    }

    def make_race(self, root: Path, race_id: str, *, replay: bool = True, scenarios: bool = True) -> dict[str, object]:
        packages = [root / f"{race_id}-randow-maps", root / f"{race_id}-opt-eval"]
        for package in packages:
            package.mkdir()
            if scenarios:
                (package / "scenario-iteration-2.yaml").write_text("map: {}\n")
                (package / "scenario-iteration-10.yaml").write_text("map: {}\n")
        if replay:
            (root / f"{race_id}-replay.html").write_text("replay")
        state = {
            "status": "complete",
            "report": str(root / f"{race_id}-race-report.md"),
            "leaderboard": str(root / f"{race_id}-leaderboard.json"),
            "packages": [str(package) for package in packages],
        }
        (root / f"{race_id}-pair.json").write_text(json.dumps(state))
        return state

    def test_complete_race_links_every_artifact_and_latest_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = self.make_race(root, "race-42")
            links = dict(web._race_links("race-42", state, root))
        self.assertEqual(set(links), {"Report", "Leaderboard", "Pit Wall", "Randow Map", "Control Map"})
        self.assertEqual(links["Pit Wall"], "/race-42-replay.html")
        self.assertIn("map=race-42-randow-maps", links["Randow Map"])
        self.assertIn("scenario=scenario-iteration-10", links["Randow Map"])
        self.assertIn("map=race-42-opt-eval", links["Control Map"])

    def test_missing_replay_and_scenarios_do_not_make_broken_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = self.make_race(root, "race-legacy", replay=False, scenarios=False)
            links = dict(web._race_links("race-legacy", state, root))
        self.assertEqual(set(links), {"Report", "Leaderboard"})

    def test_incomplete_race_has_no_evidence_links_in_races_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_race(root, "race-running")
            pair = root / "race-running-pair.json"
            state = json.loads(pair.read_text())
            state["status"] = "running"
            pair.write_text(json.dumps(state))
            with mock.patch.object(web, "ROOT", root):
                rendered = web._race_list("race-running")
        self.assertIn("running", rendered)
        self.assertNotIn("Pit Wall", rendered)
        self.assertNotIn("Randow Map", rendered)

    def test_complete_race_list_exposes_all_five_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_race(root, "race-42")
            with mock.patch.object(web, "ROOT", root):
                rendered = web._race_list("race-42")
        for label in ("Report", "Leaderboard", "Pit Wall", "Randow Map", "Control Map"):
            self.assertIn(f">{label}</a>", rendered)

    def test_replay_is_served_as_html(self) -> None:
        self.assertEqual(web.artifact_content_type(Path("race-42-replay.html")), "text/html; charset=utf-8")
        self.assertEqual(web.artifact_content_type(Path("race-42-race-report.md")), "text/plain; charset=utf-8")

    def test_newly_completed_race_generates_and_exposes_replay(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            service = MapDrivenRaceService("race-fresh", root)
            service.prepare()
            service.configure_common(self.SETTINGS)
            service.review("randow-maps")
            service.review("opt-eval")
            service.freeze()
            service.run()
            state = json.loads(service.pair_path.read_text())
            links = dict(web._race_links(service.race_id, state, root))
            replay = root / "race-fresh-replay.html"
            self.assertTrue(replay.is_file())
            self.assertEqual(links["Pit Wall"], "/race-fresh-replay.html")


if __name__ == "__main__":
    unittest.main()
