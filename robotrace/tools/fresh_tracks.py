#!/usr/bin/env python3
"""Fresh same-family tracks: the primary metric's zero-token-cost evaluation path (PHASE0_FREEZE.md §4b).

A dev-family track is defined by {family, difficulty, length} (`simulator/adapter/headless.py`'s
`_track_polyline` is a pure function of exactly those three fields). The existing held-out tracks are already
just resampled dev-family parameters with a flag flipped (e.g. dev `slalom` is difficulty 0.25, length 22.0;
held-out `slalom-b` is the SAME family, difficulty 0.45, length 20.0) -- this module generates more of the
same, at a fixed, recorded seed, for tracks the agent's own tool/evidence path never shows it (only the three
literal dev tracks oval/s-bend/slalom, at their one fixed parameter setting, ever appear there).

FRESH_TRACK_SEED is fixed and recorded in PHASE0_FREEZE.md §4b; do not change it without a new freeze entry.
"""
from __future__ import annotations

import random
import statistics
from typing import Any

FRESH_TRACK_SEED = 777
DEV_FAMILIES = ("oval", "s-bend", "slalom")
N_FRESH_PER_FAMILY = 3

# The existing dev track's own {difficulty, length}, used as the centre each family's fresh tracks are sampled
# around (tracks/development/*.json, tracks/anchor/oval.json).
DEV_TRACK_CENTRE = {"oval": {"difficulty": 0.35, "length": 20.0}, "s-bend": {"difficulty": 0.55, "length": 24.0}, "slalom": {"difficulty": 0.25, "length": 22.0}}
DIFFICULTY_SPREAD, LENGTH_SPREAD = 0.20, 3.0  # +/-, matching the scale of the difficulty/length gap already seen between a dev track and its held-out counterpart


def generate_fresh_tracks(seed: int = FRESH_TRACK_SEED, families: tuple = DEV_FAMILIES, n_per_family: int = N_FRESH_PER_FAMILY) -> dict[str, dict[str, Any]]:
    """Deterministic given `seed`: same seed always returns the same tracks."""
    rng = random.Random(seed)
    tracks = {}
    for family in families:
        centre = DEV_TRACK_CENTRE[family]
        for i in range(n_per_family):
            difficulty = max(0.05, min(0.95, centre["difficulty"] + rng.uniform(-DIFFICULTY_SPREAD, DIFFICULTY_SPREAD)))
            length = max(10.0, min(30.0, centre["length"] + rng.uniform(-LENGTH_SPREAD, LENGTH_SPREAD)))
            track_id = f"{family}-fresh-{i}"
            tracks[track_id] = {"id": track_id, "family": family, "difficulty": round(difficulty, 3), "length": round(length, 2), "tape_width": 0.025, "held_out": False}
    return tracks


def primary_metric(design: dict, dev_tracks: dict[str, dict], config: dict, seeds: list[int], fresh_tracks: dict[str, dict] | None = None) -> dict:
    """Mean score over the three literal dev tracks AND the fresh same-family tracks, on the given (fresh
    validation) seeds -- the primary comparison metric per PHASE0_FREEZE.md §4b. dev_tracks must already
    contain oval/s-bend/slalom (tools/baseline_search.load_tracks()); fresh_tracks defaults to
    generate_fresh_tracks() at the frozen seed."""
    from simulator.adapter.headless import run_trial
    fresh_tracks = fresh_tracks if fresh_tracks is not None else generate_fresh_tracks()
    all_tracks = {**{name: dev_tracks[name] for name in DEV_FAMILIES}, **fresh_tracks}
    per_track = {}
    for name, track in all_tracks.items():
        trials = [run_trial(design, track, seed, config) for seed in seeds]
        scores = [float(t["score"]) for t in trials]
        per_track[name] = {"mean": statistics.mean(scores), "finish_rate": sum(t.get("termination_reason") == "finished" for t in trials) / len(trials)}
    return {"mean": statistics.mean(v["mean"] for v in per_track.values()), "tracks": per_track}


if __name__ == "__main__":
    import json
    print(json.dumps(generate_fresh_tracks(), indent=1))
