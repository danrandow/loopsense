# Autonomous-session mechanics changelog

Per `CLAUDE.md`'s charter: harness/mechanics fixes (timeouts, retries, accounting, crashes, and the tests that
check them) are logged here rather than asked about. Design, scoring, and anything that changes what agents see
is not in scope for this file — see `PHASE0_FREEZE.md` and race reports for those.

## 2026-10-12 — Gate 1 (Phase 0) session

- **Reviewed the uncommitted working-tree diff** in `orchestrator/controller.py`, `executors.py`, `validators.py`
  and the two `race.yaml` templates (present at session start, not written by this session). It renames the
  budget block's ambiguous `model_actions_still_to_run_this_iteration` to clearer `action_runs_*` fields, adds
  `your_previous_calls` and `output_limit_tokens_this_call` to the per-call budget block, and tells a model
  explicitly when its previous answer was cut off at the output-token limit instead of surfacing a bare JSON
  parse error it cannot act on. Also raises `iterations` 6→12 and `total_tokens_per_condition` 1M→2M in both
  templates. Ran the full test suite against it before building anything on top: no regressions from this diff.
- **Fixed `tests/test_replicates.py::test_mock_replicates_use_own_dev_seed_and_shared_held_out_seeds`** (failing
  on HEAD before any of today's changes): it referenced `replicates.HELD_OUT_SEEDS`, a module constant removed in
  commit `cc14e40` when held-out seeds moved from a 5-seed module list to the template's own 20-seed list; the
  test was never updated and raised `AttributeError`. It also still asserted a single fixed dev seed per
  replicate (17, 29) from the pre-`cc14e40` single-seed scheme, when replicates have used a 20-seed block per
  replicate (1–20, 21–40, …) since that commit. Fixed the test to read held-out seeds from the template directly
  (so it can't drift from the template again) and to assert the correct per-replicate dev-seed block. Confirmed
  by checking out `orchestrator/progress.py`/`tests/test_progress.py` etc. at earlier revisions that this was a
  pre-existing bug, not something introduced by the session's own changes.
- **Fixed `tests/test_progress.py::test_quiet_running_race_is_flagged_stalled`** (also failing on HEAD, since the
  commit that introduced `orchestrator/progress.py`, `894c5ad`): the test's `make_race` helper wrote a
  rejected-attempt file via `Path.write_text`, which stamps the real wall-clock mtime, while every other
  timestamp in the test is a frozen historical instant (`T0`, dated 2026-10-09). `progress.py` correctly treats a
  rejected attempt's file mtime as activity, so `last_activity` picked up the real "now" (which is in the
  test's simulated "future" relative to `T0`), making `quiet_for_s` negative and the race look permanently
  active. This is a test-fixture bug, not a production one (in production `now` and mtimes are both the real
  clock). Fixed by giving the `write()` test helper an optional `mtime` and pinning the rejected-attempt file to
  `T0 + 10`, consistent with the rest of the fixture's frozen clock.
- Full suite (`python3 -m unittest discover -s tests`) is green: 126/126.
- Resolved the `max_steps` 300-vs-1200 ambiguity flagged in `SIMULATOR_REVIEW_AND_DESIGN_APPROACH.md` — see
  `PHASE0_FREEZE.md` §2. No code change: `config/experiment.yaml` (1200) is legacy and unread by any live race
  path; `race.yaml` (300) is what every race runs under and is achievable (designs finish in 1.9–2.4s).
- **Found, not yet fixed: the per-call `cost_usd` mechanism (added for Gate 8) under-reported actual spend in
  the Gate 9 replication batch.** Summed `cost_usd` across the 12 races' `events.jsonl` = $0.8770 (matching the
  $0.134/M-token rate seen in every earlier gate); the OpenRouter account's own usage ledger moved by $1.3920
  over the same window ($0.213/M tokens, ~60% above the established rate) — a real, unexplained gap, unlike
  Gate 8 where the two matched to the cent. Checked for the one known mechanism that *could* drop cost silently
  (an action that exhausts all repair attempts raises `ContractFailure`/`BudgetExhausted` without `spent_cost`,
  so a failed call's cost never reaches `events.jsonl`) and ruled it out: zero `action_rejected` or
  `budget_exhausted` events exist anywhere in this batch, only clean `action_completed`. Root cause not found
  from already-logged data; not fixed, since fixing a cost-accounting path without understanding why it failed
  risks hiding the next instance rather than catching it. Flagged to Dan in `GATE9_REPORT.md` as a safety-
  relevant finding, not treated as resolved.
