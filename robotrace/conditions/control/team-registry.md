---
name: control-robotrace-team-registry
description: Control Robot Race role and artifact routing table. Source of truth for who generates and consumes each topology entity.
sources:
  - robotrace-control/base.yaml
  - robotrace/orchestrator/runner.py
last_updated: 2026-10-05
---

# Team Registry — Evaluator–Optimizer Control

Entity IDs reference `robotrace-control/base.yaml`. Entity descriptions and
topology wiring live there and are not duplicated here. This registry translates
that topology into role ownership and current harness paths.

## Role table

| | **Robot Optimizer** | **Evaluator** |
|---|---|---|
| **actorID** | actor0 | actor1 |
| **actionID** | action0 | action1 |
| **Role** | Produce and revise a complete robot candidate | Critique the current candidate and decide whether to revise or ship |
| **Private expertise** | `conditions/control/private/optimizer.md` | `conditions/control/private/evaluator.md` |
| **Shared coordination** | Reads and writes the Shared Blackboard (`entityTeam0`) | Reads and writes the Shared Blackboard (`entityTeam0`) |
| **Generates** | `entity0`, `entityPrv0`; contributes to `entityTeam0` | `entity1`, `entityR1`, `entityPrv1`; contributes to `entityTeam0` |
| **Consumes** | `entityR1`, `entityR2A`, `entityTeam0`, `entityPrv0` | `entity0`, `entityR2B`, `entityTeam0`, `entityPrv1` |

**RobotraceSim Robot** (`actor2`, `action2`) is deterministic software, not a
team member or model call. It consumes `entity1` and generates `entity2`,
`entityR2A`, and `entityR2B` from one canonical race measurement capture.
`entity2` is retained for audit and spectators; neither AI role consumes it.

## Entity routing and file locations

For race `race-N` and iteration `i`, the runtime root is
`runs/race-N/control/iteration-i/`. Packaged candidates and approved builds
carry manifests listing their files and allowed inputs.

| Entity | Written by | Runtime path | Read by |
|---|---|---|---|
| `entity0` — Complete Robot Candidate | Robot Optimizer | `blackboard/candidate-{cycle}/` | Evaluator |
| `entity1` — Approved Robot Build | Evaluator gates the selected candidate unchanged | `entity1/` | RobotraceSim Robot |
| `entity2` — Race Outcome | RobotraceSim Robot | `entity2/` | Audit and spectators only |
| `entityR1` — Evaluator Feedback | Evaluator when it requests revision | `entityR1/feedback-{cycle}.json` | Robot Optimizer in the next cycle |
| `entityR2A` — Race Data for Optimizer | RobotraceSim Robot | `return-geometry/` | Robot Optimizer in the next iteration |
| `entityR2B` — Race Data for Evaluator | RobotraceSim Robot | `return-integration/` | Evaluator in the next iteration |
| `entityTeam0` — Shared Blackboard | Both AI roles | `blackboard/`; initial criteria are frozen in `manifest.json` | Both AI roles |
| `entityPrv0` — Optimizer Expertise | Robot Optimizer in the topology | Checked-in seed at `conditions/control/private/optimizer.md` | Robot Optimizer only |
| `entityPrv1` — Evaluator Expertise | Evaluator in the topology | Checked-in seed at `conditions/control/private/evaluator.md` | Evaluator only |
| `entityPub0` — Track Conditions | Experiment operator | Frozen in `manifest.json`; source configuration under `config/` and `tracks/` | RobotraceSim Robot; constraints are also included in permitted model context |

The initial blackboard criteria come from the frozen race configuration, with
the checked-in default at `conditions/control/working-agreement-v0.md`.

## Iteration timing

The Robot Optimizer and Evaluator may alternate through `entity0` and
`entityR1` for multiple cycles while the shared budget remains. When the
Evaluator ships, `entity1` is an unchanged copy of the selected candidate.
The robot then races once. The two addressed race-data returns become
operational inputs in iteration `i+1`.

## Current harness note

Candidate and evaluation versions are persisted on the iteration blackboard.
Private expertise is still a fixed prompt input rather than a per-iteration
writable artifact. The current prompt assembly also supplies both previous
race-return records to both roles through one prior-state object, rather than
enforcing the map's separately addressed consumption routes. The generic runtime
directory names `return-geometry/` and `return-integration/` correspond to
control-map entities `entityR2A` and `entityR2B` respectively, despite their
LoopSense-oriented folder names. Treat these as implementation gaps, not as
different routing rules.
