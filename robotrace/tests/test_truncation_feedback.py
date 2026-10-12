"""An answer cut off at the output limit is reported to the model as such, not as a bare JSON parse error."""
from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator.executors import PackageExecutor
from orchestrator.map_package import MapPackage
from orchestrator.race_service import MapDrivenRaceService
from orchestrator.validators import ContractFailure


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): return False


def reply(content: str, finish_reason: str, completion_tokens: int):
    body = {"id": "gen-test", "choices": [{"message": {"content": content}, "finish_reason": finish_reason}],
            "usage": {"prompt_tokens": 1000, "completion_tokens": completion_tokens}}
    return Response(json.dumps(body).encode())


class TruncationFeedbackTests(unittest.TestCase):
    def run_attempts(self, replies):
        requests = []

        def fake_urlopen(request, timeout=None):
            requests.append(json.loads(request.data))
            return replies[len(requests) - 1]

        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "test"}):
            service = MapDrivenRaceService("trunc", Path(directory)); service.prepare()
            package = MapPackage(service.packages[0]).validate()
            executor = PackageExecutor(package)
            action = package.actions["action0"]
            context = {"iteration": 0, "iteration_plan": None, "previous_iteration": None, "race": package.race,
                       "budget": {"iteration_tokens_remaining": 300000, "total_tokens_remaining": 2000000}}
            with mock.patch("orchestrator.executors.urlopen", fake_urlopen):
                with self.assertRaises(ContractFailure) as caught:
                    executor._openrouter(action, ["entity0"], {}, context)
            return requests, caught.exception, package.race["model"]["max_output_tokens"]

    def test_cut_off_answer_is_named_as_such_and_the_next_attempt_is_told(self) -> None:
        limit = 4000
        replies = [reply('{"entity0": {"rationale": "unterminated', "length", limit) for _ in range(4)]
        requests, failure, _ = self.run_attempts(replies)
        self.assertIn("cut off", failure.errors[0])
        self.assertIn(f"{limit:,}", failure.errors[0])
        second = json.loads(requests[1]["messages"][1]["content"])
        self.assertIn("cut off", second["previous_validation_error"])

    def test_a_genuine_syntax_error_is_not_called_a_cut_off(self) -> None:
        replies = [reply('{"entity0": nope}', "stop", 12) for _ in range(4)]
        requests, failure, _ = self.run_attempts(replies)
        self.assertNotIn("cut off", failure.errors[0])
        second = json.loads(requests[1]["messages"][1]["content"])
        self.assertNotIn("cut off", second["previous_validation_error"])

    def test_the_output_limit_is_in_the_budget_block(self) -> None:
        requests, _, cap = self.run_attempts([reply("{}", "stop", 5) for _ in range(4)])
        budget = json.loads(requests[0]["messages"][1]["content"])["remaining_budget"]
        self.assertEqual(budget["output_limit_tokens_this_call"], cap)
        self.assertIn("output_limit_tokens_this_call", requests[0]["messages"][0]["content"])


class PreviousCallsTests(unittest.TestCase):
    def test_an_actor_is_shown_what_its_earlier_calls_spent(self) -> None:
        from orchestrator.controller import MapDrivenController
        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("usage", Path(directory)); service.prepare()
            package = MapPackage(service.packages[0]).validate()
            controller = MapDrivenController(package, lambda *_: None, "test-sim")
            for iteration, rows in {0: [{"action": "action1", "type": "action_completed", "input_tokens": 9000, "output_tokens": 3000, "attempts": 2, "attempts_cut_off": 1},
                                        {"action": "action0", "type": "action_completed", "input_tokens": 1, "output_tokens": 1}],
                                    1: [{"action": "action1", "type": "action_rejected", "input_tokens": 40000, "output_tokens": 16000, "attempts": 4, "attempts_cut_off": 4}]}.items():
                path = package.path(f"iteration-{iteration}"); path.mkdir(parents=True, exist_ok=True)
                (path / "events.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
            calls = controller._previous_calls("action1", 2)
            self.assertEqual([c["iteration"] for c in calls], [1, 0], "newest first")
            self.assertEqual((calls[0]["delivered"], calls[0]["attempts"], calls[0]["attempts_cut_off_by_output_limit"]), (False, 4, 4))
            self.assertEqual((calls[1]["delivered"], calls[1]["input_tokens"], calls[1]["output_tokens"]), (True, 9000, 3000))
            self.assertEqual(controller._previous_calls("action1", 0), [])


if __name__ == "__main__":
    unittest.main()
