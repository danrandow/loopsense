# LoopSense Robot Race experiment

This directory implements the experiment specified in `IMPLEMENTATION_PLAN.md`. It is intentionally local, deterministic, auditable, and safe by construction: model output is validated data, never executable code or a path.

## Run the offline smoke experiment

From this directory:

```sh
python3 -m orchestrator.runner
```

This validates configuration, runs two iterations for both conditions with the bundled deterministic mock model, races exactly one selected package per condition and iteration, and writes the complete spectator/audit record under `runs/robotrace-smoke/`.

To verify without running:

```sh
python3 -m orchestrator.runner --validate-only
python3 -m unittest discover -s tests -v
```

To resume an interrupted run without replaying completed calls or trials:

```sh
python3 -m orchestrator.runner --resume
```

## Current simulator boundary

`simulator/adapter/headless.py` is a deterministic, headless contract implementation used to build and test the entire harness before pinning RobotTraceSim. It provides explicit seeds, constrained observations, termination reasons, metrics, telemetry, and stable JSON. It does **not** claim to be RobotTraceSim physics. Before a recorded experiment, replace this implementation behind the same `run_trial` contract with the pinned upstream simulator and record the upstream commit and MIT license in `simulator/upstream/`.

## Recorded-run gate

The checked-in configuration is deliberately marked `mode: smoke` and uses `provider: mock`. Do not interpret its scores as experimental evidence. A recorded run requires:

1. pinning and adapting RobotTraceSim;
2. adding an explicit model provider adapter;
3. freezing model settings, score weights, geometry bounds, budgets, tracks, and run length;
4. running and resetting the two disposable smoke iterations;
5. tagging the exact configuration before starting.

## Artifact layout

Each run contains a top-level manifest, immutable JSONL audit log, hashed result records, shared leaderboard, and per-condition iteration folders. Each iteration contains context manifests, budget ledgers, entities, two independently addressed measurement returns, telemetry, trajectory SVGs, a summary SVG, a public-link scenario map, and an atomic completion checkpoint.

