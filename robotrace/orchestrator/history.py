"""Per-actor history packs.

Agents are single model calls with no file access, so anything an actor remembers has to be compiled into
its prompt by the orchestrator. A pack is a view over the race package, built from the iteration folders that
already exist; it stores nothing new. It contains only entities the topology authorises the actor to read or
write, so an actor never sees more of its past than it could have seen at the time.

For every earlier iteration the pack holds what the actor produced, what it received that was generated in that
iteration (race data describes the robot raced in the same iteration), and a one-line outcome row joining the
design values the actor can see with the race result. Per-step telemetry is kept newest-first until a token
ceiling is reached; older race data keeps its metrics but loses the per-step telemetry.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from .io import digest

CHARS_PER_TOKEN = 3  # conservative for number-heavy packed telemetry (measured at about 3.3)
DESIGN_KEYS = ("geometry", "controller")
TRIAL_KEEP = ("track", "seed", "termination_reason", "score", "metrics")
ROW_METRICS = ("completion", "progress", "line_loss_events", "rms_error", "max_error")
TELEMETRY_OMITTED = "omitted: older iteration, metrics only"
FOOTER_TOKENS = 100  # the small "telemetry" summary appended after the pack is sized

Pack = Callable[[Any], "tuple[Any, bool]"]

ABOUT = (
    "Your own earlier iterations, oldest first. 'produced' is what you wrote in that iteration. 'received' is what was "
    "generated for you in that iteration; race data describes the robot raced in that same iteration, and feedback "
    "describes the candidate of that iteration (you read it in the next one). 'same_as_authorized_input' means the "
    "entity is identical to one already supplied in authorized_inputs. outcome_table lines up, for each iteration, the "
    "design values you are authorised to see with the race result. Per-step telemetry is kept for the most recent race "
    "data that fits the token ceiling; older race data keeps its metrics only."
)


def estimate_tokens(value: Any, pack: Pack) -> int:
    packed, _ = pack(value)
    return -(-len(json.dumps(packed, sort_keys=True, separators=(",", ":"))) // CHARS_PER_TOKEN)


def has_telemetry(payload: Any) -> bool:
    trials = payload.get("trials") if isinstance(payload, dict) else None
    return isinstance(trials, list) and any(isinstance(trial, dict) and trial.get("telemetry") for trial in trials)


def metrics_only(payload: dict[str, Any]) -> dict[str, Any]:
    kept = {key: value for key, value in payload.items() if key != "trials"}
    kept["trials"] = [
        {**{key: trial[key] for key in TRIAL_KEEP if key in trial}, "telemetry": TELEMETRY_OMITTED}
        for trial in payload["trials"] if isinstance(trial, dict)
    ]
    return kept


def _load_iteration(root: Path, iteration: int, reads: frozenset[str], writes: frozenset[str]) -> dict[str, Any] | None:
    base = root / f"iteration-{iteration}"
    if not base.is_dir():
        return None
    record: dict[str, Any] = {"iteration": iteration, "complete": True, "produced": {}, "received": {}}
    outcome = base / "outcome.json"
    if outcome.is_file():
        data = json.loads(outcome.read_text(encoding="utf-8"))
        record["complete"] = bool(data.get("complete"))
        if not record["complete"] and data.get("reason"):
            record["incomplete_reason"] = data["reason"]
    for entity_dir in sorted(path for path in base.iterdir() if path.is_dir() and not path.name.startswith(".")):
        entity_id = entity_dir.name
        if entity_id not in reads | writes or not (entity_dir / "current").is_file():
            continue
        version = (entity_dir / "current").read_text(encoding="utf-8").strip()
        payload_path = entity_dir / "versions" / version / "payload.json"
        # A carried version was generated in an earlier iteration and is already in that iteration's record.
        if version.startswith("carried-") or not payload_path.is_file():
            continue
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            record["produced" if entity_id in writes else "received"][entity_id] = payload
    return record


def _design(record: dict[str, Any]) -> dict[str, Any]:
    design: dict[str, Any] = {}
    for bucket in ("produced", "received"):
        for payload in record[bucket].values():
            for key in DESIGN_KEYS:
                if key not in design and isinstance(payload.get(key), dict):
                    design[key] = payload[key]
    return design


def _outcome(record: dict[str, Any]) -> dict[str, Any] | None:
    for bucket in ("received", "produced"):
        for payload in record[bucket].values():
            if isinstance(payload.get("trials"), list):
                return {"score": payload.get("score"), "trials": [
                    {"track": trial.get("track"), "termination_reason": trial.get("termination_reason"), "score": trial.get("score"),
                     **{key: (trial.get("metrics") or {}).get(key) for key in ROW_METRICS}}
                    for trial in payload["trials"] if isinstance(trial, dict)
                ]}
    return None


def _view(record: dict[str, Any], input_digests: dict[str, str]) -> dict[str, Any]:
    """The record as shown: received entities already supplied as authorized inputs are replaced by a reference."""
    shown = {key: value for key, value in record.items() if key not in ("produced", "received")}
    shown["produced"] = dict(record["produced"])
    shown["received"] = {
        entity_id: ({"same_as_authorized_input": input_digests[digest(payload)]} if digest(payload) in input_digests else payload)
        for entity_id, payload in record["received"].items()
    }
    return shown


def build_history(
    root: Path, *, reads: frozenset[str], writes: frozenset[str], iteration: int, inputs: dict[str, dict[str, Any]],
    settings: dict[str, Any] | None, pack: Pack, pack_cap: int | None = None,
) -> dict[str, Any] | None:
    """Compile one actor's history of iterations 0..iteration-1, or None when disabled or there is nothing yet.

    telemetry_token_ceiling bounds all per-step telemetry in the prompt, including the latest race data already in
    authorized_inputs; older race data is dropped to metrics oldest-first. pack_cap, when given, bounds the whole
    pack (derived by the caller from the remaining token budget); iteration detail is then dropped oldest-first,
    keeping the outcome table, until it fits."""
    if not settings or not settings.get("enabled", True):
        return None
    records = [r for r in (_load_iteration(root, k, reads, writes) for k in range(iteration)) if r]
    if not records:
        return None
    input_digests = {digest(payload): entity_id for entity_id, payload in inputs.items()}
    table = [{"iteration": r["iteration"], "design": _design(r), "outcome": _outcome(r), **({"incomplete_reason": r["incomplete_reason"]} if "incomplete_reason" in r else {})} for r in records]
    views = [_view(r, input_digests) for r in records]
    heavy = [(i, entity_id) for i, view in enumerate(views) for entity_id, payload in view["received"].items() if has_telemetry(payload)]
    originals = {(i, entity_id): views[i]["received"][entity_id] for i, entity_id in heavy}
    for i, entity_id in heavy:
        views[i]["received"][entity_id] = metrics_only(originals[(i, entity_id)])

    def assemble(details: list[dict[str, Any]]) -> dict[str, Any]:
        return {"about": ABOUT, "outcome_table": table, "iterations": details}

    ceiling = int(settings.get("telemetry_token_ceiling", 0))
    allowance = ceiling - sum(estimate_tokens(payload, pack) for payload in inputs.values() if has_telemetry(payload))
    if pack_cap is not None:
        allowance = min(allowance, pack_cap - FOOTER_TOKENS - estimate_tokens(assemble(views), pack))
    full: list[int] = []
    for i, entity_id in reversed(heavy):  # newest first; the first race data that does not fit closes the block
        cost = estimate_tokens(originals[(i, entity_id)], pack)
        if cost > allowance:
            break
        allowance -= cost
        views[i]["received"][entity_id] = originals[(i, entity_id)]
        full.append(records[i]["iteration"])
    details = views
    omitted: list[int] = []
    if pack_cap is not None:
        details = [dict(view) for view in views]
        for view in details:  # oldest first
            if estimate_tokens(assemble(details), pack) <= pack_cap - FOOTER_TOKENS:
                break
            omitted.append(view["iteration"])
            view["produced"], view["received"] = {}, {}
            view["detail"] = "omitted to fit the token budget; see outcome_table"
    history = assemble(details)
    history["telemetry"] = {"ceiling_tokens": ceiling, "full_telemetry_iterations": sorted(full)}
    if omitted:
        history["telemetry"]["detail_omitted_iterations"] = sorted(omitted)
    return history
