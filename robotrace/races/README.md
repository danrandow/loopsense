# Race data

Every race package (`race-N-<entrant>/`, `dry-run-N-<entrant>/`), its status file
(`race-N-pair.json`), and its leaderboard, report and replay artefacts
(`race-N-leaderboard.json`, `race-N-race-report.md`, `race-N-replay.html`) live here.

## Where this moved from

All of it previously lived loose at the **git repository root** (`/race-N-<entrant>/`,
`/race-N-pair.json`, etc.) — a long-running convention from before this repo held more than one
project. A small number of races (105-107) had instead ended up directly under `robotrace/` itself,
inconsistently. Both sets are now here, unified, with no content change: every move was a plain
`git mv`, so each race's file history is intact (`git log --follow` still works).

`race-40-replicates.md` (the comparison summary `replicates.py compare` writes) moved the same way.

## If a script still points at the old location

`orchestrator/race_service.py`, `orchestrator/progress.py`, and `orchestrator/web.py` all default to
this directory now (`robotrace/races/`), not the repo root. `replicates.py`'s `--workspace` default
moved the same way — `--workspace` still works if you want somewhere else. If you have an older
script or note pointing at the repo root or at `robotrace/race-N-...`, point it here instead.
