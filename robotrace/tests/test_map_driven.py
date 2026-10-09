from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from orchestrator.controller import ActionResult, MapDrivenController
from orchestrator.map_package import MapPackage, PackageValidationError
from orchestrator.transactions import ScenarioTransaction, recover_transactions
from orchestrator.race_service import MapDrivenRaceService


BASE = """map:
  id: test-team
  title: Test Team
  schema: v0.2
  scenario: Moving Parts
  is_moo: true
  dimension_axes: [time_horizon, iteration]
actors:
  - {id: actor0, label: Maker}
  - {id: actor1, label: Runner}
actions:
  - {id: action0, actor: actor0, label: Make}
  - {id: action1, actor: actor1, label: Run}
entities:
  - {id: entity0, label: Build, system_boundary: internal}
  - {id: entity1, label: Result, system_boundary: internal}
  - {id: entityR1, label: Feedback}
edges:
  - {id: edge0G, type: generates, from: action0, to: entity0}
  - {id: edge0U, type: used by, from: entity0, to: action1}
  - {id: edge1G, type: generates, from: action1, to: entity1}
  - {id: edge1R1G, type: generates, from: action1, to: entityR1, direction: return}
  - {id: edge1R1U, type: used by, from: entityR1, to: action0, direction: return}
"""


