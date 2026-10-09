"""Harness v2: an undelivered output ends the iteration as a race outcome (not a crash) and actors are told who depends on them."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import test_map_driven as base
from orchestrator.controller import ActionResult, MapDrivenController
from orchestrator.executors import downstream_dependents, role_brief, iteration_guidance
from orchestrator.map_package import MapPackage
from orchestrator.race_service import MapDrivenRaceService
from orchestrator.validators import ContractFailure


def package(root: Path, iterations: int) -> MapPackage:
    base.MapDrivenTests().package(root)
    race = root / "config/race.yaml"
    race.write_text(race.read_text() + f"iterations: {iterations}\n")
    return MapPackage(root).validate()


class IncompleteIterationTests(unittest.TestCase):
    def executor(self, omit_in: set[int], seen: list[tuple[int, str, dict]]):
        def execute(action, inputs, context):
            seen.append((context["iteration"], action.id, context))
            if action.id == "action0":
                if context["iteration"] in omit_in:
                    return ActionResult({}, {}, {}, {"kind": "omitted"})
                return ActionResult({"entity0": {"value": 1}}, {"entity0": "Ready"}, {}, {"kind": "made"})
            return ActionResult({"entity1": {"score": 1}, "entityR1": {"advice": "repeat"}}, {"entity1": "Complete"}, {}, {"kind": "ran"})
        return execute

    def test_omitted_output_closes_the_iteration_instead_of_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            controller = MapDrivenController(package(root, 3), self.executor({0}, []), "test-sim")
            controller.run_iteration(0)  # used to raise "workflow stalled"
            outcome = json.loads((root / "iteration-0/outcome.json").read_text())
            self.assertFalse(outcome["complete"])
            self.assertEqual(outcome["undelivered"], ["entity0"])
            self.assertEqual(outcome["blocked_actions"], {"action1": ["entity0"]})
            self.assertFalse((root / "iteration-0/entity1/current").exists())
            self.assertTrue((root / "scenario-iteration-1.yaml").exists(), "the next iteration must still be seeded")

    def test_next_iteration_is_told_what_was_not_delivered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, seen = Path(directory), []
            controller = MapDrivenController(package(root, 3), self.executor({0}, seen), "test-sim")
            controller.run_iteration(0)
            controller.run_iteration(1)
            first = next(ctx for it, action, ctx in seen if it == 0 and action == "action0")
            retry = next(ctx for it, action, ctx in seen if it == 1 and action == "action0")
            self.assertIsNone(first["previous_iteration"])
            self.assertEqual(retry["previous_iteration"]["undelivered"], ["entity0"])
            self.assertTrue((root / "iteration-1/entity1/current").exists(), "iteration 1 delivers and completes")
            self.assertTrue(json.loads((root / "iteration-1/outcome.json").read_text())["complete"])

    def test_rejected_output_is_feedback_not_a_crash(self) -> None:
        """A contract failure (e.g. a sensor 0.002 out of range) ends the iteration; the next one is told exactly what was rejected."""
        with tempfile.TemporaryDirectory() as directory:
            root, seen = Path(directory), []
            good = self.executor(set(), seen)

            def execute(action, inputs, context):
                if action.id == "action0" and context["iteration"] == 0:
                    raise ContractFailure("failed", "action0", ["sensor 0 x must be a number between -0.08 and 0.08 (got -0.082)"])
                return good(action, inputs, context)

            controller = MapDrivenController(package(root, 3), execute, "test-sim")
            controller.run_iteration(0)
            controller.run_iteration(1)
            outcome = json.loads((root / "iteration-0/outcome.json").read_text())
            self.assertFalse(outcome["complete"])
            self.assertIn("-0.082", outcome["reason"])
            retry = next(ctx for it, action, ctx in seen if it == 1 and action == "action0")
            self.assertIn("-0.082", retry["previous_iteration"]["reason"])
            self.assertEqual(retry["previous_iteration"]["rejected"]["action"], "action0")
            self.assertTrue(json.loads((root / "iteration-1/outcome.json").read_text())["complete"])

    def test_iteration_plan_flags_the_final_iteration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root, seen = Path(directory), []
            controller = MapDrivenController(package(root, 2), self.executor(set(), seen), "test-sim")
            controller.run_iteration(0)
            controller.run_iteration(1)
            plans = {it: ctx["iteration_plan"] for it, action, ctx in seen if action == "action0"}
            self.assertEqual(plans[0], {"iteration": 0, "iterations_total": 2, "iterations_remaining_after_this": 1, "final_iteration": False})
            self.assertTrue(plans[1]["final_iteration"])
            self.assertEqual(plans[1]["iterations_remaining_after_this"], 0)

    def test_token_exhaustion_before_delivery_is_an_incomplete_iteration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pkg = package(root, 1)
            controller = MapDrivenController(pkg, self.executor(set(), []), "test-sim")
            pkg.race["budget"]["max_tokens_per_iteration"] = 0  # spent before anything shipped (set after validation, which requires > 0)
            controller.run_iteration(0)
            outcome = json.loads((root / "iteration-0/outcome.json").read_text())
            self.assertFalse(outcome["complete"])
            self.assertIn("token budget", outcome["reason"])


class PromptContentTests(unittest.TestCase):
    def test_actor_is_told_who_depends_on_each_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pkg = package(Path(directory), 1)
            dependents = downstream_dependents(pkg, pkg.actions["action0"], ["entity0"])
            self.assertEqual(dependents, {"entity0": [{"action": "action1", "does": "Run", "actor": "Runner", "cannot_run_without_it": True, "what_they_do": None, "what_this_output_is_for": None}]})
            self.assertEqual(downstream_dependents(pkg, pkg.actions["action1"], ["entity1"]), {})

    def test_actor_gets_a_role_brief_and_required_outputs_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            pkg = package(Path(directory), 1)
            brief = role_brief(pkg, pkg.actions["action0"], ["entity0"])
            self.assertEqual(set(brief), {"you_are", "about_you", "your_action", "what_your_action_involves", "your_outputs"})
            self.assertIn("entity0", brief["your_outputs"])

    def test_final_iteration_warns_that_the_score_is_zero_if_nothing_ships(self) -> None:
        plan = {"iteration": 5, "iterations_total": 6, "iterations_remaining_after_this": 0, "final_iteration": True}
        text = iteration_guidance(plan, ["entity2"])["final_iteration_warning"]
        self.assertIn("scored 0", text)
        self.assertNotIn("final_iteration_warning", iteration_guidance({**plan, "final_iteration": False}, ["entity2"]))
        self.assertIsNone(iteration_guidance(None, []))


class FinalEvaluationTests(unittest.TestCase):
    def test_no_design_in_the_final_iteration_scores_zero_and_the_race_completes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            settings = {**base.FailedRunTests.SETTINGS, "iterations": "1"}
            service = MapDrivenRaceService("incomplete-final", Path(directory)); service.prepare()
            service.configure_common(settings)
            service.review("randow-maps"); service.review("opt-eval"); service.freeze()
            controllers = service.preflight()

            def close_without_delivery(controller):
                def run(iteration):
                    root = controller.package.path(f"iteration-{iteration}")
                    root.mkdir(parents=True, exist_ok=True)
                    (root / "outcome.json").write_text(json.dumps({"complete": False, "reason": "token budget exhausted", "undelivered": ["entity0"]}))
                controller.run_iteration = run
            for controller in controllers:
                close_without_delivery(controller)
            report = service._execute(controllers, json.loads(service.pair_path.read_text()))
            results = json.loads((Path(directory) / "incomplete-final-leaderboard.json").read_text())["results"]
            self.assertEqual({item["score"] for item in results}, {0.0})
            self.assertTrue(all(item["incomplete"] and item["development_score"] is None for item in results))
            final = json.loads(controllers[0].package.path("final-evaluation.json").read_text())
            self.assertTrue(final["incomplete"])
            self.assertEqual(final["reason"], "token budget exhausted")
            self.assertTrue(report.exists())


if __name__ == "__main__":
    unittest.main()
