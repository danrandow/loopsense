from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from orchestrator.executors import PackageExecutor, compact_telemetry
from orchestrator.history import TELEMETRY_OMITTED, build_history, estimate_tokens
from orchestrator.map_package import MapPackage, PackageValidationError

SETTINGS = {"enabled": True, "telemetry_token_ceiling": 100000}
GEOMETRY = {"wheel_track": 0.12}
CONTROLLER = {"kp": 1.0}


def race_data(score: float, steps: int = 20) -> dict:
    row = {"progress": 0.1, "error": 0.01, "speed": 0.5, "x": 0.1, "y": 0.0, "heading": 0.0, "sensors": [0.0, 1.0, 0.0], "line_lost": False}
    return {"summary": "s", "score": score, "trials": [{"track": "oval", "seed": 17, "termination_reason": "off_track", "score": score, "run_id": "r",
            "metrics": {"progress": 0.1, "completion": False, "line_loss_events": 1, "rms_error": 0.02, "max_error": 0.06}, "telemetry": [dict(row, step=i) for i in range(steps)]}]}


def put(root: Path, iteration: int, entity: str, payload: dict, version: str | None = None) -> None:
    version = version or f"v{iteration}{entity}"
    folder = root / f"iteration-{iteration}" / entity
    (folder / "versions" / version).mkdir(parents=True, exist_ok=True)
    (folder / "versions" / version / "payload.json").write_text(json.dumps(payload))
    (folder / "current").write_text(version + "\n")


def build(root: Path, iterations: int, **kw):
    """History for a Builder-like actor: writes entity0, reads feedback and race data."""
    args = dict(reads=frozenset({"entityR1", "entityR2A"}), writes=frozenset({"entity0"}), iteration=iterations, inputs={}, settings=SETTINGS, pack=compact_telemetry)
    args.update(kw)
    return build_history(root, **args)


class HistoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        for k in range(4):
            put(self.root, k, "entity0", {"geometry": {**GEOMETRY, "wheel_track": 0.10 + k / 100}, "rationale": f"geometry {k}"})
            put(self.root, k, "entity1", {"geometry": GEOMETRY, "controller": {"kp": 1.0 + k}})  # a controller the Builder must never see
            put(self.root, k, "entityR2A", race_data(10.0 * (k + 1)))
            put(self.root, k, "entityR1", {"feedback": f"feedback {k}", "requested_changes": []})
            if k:  # carried copies of the previous iteration's feedback and race data
                put(self.root, k, "entityR1", {"feedback": f"feedback {k - 1}", "requested_changes": []}, version="carried-aa")
                (self.root / f"iteration-{k}" / "entityR1" / "current").write_text(f"v{k}entityR1\n")
            (self.root / f"iteration-{k}" / "outcome.json").write_text(json.dumps({"complete": True}))

    def test_nothing_to_show_before_the_first_iteration_or_when_disabled(self) -> None:
        self.assertIsNone(build(self.root, 0))
        self.assertIsNone(build(self.root, 3, settings=None))
        self.assertIsNone(build(self.root, 3, settings={"enabled": False, "telemetry_token_ceiling": 1}))

    def test_actor_sees_only_entities_it_is_authorised_to_read_or_write(self) -> None:
        history = build(self.root, 3)
        text = json.dumps(history)
        self.assertNotIn("controller", text)  # entity1 holds the controller and is not this actor's
        first = history["iterations"][0]
        self.assertEqual(set(first["produced"]), {"entity0"})
        self.assertEqual(set(first["received"]), {"entityR1", "entityR2A"})

    def test_outcome_table_joins_visible_design_values_to_the_race_result(self) -> None:
        row = build(self.root, 3)["outcome_table"][1]
        self.assertEqual(row["design"], {"geometry": {"wheel_track": 0.11}})
        self.assertEqual(row["outcome"]["score"], 20.0)
        self.assertEqual(row["outcome"]["trials"][0]["line_loss_events"], 1)

    def test_full_actor_sees_design_values_it_is_authorised_for(self) -> None:
        history = build(self.root, 3, reads=frozenset({"entityR2A"}), writes=frozenset({"entity1"}))
        self.assertEqual(history["outcome_table"][2]["design"]["controller"], {"kp": 3.0})

    def test_entities_identical_to_authorized_inputs_are_referenced_not_repeated(self) -> None:
        inputs = {"entityR2A": race_data(30.0)}  # equals iteration 2's race data
        history = build(self.root, 3, inputs=inputs)
        self.assertEqual(history["iterations"][2]["received"]["entityR2A"], {"same_as_authorized_input": "entityR2A"})

    def test_carried_versions_are_not_duplicated(self) -> None:
        feedback = [v["received"]["entityR1"]["feedback"] for v in build(self.root, 3)["iterations"]]
        self.assertEqual(feedback, ["feedback 0", "feedback 1", "feedback 2"])

    def test_telemetry_is_kept_newest_first_until_the_ceiling(self) -> None:
        one = estimate_tokens(race_data(0), compact_telemetry)
        history = build(self.root, 4, settings={"enabled": True, "telemetry_token_ceiling": one * 2 + 20})
        self.assertEqual(history["telemetry"]["full_telemetry_iterations"], [2, 3])
        older = history["iterations"][0]["received"]["entityR2A"]["trials"][0]
        self.assertEqual(older["telemetry"], TELEMETRY_OMITTED)
        self.assertEqual(older["metrics"]["progress"], 0.1)
        self.assertIsInstance(history["iterations"][3]["received"]["entityR2A"]["trials"][0]["telemetry"], list)

    def test_telemetry_in_authorized_inputs_counts_against_the_ceiling(self) -> None:
        one = estimate_tokens(race_data(0), compact_telemetry)
        history = build(self.root, 4, inputs={"entityR2A": race_data(99.0)}, settings={"enabled": True, "telemetry_token_ceiling": one * 2 + 20})
        self.assertEqual(history["telemetry"]["full_telemetry_iterations"], [3])

    def test_a_failing_team_keeps_all_telemetry_while_it_fits(self) -> None:
        self.assertEqual(build(self.root, 4)["telemetry"]["full_telemetry_iterations"], [0, 1, 2, 3])

    def test_pack_cap_drops_oldest_detail_but_keeps_the_outcome_table(self) -> None:
        full = build(self.root, 4, settings={"enabled": True, "telemetry_token_ceiling": 0})
        cap = estimate_tokens(full, compact_telemetry) - 1
        history = build(self.root, 4, settings={"enabled": True, "telemetry_token_ceiling": 0}, pack_cap=cap)
        self.assertEqual(history["telemetry"]["detail_omitted_iterations"], [0])
        self.assertEqual(len(history["outcome_table"]), 4)
        self.assertEqual(history["iterations"][0]["produced"], {})
        self.assertEqual(history["iterations"][3]["produced"]["entity0"]["rationale"], "geometry 3")
        self.assertLessEqual(estimate_tokens(history, compact_telemetry), cap)

    def test_incomplete_iteration_is_recorded(self) -> None:
        (self.root / "iteration-1" / "outcome.json").write_text(json.dumps({"complete": False, "reason": "token budget exhausted"}))
        history = build(self.root, 3)
        self.assertFalse(history["iterations"][1]["complete"])
        self.assertEqual(history["outcome_table"][1]["incomplete_reason"], "token budget exhausted")