class MapDrivenTests(unittest.TestCase):
    def package(self, root: Path) -> MapPackage:
        (root / "base.yaml").write_text(BASE)
        (root / "config").mkdir()
        (root / "config/workflow.yaml").write_text("""version: 1
entry_actions: [action0]
reentry: {action0: on_new_inputs, action1: once_per_iteration}
iteration_complete_when: {entities_present: [entity1, entityR1]}
""")
        (root / "config/race.yaml").write_text("""race_id: template
model: {provider: mock, id: mock, max_output_tokens: 100}
budget: {max_action_runs: 3, total_tokens_per_condition: 1000, max_tokens_per_iteration: 500}
evaluation: {tracks: [oval], seeds: [1]}
simulator: {version: test}
""")
        (root / "scenario-iteration-0.yaml").write_text("""map:
  id: test-team
  schema: v0.2
  scenario: Iteration 0
  inherits: base.yaml
dimensions: {time_horizon: race-test, iteration: 0}
overrides: {}
""")
        for action in ("action0", "action1"):
            directory = root / "actions" / action
            directory.mkdir(parents=True)
            (directory / "runtime.yaml").write_text("kind: model\n")
            (directory / "instructions.md").write_text(f"Perform {action}.\n")
        contract = root / "entities/entity0"
        contract.mkdir(parents=True)
        (contract / "contract.schema.json").write_text(json.dumps({"type": "object", "required": ["value"], "properties": {"value": {"type": "number"}}, "additionalProperties": False}))
        return MapPackage(root).validate()

    def test_topology_derives_read_write_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            package = self.package(Path(directory))
            self.assertEqual(package.actions["action0"].reads, {"entityR1"})
            self.assertEqual(package.actions["action0"].writes, {"entity0"})
            with self.assertRaises(PermissionError):
                package.require_write("action0", "entity1")

    def test_scenario_cannot_change_structure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.package(root)
            scenario = root / "scenario-iteration-0.yaml"
            scenario.write_text(scenario.read_text() + "actors: []\n")
            with self.assertRaises(PackageValidationError):
                package.validate_scenario(scenario)

    def test_transaction_failure_is_not_visible_and_resume_rejects_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.package(root)
            iteration = root / "iteration-0"
            scenario = root / "scenario-iteration-0.yaml"
            original = scenario.read_text()
            transaction = ScenarioTransaction(package, scenario, iteration, "action0")
            transaction.write_entity("entity0", {"value": 1})
            transaction.update("entities", "entity0", label="Ready")
            transaction.append_event("done", {})
            with self.assertRaises(RuntimeError):
                transaction.commit(fail_at="prepared")
            self.assertEqual(scenario.read_text(), original)
            self.assertEqual(recover_transactions(iteration), [transaction.id])

    def test_all_transaction_boundaries_roll_back_visible_state(self) -> None:
        for boundary in ("prepared", "artifacts", "scenario", "event", "budget", "checkpoint"):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as directory:
                root = Path(directory); package = self.package(root); scenario = root / "scenario-iteration-0.yaml"; original = scenario.read_bytes(); iteration = root / "iteration-0"
                transaction = ScenarioTransaction(package, scenario, iteration, "action0")
                transaction.write_entity("entity0", {"value": 1}); transaction.append_event("done", {}); transaction.update_budget({"action_runs": 1})
                with self.assertRaises(RuntimeError): transaction.commit(fail_at=boundary)
                self.assertEqual(scenario.read_bytes(), original)
                self.assertFalse((iteration / "entity0/current").exists())
                self.assertFalse((iteration / "events.jsonl").exists())
                self.assertFalse((iteration / "budget-ledger.json").exists())
                self.assertFalse((iteration / "checkpoint.json").exists())

    def test_root_yaml_allowlist_and_ui_legacy_guard(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.package(root); (root / "workflow.yaml").write_text("bad: true\n")
            with self.assertRaisesRegex(PackageValidationError, "root YAML"):
                MapPackage(root).validate()
        web_source = (Path(__file__).parents[1] / "orchestrator/web.py").read_text()
        self.assertNotIn("ExperimentRunner", web_source)
        self.assertNotIn("from .runner", web_source)

    def test_definition_edit_invalidates_review_and_freeze_locks_edits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("edit-test", Path(directory)); service.prepare(); service.review("randow-maps")
            path = service.packages[0] / "base.yaml"
            service.update_definition("randow-maps", "base.yaml", path.read_text() + "\n# review edit\n")
            self.assertNotIn("randow-maps", json.loads(service.pair_path.read_text())["reviewed"])
            service.review("randow-maps"); service.review("opt-eval"); service.freeze()
            with self.assertRaisesRegex(RuntimeError, "before freeze"):
                service.update_definition("randow-maps", "base.yaml", "changed")

    def test_common_settings_are_paired_and_invalidate_reviews(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            service = MapDrivenRaceService("settings-test", Path(directory)); service.prepare(); service.review("randow-maps")
            service.configure_common({
                "iterations": "3", "provider": "openrouter", "model_id": "openai/test-model",
                "max_output_tokens": "700", "max_action_runs": "5",
                "total_tokens_per_condition": "12000", "max_tokens_per_iteration": "4000",
            })
            races = [MapPackage(path).validate().race for path in service.packages]
            self.assertEqual(races[0]["model"], races[1]["model"])
            self.assertEqual(races[0]["budget"], races[1]["budget"])
            self.assertEqual(races[0]["iterations"], 3)
            self.assertEqual(json.loads(service.pair_path.read_text())["reviewed"], {})

    def test_invalid_token_budget_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.package(root)
            race_path = root / "config/race.yaml"
            race = race_path.read_text().replace("max_tokens_per_iteration: 500", "max_tokens_per_iteration: 1001")
            race_path.write_text(race)
            with self.assertRaisesRegex(PackageValidationError, "per-iteration token budget"):
                MapPackage(root).validate()

    def test_new_topology_executes_without_team_branch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.package(root)

            def execute(action, inputs, context):
                if action.id == "action0":
                    return ActionResult({"entity0": {"value": 1}}, {"entity0": "Ready"}, {}, {"kind": "made"})
                return ActionResult({"entity1": {"score": 1}, "entityR1": {"advice": "repeat"}}, {"entity1": "Complete"}, {}, {"kind": "ran"})

            controller = MapDrivenController(package, execute, "test-sim")
            manifest = controller.freeze(root / "manifest.json")
            self.assertEqual(manifest["status"], "frozen")
            controller.run_iteration(0)
            self.assertTrue((root / "iteration-0/entity1/current").exists())
            self.assertEqual(len((root / "iteration-0/events.jsonl").read_text().splitlines()), 2)


if __name__ == "__main__":
    unittest.main()


class DesignProjectionTests(unittest.TestCase):
    def test_project_design_drops_entity_metadata(self) -> None:
        from orchestrator.executors import project_design
        entity = {"geometry": {}, "controller": {}, "observation_request": {}, "learning": "x", "notes": "y", "approval": "z"}
        self.assertEqual(set(project_design(entity)), {"geometry", "controller", "observation_request"})

    def test_design_with_extra_metadata_passes_validate_package(self) -> None:
        from orchestrator.executors import project_design
        from orchestrator.validators import ValidationError, validate_package
        with self.assertRaises(ValidationError):
            validate_package({"geometry": {}, "controller": {}, "observation_request": {}, "notes": "x"}, {})
        # projection removes exactly the field that made validate_package reject the package
        self.assertEqual(set(project_design({"geometry": {}, "controller": {}, "observation_request": {}, "notes": "x"})), {"geometry", "controller", "observation_request"})


class RaceTitleTests(unittest.TestCase):
    def test_race_number_inserted_after_robot_race(self) -> None:
        from orchestrator.controller import race_title
        self.assertEqual(race_title("Robot Race — Optimizer Evaluator", "race-9"), "Robot Race 9 — Optimizer Evaluator")
        self.assertEqual(race_title("Robot Race — Randow Maps", "dry-run-x"), "Robot Race dry-run-x — Randow Maps")

    def test_clone_package_sets_title_on_base_only(self) -> None:
        import yaml
        from orchestrator.controller import clone_package
        templates = Path(__file__).resolve().parents[1] / "package-templates"
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "race-9-opt-eval"
            clone_package(templates / "opt-eval", dest, "race-9")
            self.assertEqual(yaml.safe_load((dest / "base.yaml").read_text())["map"]["title"], "Robot Race 9 — Optimizer Evaluator")
            self.assertNotIn("title", yaml.safe_load((dest / "scenario-iteration-0.yaml").read_text())["map"])


class TemplateCanonicalKeyTests(unittest.TestCase):
    NODE_KEYS = {"actors": {"id", "label", "notes", "map_link", "measures"}, "actions": {"id", "label", "actor", "notes", "map_link", "measures"}, "entities": {"id", "label", "system_boundary", "notes", "map_link", "measures"}, "edges": {"id", "type", "from", "to", "direction", "label", "notes"}}
    TEMPLATES = Path(__file__).resolve().parents[1] / "package-templates"

    def load(self, name: str) -> dict:
        import yaml
        return yaml.safe_load((self.TEMPLATES / name / "base.yaml").read_text())

    def test_every_template_element_uses_only_canonical_keys(self) -> None:
        for name in ("randow-maps", "opt-eval"):
            data = self.load(name)
            for section, allowed in self.NODE_KEYS.items():
                for item in data[section]:
                    self.assertFalse(set(item) - allowed, f"{name} {item['id']} has non-canonical keys {sorted(set(item) - allowed)}")

    def test_out_of_scope_private_entities_are_absent_and_feedback_is_required(self) -> None:
        import yaml
        for name in ("randow-maps", "opt-eval"):
            ids = {e["id"] for e in self.load(name)["entities"]}
            self.assertFalse(ids & {"entity3", "entityPrv0", "entityPrv1"})
            self.assertIn("entityR1", ids)
            runtime = yaml.safe_load((self.TEMPLATES / name / "actions" / "action1" / "runtime.yaml").read_text())
            self.assertIn("entityR1", runtime["required_outputs"])
            workflow = yaml.safe_load((self.TEMPLATES / name / "config" / "workflow.yaml").read_text())
            self.assertIn("entityR1", workflow["carry_forward"])

    def test_opt_eval_evaluator_approval_ends_the_revision_loop(self) -> None:
        from orchestrator.map_package import MapPackage
        package = MapPackage(self.TEMPLATES / "opt-eval").validate()
        ran = {"action0": ("entityR1:c",), "action1": ("entity0:a",)}  # R1 has a new version since action0 last ran
        rejected = {"entity0": "a", "entityR1": "d"}
        self.assertEqual(package.ready_actions(rejected, ran)[0], "action0")
        approved = {**rejected, "entity1": "b"}
        self.assertEqual(package.ready_actions(approved, ran), ["action2"])

    def test_design_outputs_carry_a_required_rationale_in_both_entrants(self) -> None:
        import json
        for name, entities in (("randow-maps", ("entity0", "entity1")), ("opt-eval", ("entity0",))):
            for entity in entities:
                contract = json.loads((self.TEMPLATES / name / "entities" / entity / "contract.schema.json").read_text())
                self.assertEqual(contract["required"][0], "rationale", f"{name} {entity}")
                self.assertEqual(next(iter(contract["properties"])), "rationale")

    def test_templates_use_block_style_not_flow_style(self) -> None:
        for name in ("randow-maps", "opt-eval"):
            text = (self.TEMPLATES / name / "base.yaml").read_text()
            self.assertNotIn("{", text)


class FailedRunTests(unittest.TestCase):
    SETTINGS = {"iterations": "1", "provider": "mock", "model_id": "deterministic-mock-v1", "max_output_tokens": "700", "max_action_runs": "5", "total_tokens_per_condition": "12000", "max_tokens_per_iteration": "4000"}

    def frozen(self, directory: str, race_id: str, **overrides: str) -> MapDrivenRaceService:
        service = MapDrivenRaceService(race_id, Path(directory)); service.prepare()
        service.configure_common({**self.SETTINGS, **overrides})
        service.review("randow-maps"); service.review("opt-eval"); service.freeze()
        return service

    def test_runtime_failure_is_recorded_and_race_can_be_retired(self) -> None:
        from orchestrator.race_service import RaceRunError
        with tempfile.TemporaryDirectory() as directory:
            service = self.frozen(directory, "fail-test")
            service._execute = lambda controllers, state: (_ for _ in ()).throw(RuntimeError("boom"))  # type: ignore[method-assign]
            with self.assertRaisesRegex(RaceRunError, "boom"):
                service.run()
            state = json.loads(service.pair_path.read_text())
            self.assertEqual(state["status"], "failed")
            self.assertEqual(state["error"]["message"], "boom")
            service.retire()
            self.assertEqual(json.loads(service.pair_path.read_text())["status"], "retired")
            with self.assertRaises(RuntimeError):
                service.retire()

    def test_openrouter_without_key_is_blocked_before_running(self) -> None:
        import os
        from orchestrator.race_service import PreRunCheckError
        with tempfile.TemporaryDirectory() as directory:
            service = self.frozen(directory, "key-test", provider="openrouter")
            saved = os.environ.pop("OPENROUTER_API_KEY", None)
            try:
                with self.assertRaisesRegex(PreRunCheckError, "no API key"):
                    service.run()
            finally:
                if saved is not None:
                    os.environ["OPENROUTER_API_KEY"] = saved
            self.assertEqual(json.loads(service.pair_path.read_text())["status"], "frozen")
            self.assertIn("looks like the offline mock", service.run_warnings()[0])

    def test_error_status_mapping(self) -> None:
        from http import HTTPStatus
        from orchestrator.race_service import RaceRunError, RaceStateError
        from orchestrator.web import error_status
        self.assertEqual(error_status(ValueError("x")), HTTPStatus.BAD_REQUEST)
        self.assertEqual(error_status(RaceStateError("x")), HTTPStatus.CONFLICT)
        self.assertEqual(error_status(RaceRunError("x")), HTTPStatus.INTERNAL_SERVER_ERROR)


class FieldDocsTests(unittest.TestCase):
    def test_every_form_setting_is_documented(self) -> None:
        import inspect
        import re
        from orchestrator import web
        from orchestrator.field_docs import FIELD_DOCS
        source = inspect.getsource(web)
        form_fields = set(re.findall(r'<(?:input|select|textarea)\b[^>]*?name="([a-z_]+)"', source)) - {"action", "entrant", "relative_path", "content"}
        self.assertTrue({"max_action_runs", "iterations", "model_id"} <= form_fields)
        self.assertEqual(sorted(form_fields - set(FIELD_DOCS)), [])
        for key, doc in FIELD_DOCS.items():
            for part in ("label", "scope", "summary", "details"):
                self.assertTrue(doc[part].strip(), f"{key}.{part} is empty")

    def test_page_and_docs_render_help(self) -> None:
        from orchestrator.field_docs import docs_page_body
        from orchestrator.web import page
        html_page = page("race-docs-test").decode()
        self.assertIn('class="help"', html_page)
        self.assertIn("/docs#max_action_runs", html_page)
        self.assertIn('id="max_action_runs"', docs_page_body())


class CanonicalValidatorWiringTests(unittest.TestCase):
    def test_package_with_stray_element_key_is_rejected(self) -> None:
        import shutil
        import yaml
        templates = Path(__file__).resolve().parents[1] / "package-templates"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "copy"
            shutil.copytree(templates / "opt-eval", root)
            base_path = root / "base.yaml"
            base = yaml.safe_load(base_path.read_text())
            base["entities"][3]["evaluations"] = "spurious key from an unquoted comma"
            base_path.write_text(yaml.safe_dump(base, sort_keys=False))
            with self.assertRaisesRegex(PackageValidationError, "non-canonical keys"):
                MapPackage(root).validate()

    def test_canonical_validator_rejects_missing_title(self) -> None:
        from orchestrator import canonical
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "base.yaml"
            path.write_text("map:\n  id: x\n  schema: v0.2\nactors: []\nactions: []\nentities: []\nedges: []\n")
            with self.assertRaisesRegex(ValueError, "title"):
                canonical.validate_map_file(path)


class LegacyRemovalTests(unittest.TestCase):
    def test_legacy_runner_and_model_client_are_gone(self) -> None:
        orchestrator = Path(__file__).resolve().parents[1] / "orchestrator"
        self.assertFalse((orchestrator / "runner.py").exists())
        self.assertFalse((orchestrator / "model_client.py").exists())
        for source in orchestrator.glob("*.py"):
            self.assertNotIn("ExperimentRunner", source.read_text(), source.name)
