from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from orchestrator.map_package import MapPackage, PackageValidationError
from orchestrator.validators import ValidationError, design_bounds_from_contract, validate_controller

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "package-templates"
CONTRACT = "entities/entityPub0/contract.schema.json"


def load(template: str) -> dict:
    return json.loads((TEMPLATES / template / CONTRACT).read_text())


def walk(schema: dict, path: str = ""):
    yield path, schema
    for name, child in (schema.get("properties") or {}).items():
        yield from walk(child, f"{path}/{name}")
    if isinstance(schema.get("items"), dict):
        yield from walk(schema["items"], f"{path}[]")


class DesignContractTests(unittest.TestCase):
    def test_templates_share_one_contract(self):
        self.assertEqual(load("opt-eval"), load("randow-maps"))

    def test_every_field_is_described(self):
        for path, schema in walk(load("randow-maps")):
            self.assertTrue(str(schema.get("description", "")).strip(), f"{path or 'root'} has no description")

    def test_bounds_come_from_the_contract_and_match_the_legacy_limits(self):
        legacy = yaml.safe_load((ROOT / "config/experiment.yaml").read_text())["design_bounds"]
        derived = design_bounds_from_contract(load("randow-maps"))
        for key, value in legacy.items():
            if key != "controller":
                self.assertEqual(derived[key], value, key)
        self.assertEqual(derived["controller"]["kp"], [0, 20])
        self.assertEqual(derived["controller"]["sensor_weight"], [-2, 2])

    def test_race_yaml_carries_no_bounds(self):
        for template in ("opt-eval", "randow-maps"):
            race = yaml.safe_load((TEMPLATES / template / "config/race.yaml").read_text())
            self.assertNotIn("design_bounds", race)

    def test_package_derives_bounds_and_rejects_a_conflicting_race_yaml(self):
        package = MapPackage(TEMPLATES / "randow-maps").validate()
        self.assertTrue(package.bounds_in_contract)
        self.assertEqual(package.race["design_bounds"]["mass"], [0.4, 1.5])
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "randow-maps"
            shutil.copytree(TEMPLATES / "randow-maps", copy)
            race_path = copy / "config/race.yaml"
            race = yaml.safe_load(race_path.read_text())
            race["design_bounds"] = {**package.race["design_bounds"], "mass": [0.1, 9]}
            race_path.write_text(yaml.safe_dump(race))
            with self.assertRaises(PackageValidationError):
                MapPackage(copy).validate()

    def test_controller_limits_are_enforced(self):
        bounds = design_bounds_from_contract(load("randow-maps"))
        good = {"base_speed": 1, "kp": 3, "ki": 0, "kd": 0.2, "sensor_weights": [-1, 0, 1], "line_loss": "stop"}
        validate_controller(good, 3, bounds)
        for field, value in (("kp", 21), ("base_speed", 3), ("sensor_weights", [-3, 0, 1])):
            with self.assertRaises(ValidationError, msg=field):
                validate_controller({**good, field: value}, 3, bounds)


if __name__ == "__main__":
    unittest.main()