class ExecutorWiringTests(unittest.TestCase):
    def executor(self, root: Path, history: dict | None, iteration_tokens: int = 40000) -> tuple[PackageExecutor, SimpleNamespace, dict]:
        action = SimpleNamespace(id="action0", reads=frozenset({"entityR1", "entityR2A"}), writes=frozenset({"entity0"}), runtime={"kind": "model"})
        sim = SimpleNamespace(runtime={"kind": "component"})
        race = {"model": {"max_output_tokens": 4000}, **({"history": history} if history is not None else {})}
        package = SimpleNamespace(root=root, race=race, actions={"action0": action, "action1": action, "action2": sim})
        context = {"iteration": 3, "budget": {"iteration_tokens_remaining": iteration_tokens, "total_tokens_remaining": 250000}}
        return PackageExecutor(package), action, context  # type: ignore[arg-type]

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        for k in range(3):
            put(self.root, k, "entity0", {"geometry": GEOMETRY, "rationale": "r"})
            put(self.root, k, "entityR2A", race_data(5.0))

    def test_no_history_setting_means_no_pack(self) -> None:
        executor, action, context = self.executor(self.root, None)
        self.assertIsNone(executor._history(action, {}, context, base_tokens=0))

    def test_pack_is_sized_to_the_remaining_token_budget(self) -> None:
        executor, action, context = self.executor(self.root, SETTINGS)
        roomy = executor._history(action, {}, context, base_tokens=0)
        self.assertEqual(roomy["telemetry"]["full_telemetry_iterations"], [0, 1, 2])
        executor, action, context = self.executor(self.root, SETTINGS, iteration_tokens=9000)  # (9000 / 2 model actions) leaves nothing after output reserve
        tight = executor._history(action, {}, context, base_tokens=0)
        self.assertEqual(tight["telemetry"]["full_telemetry_iterations"], [])


