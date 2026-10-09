# Harness changes for race 16

These change what the agents see and how runs are scored, so scores are **not comparable with races 0–15**.
Both entrants get identical settings (enforced by the pair check in `validate_pair`, which now also compares `objective`).

| Change | Where |
|---|---|
| `entityR2A` / `entityR2B` carry the full development trials, including per-step telemetry (`entity2` is unchanged and stays for humans). | `package-templates/*/entities/entityR2{A,B}/contract.schema.json`, `orchestrator/executors.py` (`_simulator`) |
| Per-step telemetry is column-packed in the prompt (lossless; `step` is the row index, `line_lost` is 0/1) and the prompt JSON is minified. A `telemetry_format` note explains the packing. | `orchestrator/executors.py` (`compact_telemetry`, `_openrouter`) |
| Every model action is told the objective: maximise the score, judged once after the last iteration on an unseen track of a different shape. The scoring formula is generated from the race weights and the adapter constants, so it cannot drift from the code. The held-out track names and seeds are never shown. | `config/race.yaml` → `objective`; `orchestrator/executors.py` (`objective_for_prompt`); `simulator/adapter/headless.py` (`score_description`) |
| Robustness and precision are multiplied by progress (1 for a completed run). A robot that does not move scores 0 instead of 175. Completed runs score exactly as before. | `simulator/adapter/headless.py` (`_score`) |
| New `stalled` ending: a run ends when progress rises by less than `stall_min_progress` (0.002) over `stall_steps` (50) steps. A stationary robot now produces ~51 telemetry rows instead of 300. | `config/race.yaml` → `simulator`; `simulator/adapter/headless.py`; `orchestrator/artifacts.py` (track view marker "S") |
| Template defaults: 6 iterations, 250,000 tokens per entrant, 40,000 per iteration. (The web form can still override these.) | `package-templates/*/config/race.yaml` |
| Race report links every iteration, not just 0 and 1. | `orchestrator/race_service.py` |

Not changed: the `observation_request` field is still accepted and still ignored. Both agents receive the same full evidence.

Tests: `tests/test_race16.py`.
