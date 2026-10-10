"""Race report: tied held-out scores share a place; charged tokens include rejected attempts."""
from __future__ import annotations

import unittest

from orchestrator.race_service import MapDrivenRaceService


class ReportColumnTests(unittest.TestCase):
    def test_ties_share_a_place_and_unraced_final_is_labelled(self) -> None:
        service = MapDrivenRaceService.__new__(MapDrivenRaceService)
        service.race_id = "r"
        scores = [
            {"entrant": "a", "score": 0.0, "development_score": None, "best_development_score": 992.4, "final_development_score": None},
            {"entrant": "b", "score": 0.0, "development_score": 6.7, "best_development_score": 8.8, "final_development_score": 6.7},
        ]
        text = "\n".join(service._race_summary_lines(scores))
        self.assertIn("| 1= | a | 0.0 | 992.4 | not raced |", text)
        self.assertIn("| 1= | b | 0.0 | 8.8 | 6.7 |", text)

    def test_a_clear_winner_has_no_tie_mark(self) -> None:
        service = MapDrivenRaceService.__new__(MapDrivenRaceService)
        service.race_id = "r"
        scores = [{"entrant": "a", "score": 5.0, "development_score": 1, "best_development_score": 1, "final_development_score": 1},
                  {"entrant": "b", "score": 0.0, "development_score": 1, "best_development_score": 1, "final_development_score": 1}]
        text = "\n".join(service._race_summary_lines(scores))
        self.assertIn("| 1 | a |", text)
        self.assertIn("| 2 | b |", text)


if __name__ == "__main__":
    unittest.main()
