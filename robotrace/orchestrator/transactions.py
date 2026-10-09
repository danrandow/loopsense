from __future__ import annotations

import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .io import atomic_write, digest, read_yaml, safe_child, write_json
from .map_package import MapPackage


class ScenarioTransaction:
    """Stage an action transition, then expose artifacts/scenario/event together."""

    def __init__(self, package: MapPackage, scenario_path: Path, iteration_dir: Path, action_id: str):
        self.package = package
        self.scenario_path = scenario_path.resolve()
        self.iteration_dir = iteration_dir.resolve()
        self.action_id = action_id
        self.id = uuid.uuid4().hex
        self.staging = safe_child(self.iteration_dir, ".transactions", self.id)
        self.artifacts: dict[str, dict[str, Any]] = {}
        self.overrides: dict[str, dict[str, dict[str, Any]]] = {}
        self.measurements: dict[str, list[dict[str, Any]]] = {}
        self.event: dict[str, Any] | None = None
        self.budget: dict[str, Any] | None = None

    def write_entity(self, entity_id: str, payload: dict[str, Any]) -> None:
        self.package.require_write(self.action_id, entity_id)
        self.package.validate_payload(entity_id, payload)
        self.artifacts[entity_id] = payload

    def update(self, section: str, element_id: str, *, label: str | None = None, notes: str | None = None, confidence: str | None = None) -> None:
        allowed = {"actors", "actions", "entities", "edges"}
        if section not in allowed:
            raise ValueError(f"invalid override section {section}")
        values = {key: value for key, value in {"label": label, "notes": notes, "confidence": confidence}.items() if value is not None}
        if confidence is not None and section != "edges":
            raise ValueError("confidence is edge-only")
        self.overrides.setdefault(section, {})[element_id] = {"id": element_id, **values}

    def append_measurement(self, element_id: str, measurement: dict[str, Any]) -> None:
        self.measurements.setdefault(element_id, []).append(measurement)

    def append_event(self, event_type: str, details: dict[str, Any]) -> None:
        if self.event is not None:
            raise ValueError("one work event is required per transaction")
        self.event = {
            "id": self.id, "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type, "action": self.action_id, **details,
        }

    def update_budget(self, budget: dict[str, Any]) -> None:
        self.budget = budget

    def commit(self, fail_at: str | None = None) -> None:
        if self.event is None:
            raise ValueError("transaction has no event")
        self.staging.mkdir(parents=True, exist_ok=False)
        scenario = read_yaml(self.scenario_path)
        for section, updates in self.overrides.items():
            existing = {item["id"]: item for item in scenario.setdefault("overrides", {}).setdefault(section, [])}
            existing.update(updates)
            scenario["overrides"][section] = list(existing.values())
        for element_id, values in self.measurements.items():
            scenario.setdefault("measurements", {})[element_id] = values
        atomic_write(self.staging / "scenario.yaml", yaml.safe_dump(scenario, sort_keys=False, allow_unicode=True))
        for entity_id, payload in self.artifacts.items():
            entity = self.staging / "artifacts" / entity_id
            write_json(entity / "payload.json", payload)
            write_json(entity / "version.json", {"transaction": self.id, "hash": digest(payload)})
        write_json(self.staging / "event.json", self.event)
        write_json(self.staging / "budget.json", self.budget or {})
        write_json(self.staging / "prepared.json", {"transaction": self.id, "state": "prepared"})
        if fail_at == "prepared":
            raise RuntimeError("forced transaction failure")

        backups = self.staging / "backups"
        backups.mkdir()
        shutil.copy2(self.scenario_path, backups / "scenario.yaml")
        events = self.iteration_dir / "events.jsonl"
        checkpoint = self.iteration_dir / "checkpoint.json"
        ledger = self.iteration_dir / "budget-ledger.json"
        old_events = events.read_bytes() if events.exists() else None
        old_checkpoint = checkpoint.read_bytes() if checkpoint.exists() else None
        old_ledger = ledger.read_bytes() if ledger.exists() else None
        moved: list[Path] = []
        try:
            for entity_id in self.artifacts:
                target = safe_child(self.iteration_dir, entity_id)
                if target.exists():
                    shutil.copytree(target, backups / entity_id)
                version = target / "versions" / self.id
                version.parent.mkdir(parents=True, exist_ok=True)
                os.replace(self.staging / "artifacts" / entity_id, version)
                moved.append(version)
                atomic_write(target / "current", self.id + "\n")
            if fail_at == "artifacts":
                raise RuntimeError("forced transaction failure")
            os.replace(self.staging / "scenario.yaml", self.scenario_path)
            if fail_at == "scenario":
                raise RuntimeError("forced transaction failure")
            with events.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(self.event, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            if fail_at == "event":
                raise RuntimeError("forced transaction failure")
            write_json(ledger, self.budget or {})
            if fail_at == "budget":
                raise RuntimeError("forced transaction failure")
            write_json(checkpoint, {"last_transaction": self.id, "state": "committed", "budget": self.budget or {}})
            if fail_at == "checkpoint":
                raise RuntimeError("forced transaction failure")
            write_json(self.staging / "committed.json", {"transaction": self.id, "state": "committed"})
        except Exception:
            os.replace(backups / "scenario.yaml", self.scenario_path)
            for entity_id in self.artifacts:
                target = safe_child(self.iteration_dir, entity_id)
                if (backups / entity_id).exists():
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(backups / entity_id, target)
                else:
                    for version in moved:
                        if version.parent.parent == target and version.exists():
                            shutil.rmtree(version)
                    current = target / "current"
                    if current.exists():
                        current.unlink()
            for target, previous in ((events, old_events), (checkpoint, old_checkpoint), (ledger, old_ledger)):
                if previous is None:
                    if target.exists():
                        target.unlink()
                else:
                    atomic_write(target, previous)
            raise


def recover_transactions(iteration_dir: Path) -> list[str]:
    """Reject prepared-but-uncommitted transitions deterministically on resume."""
    rejected: list[str] = []
    for path in sorted((iteration_dir / ".transactions").glob("*")) if (iteration_dir / ".transactions").exists() else []:
        if (path / "prepared.json").exists() and not (path / "committed.json").exists():
            write_json(path / "rejected.json", {"transaction": path.name, "state": "rejected"})
            rejected.append(path.name)
    return rejected
