---
name: loopsense-robotrace-team-registry
description: LoopSense Robot Race role and artifact routing table. Source of truth for who generates and consumes each topology entity.
sources:
  - robotrace/base.yaml
  - robotrace/orchestrator/runner.py
last_updated: 2026-10-05
---

# Team Registry — LoopSense Robot Race

Entity IDs reference `robotrace/base.yaml`. Entity descriptions and topology
wiring live there and are not duplicated here. This registry translates that
topology into role ownership and current harness paths.

## Role table

| | **Geometry Builder** | **Robot Integrator** |
|---|---|---|
| **actorID** | actor0 | actor1 |
| **actionID** | action0 | action1 |
| **Role** | Design bounded robot geometry | Integrate the geometry with a controller |
| **Private expertise** | `conditions/loopsense/private/geometry.md` | `conditions/loopsense/private/integration.md` |
| **Shared coordination** | Reads the Working Agreement (`entityTeam0`) | Reads the Working Agreement (`entityTeam0`) |
| **Generates** | `entity0`, `entityPrv0`; may revise `entityTeam0` in the topology | `entity1`, `entityR1`, `entityPrv1`; may revise `entityTeam0` in the topology |
| **Consumes** | `entityR1`, `entityR2A`, `entityTeam0`, `entityPrv0` | `entity0`, `entityR2B`, `entityTeam0`, `entityPrv1` |

**RobotraceSim Robot** (`actor2`, `action2`) is deterministic software, not a
team member or model call. It consumes `entity1` and generates `entity2`,
`entityR2A`, and `entityR2B` from one canonical race measurement capture.
`entity2` is retained for audit and spectators; neither AI role consumes it.

## Entity routing and file locations

For race `race-N` and iteration `i`, the runtime root is
`runs/race-N/loopsense/iteration-i/`. Packaged forward entities and integration
feedback carry manifests listing their files and allowed inputs.

| Entity | Written by | Runtime path | Read by |
|---|---|---|---|
| `entity0` — Geometry Proposal | Geometry Builder | `entity0/` | Robot Integrator |
| `entity1` — Complete Robot Package | Robot Integrator | `entity1/` | RobotraceSim Robot |
| `entity2` — Race Outcome | RobotraceSim Robot | `entity2/` | Audit and spectators only |
| `entityR1` — Integration Feedback | Robot Integrator after the race | `entityR1/feedback.json` | Geometry Builder in the next iteration |
| `entityR2A` — Race Data for Geometry | RobotraceSim Robot | `return-geometry/` | Geometry Builder in the next iteration |
| `entityR2B` — Race Data for Integration | RobotraceSim Robot | `return-integration/` | Robot Integrator in the next iteration |
| `entityTeam0` — Working Agreement | Initial race configuration; topology permits both agents to revise it | Frozen in `manifest.json`; checked-in default at `conditions/loopsense/working-agreement-v0.md` | Both AI roles |
| `entityPrv0` — Geometry Expertise | Geometry Builder in the topology | Checked-in seed at `conditions/loopsense/private/geometry.md` | Geometry Builder only |
| `entityPrv1` — Integration Expertise | Robot Integrator in the topology | Checked-in seed at `conditions/loopsense/private/integration.md` | Robot Integrator only |
| `entityPub0` — Track Conditions | Experiment operator | Frozen in `manifest.json`; source configuration under `config/` and `tracks/` | RobotraceSim Robot; constraints are also included in permitted model context |

## Iteration timing

The Geometry Builder acts first, then the Robot Integrator, then the robot
races. After the race, the Robot Integrator produces `entityR1`. The three
return entities generated in iteration `i` become operational inputs only in
iteration `i+1`; there is no separate retrospective turn.

## Current harness note

The topology allows both agents to update `entityTeam0` and depicts their
private expertise as evolving. In the current harness, the Working Agreement
and private expertise are fixed prompt inputs rather than per-iteration writable
artifacts. Also, the Geometry Builder currently receives the complete previous
return bundle, including the integration-addressed race return, rather than only
the topology-prescribed inputs. Treat these as implementation gaps, not as
different routing rules.
