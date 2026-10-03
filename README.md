# LoopSense experiments

This repository contains experiments exploring how AI-agent work can be shaped and evaluated through explicit feedback loops.

## Current focus: Robot Race

The active experiment is **[Robot Race](robotrace/README.md)**: a local, deterministic, and auditable harness for comparing two agent conditions as they iteratively design robot-control packages and race them in a simulator.

Robot Race is currently set up for offline smoke runs using a bundled deterministic model and headless simulator contract. These runs exercise the full orchestration, validation, measurement, telemetry, leaderboard, and audit trail, but their scores are not experimental evidence. A recorded experiment still requires the real simulator and model provider to be pinned and configured, followed by a frozen, tagged experimental setup.

See the [Robot Race README](robotrace/README.md) for how to run or validate the harness, the current simulator boundary, the recorded-run gate, and the generated artifact layout.

## Original LoopSense experiment

The original **[LoopSense experiment](loopsense/README.md)** explored a file-based method for routing real-world outcomes back to teams of AI agents through named return flows. That work is currently set aside, but remains in this repository as the conceptual and historical foundation for the newer experiment.

## License

Licensed under the [Apache License 2.0](LICENSE).
