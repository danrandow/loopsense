"""What race evidence the agents see.

Two modes, set by evaluation.evidence_to_agents in race.yaml:

  full     the raw trial list including per-step telemetry (the original behaviour; very large with many seeds)
  summary  per-track aggregates over all trials: how many finished, how the others ended, and mean metrics

Summary mode lets a race use many seeds per track (which averages out simulator noise at no token cost) while the
prompt stays a few thousand tokens. Only the prompt view changes: the stored entity payload, the published trial
artefacts, the replay and the scores still hold every trial in full.
"""
from __future__ import annotations

from typing import Any

MODES = ("full", "summary")
METRICS = ("progress", "rms_error", "max_error", "line_loss_events", "steering_oscillation", "control_effort")


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def summarise_trials(trials: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-track aggregates of a trial list; no per-step telemetry and no per-trial rows."""
    by_track: dict[str, list[dict[str, Any]]] = {}
    for trial in trials:
        if isinstance(trial, dict):
            by_track.setdefault(str(trial.get("track")), []).append(trial)
    tracks: dict[str, Any] = {}
    for name, group in by_track.items():
        finished = [t for t in group if t.get("termination_reason") == "finished"]
        endings: dict[str, int] = {}
        for trial in group:
            reason = str(trial.get("termination_reason"))
            endings[reason] = endings.get(reason, 0) + 1
        metrics = {key: _mean([float(t["metrics"][key]) for t in group if isinstance(t.get("metrics"), dict) and t["metrics"].get(key) is not None]) for key in METRICS}
        scores = [float(t.get("score", 0)) for t in group]
        tracks[name] = {
            "trials": len(group), "finished": len(finished), "finish_rate": round(len(finished) / len(group), 3),
            "ended_by": endings, "mean_score": _mean(scores), "min_score": round(min(scores), 2), "max_score": round(max(scores), 2),
            "mean_finish_time_s": _mean([float(t["metrics"]["completion_time"]) for t in finished if isinstance(t.get("metrics"), dict) and t["metrics"].get("completion_time") is not None]),
            "mean_metrics": {key: value for key, value in metrics.items() if value is not None},
        }
    return tracks


def summarise_payload(value: Any) -> Any:
    """Replace every race-evidence trial list found in a payload with its per-track summary; leave everything else as is."""
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            if key == "trials" and isinstance(item, list) and item and all(isinstance(t, dict) and "track" in t for t in item):
                out["trials_summary"] = {"n_trials": len(item), "per_track": summarise_trials(item),
                                         "note": "Aggregated over all trials (several seeds per track). Per-step telemetry is not included."}
            else:
                out[key] = summarise_payload(item)
        return out
    if isinstance(value, list):
        return [summarise_payload(item) for item in value]
    return value


def mode_of(race: dict[str, Any]) -> str:
    return str((race.get("evaluation") or {}).get("evidence_to_agents", "full"))


def keep_telemetry(trials: list[dict[str, Any]], per_track: int | None) -> list[dict[str, Any]]:
    """Keep per-step telemetry for the first `per_track` trials of each track and drop it from the rest (scores and metrics stay).

    With many seeds per track, telemetry for every trial would make each stored payload and each published artefact
    tens of megabytes; this records a few trials of each track in full and the rest as results only."""
    if per_track is None:
        return trials
    seen: dict[str, int] = {}
    for trial in trials:
        track = str(trial.get("track"))
        seen[track] = seen.get(track, 0) + 1
        if seen[track] > per_track:
            trial["telemetry"] = []
    return trials
