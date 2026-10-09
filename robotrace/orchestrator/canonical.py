"""Bridge to the canonical Randow Maps validator (randow-maps/engine/render/validator.py).

The validator is the single source of truth for map structure. It is loaded by file path so
robotrace does not import the renderer package. Set RANDOW_MAPS_ROOT to the randow-maps checkout;
the default is ~/github/randow-maps. A missing validator is an error, never a silent skip.
"""
from __future__ import annotations

import importlib.util
import os
import warnings
from pathlib import Path
from types import ModuleType

import yaml

_cache: dict[Path, ModuleType] = {}


class CanonicalValidatorUnavailable(RuntimeError):
    pass


def validator_path() -> Path:
    root = Path(os.environ.get("RANDOW_MAPS_ROOT", "") or Path.home() / "github" / "randow-maps")
    return root / "engine" / "render" / "validator.py"


def _load() -> ModuleType:
    path = validator_path()
    if not path.is_file():
        raise CanonicalValidatorUnavailable(f"canonical Randow Maps validator not found at {path}; set RANDOW_MAPS_ROOT to the randow-maps checkout")
    if path not in _cache:
        spec = importlib.util.spec_from_file_location("randow_maps_canonical_validator", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _cache[path] = module
    return _cache[path]


def validate_map_file(path: Path) -> None:
    """Validate one topology or scenario file. Raises ValueError with the validator's message."""
    validator = _load()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # warnings are advisory (e.g. scenarios omit map.title by design); errors raise ValueError
        validator.validate_map(data, source=str(path))


# Element keys defined by randow-maps docs/schema.yaml. The canonical validator does not reject unknown
# keys, so a stray key (e.g. from an unquoted comma in a flow-style `notes`) must be caught here.
ELEMENT_KEYS = {
    "actors": {"id", "label", "notes", "map_link", "measures"},
    "actions": {"id", "label", "actor", "notes", "map_link", "measures"},
    "entities": {"id", "label", "system_boundary", "notes", "map_link", "measures"},
    "edges": {"id", "type", "from", "to", "direction", "label", "notes"},
}


def check_element_keys(topology: dict) -> None:
    for section, allowed in ELEMENT_KEYS.items():
        for item in topology.get(section) or []:
            extra = set(item) - allowed
            if extra:
                raise ValueError(f"{section} element {item.get('id')!r} has non-canonical keys {sorted(extra)}")