class RaceConfigTests(unittest.TestCase):
    def validate(self, history: object) -> None:
        race = {"race_id": "r", "model": {"provider": "mock", "id": "m", "max_output_tokens": 1}, "evaluation": {}, "simulator": {},
                "budget": {"max_action_runs": 1, "total_tokens_per_condition": 10, "max_tokens_per_iteration": 5}, "history": history}
        MapPackage._validate_race(SimpleNamespace(race=race))  # type: ignore[arg-type]

    def test_valid_and_invalid_history_settings(self) -> None:
        self.validate({"enabled": True, "telemetry_token_ceiling": 0})
        for bad in ({"enabled": "yes", "telemetry_token_ceiling": 1}, {"enabled": True}, {"telemetry_token_ceiling": -1}, {"telemetry_token_ceiling": True}, "on"):
            with self.assertRaises(PackageValidationError):
                self.validate(bad)


class MockRaceEndToEndTests(unittest.TestCase):
    """A whole mock race from the shipped templates: both teams get the same history setting and each actor's pack respects its reads."""

    def test_every_actor_gets_a_pack_from_the_second_iteration_and_only_of_what_it_may_see(self) -> None:
        from unittest import mock
        from orchestrator.race_service import MapDrivenRaceService

        settings = {"iterations": "3", "provider": "mock", "model_id": "deterministic-mock-v1", "max_output_tokens": "700", "max_action_runs": "6",
                    "total_tokens_per_condition": "900000", "max_tokens_per_iteration": "300000"}
        seen: list[tuple[str, str, int, dict | None]] = []
        original = PackageExecutor._history

        def spy(self_, action, inputs, context, base_tokens):
            result = original(self_, action, inputs, context, base_tokens)
            seen.append((self_.package.race["entrant"], action.id, int(context["iteration"]), result))
            return result

        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("history-e2e", Path(directory)); service.prepare()
            service.configure_common(settings)
            service.review("randow-maps"); service.review("opt-eval"); service.freeze()
            with mock.patch.object(PackageExecutor, "_history", spy):
                service.run()
        self.assertTrue(seen)
        for entrant, action, iteration, history in seen:
            if iteration == 0:
                self.assertIsNone(history, (entrant, action))
                continue
            self.assertIsNotNone(history, (entrant, action, iteration))
            self.assertEqual(len(history["outcome_table"]), iteration)
            if (entrant, action) == ("randow-maps", "action0"):  # the Geometry Builder never sees the controller
                self.assertNotIn('"controller":', json.dumps(history))
            else:
                self.assertIn('"controller":', json.dumps(history))

    def test_reports_show_token_cost_per_team_and_race_total(self) -> None:
        from orchestrator.race_service import MapDrivenRaceService

        settings = {"iterations": "3", "provider": "mock", "model_id": "deterministic-mock-v1", "max_output_tokens": "700", "max_action_runs": "6",
                    "total_tokens_per_condition": "900000", "max_tokens_per_iteration": "300000"}
        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("token-report", Path(directory)); service.prepare()
            service.configure_common(settings)
            service.review("randow-maps"); service.review("opt-eval"); service.freeze()
            report = service.run()
            text = report.read_text(encoding="utf-8")
            board = json.loads((Path(directory) / "token-report-leaderboard.json").read_text())
            team = (Path(directory) / "token-report-randow-maps" / "race-report.md").read_text(encoding="utf-8")
        self.assertIn("## Token cost", text)
        self.assertIn("**Race total**", text)
        self.assertIn("randow-maps token cost", team)
        total = sum(item["tokens"]["input"] + item["tokens"]["output"] for item in board["results"])
        self.assertGreater(total, 0)
        self.assertIn(f"**{total}**", text)
        self.assertTrue(all(item["tokens"]["history"] > 0 for item in board["results"]))


    def test_context_budget_tells_the_actor_what_is_still_to_be_spent(self) -> None:
        from unittest import mock
        from orchestrator.race_service import MapDrivenRaceService

        settings = {"iterations": "2", "provider": "mock", "model_id": "deterministic-mock-v1", "max_output_tokens": "700", "max_action_runs": "6",
                    "total_tokens_per_condition": "900000", "max_tokens_per_iteration": "300000"}
        seen = []
        original = PackageExecutor._history

        def spy(self_, action, inputs, context, base_tokens):
            seen.append((self_.package.race["entrant"], action.id, int(context["iteration"]), dict(context["budget"])))
            return original(self_, action, inputs, context, base_tokens)

        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("budget-fields", Path(directory)); service.prepare()
            service.configure_common(settings)
            service.review("randow-maps"); service.review("opt-eval"); service.freeze()
            with mock.patch.object(PackageExecutor, "_history", spy):
                service.run()
        first = [b for e, a, i, b in seen if e == "randow-maps" and i == 0]
        self.assertEqual([b["model_actions_still_to_run_this_iteration"] for b in first], [1, 0])
        self.assertEqual({b["iterations_remaining_after_this"] for b in first}, {1})
        self.assertEqual({b["iterations_remaining_after_this"] for e, a, i, b in seen if i == 1}, {0})


if __name__ == "__main__":
    unittest.main()
