# Start here

## What was tested, and the headline result

Across ~20 gates, this project tested whether a second LLM agent (reviewer, critic, or geometry/controller
split) helps a single Haiku 5.5 agent design a better simulated line-following robot than the same agent
working alone, under a fixed 12-iteration budget with no simulator tool access. **It doesn't, in any form
tried**: a lone agent (opt-solo) decisively beats both two-agent topologies tested (opt-eval and
randow-maps) and a third, more elaborate critique structure (opt-eval-pre2, two advisory rounds before
racing) on the pre-registered out-of-sample metric, and **the first critique-and-revise round degrades the
design 96.5% of the time** (across 85 iterations, mean −344) — traced to the critic confidently, and sometimes
wrongly, asserting the current design doesn't work. Giving a team explicit permission to hold geometry and
decline advice (randow-maps-dialogue) produced a large behavioural shift (3x more holding) but not yet a
statistically confirmed score change at n=8.

## Where to look

- **`FINDINGS.md`** — the one-page results table and plain-language summary. Start here for numbers.
- **`PHASE0_FREEZE.md`** — every pre-registered decision rule (§4a onward), committed before the race data
  it governs existed. The audit trail for "was this decided before or after seeing the result."
- **`GATE*_REPORT.md`** — one per gate, in order, with full method and the data behind every FINDINGS.md
  number. Gate 14 doesn't exist as its own file; its leftover work was finished inside Gate 19's report.
- **`CLAUDE.md`** — the standing mandate, charter rules, and the running cost/ops log (balance-endpoint
  history, per-call cost mechanics, every correction made along the way).
- **`package-templates/<arm>/base.yaml`** — the actual instruction text each arm's agents receive. The
  ground truth for "what was this team actually told," not a paraphrase.

## Running one race

No CLI "run" command exists yet — races are launched from a short Python script. The pattern, in full:

```python
from pathlib import Path
from orchestrator.controller import MapDrivenController, clone_package
from orchestrator.map_package import MapPackage
from orchestrator.executors import PackageExecutor

clone = clone_package(Path("package-templates/<arm>"), Path("race-<N>-<arm>"), "race-<N>")
# set clone/config/race.yaml's model.provider/model.id here if not already "openrouter"/the target model
package = MapPackage(clone).validate()
controller = MapDrivenController(package, PackageExecutor(package), package.race["simulator"]["version"])
for i in range(12):
    controller.run_iteration(i)
```

`python3 -m orchestrator.controller validate <package>` checks a template before spending anything.
`python3 -m unittest discover -s tests` (or `pytest`) must pass before building on uncommitted changes.

**Cost rule:** check both `https://openrouter.ai/api/v1/credits` (`total_credits - total_usage` — real
account balance) and `https://openrouter.ai/api/v1/auth/key` (`limit_remaining` — a separate, smaller
per-key hard cap; hitting it 403s every call regardless of real balance). **Stop issuing new calls when the
smaller of the two is within $0.50 of zero.** Use each race's own summed `cost_usd` (from `events.jsonl`,
read directly off the OpenRouter response) as the real-time per-race guard — not a polled balance, which
lags (see gotchas).

## Known gotchas

- **Gate 11 re-entry defect.** Removing a topology edge that was the *only* source of "new inputs" for an
  `on_new_inputs` reentry trigger silently stops that action from ever re-firing — the race stalls
  (`"workflow stalled: no action can run"`), not crashes. Check this explicitly before building any arm
  that removes an edge (muted variants); confirm with a mock smoke test before spending.
- **`/credits` lags, sometimes by 10+ minutes** — confirmed reading the same stale figure across an entire
  race wave despite real spend happening. It's right for an absolute balance check, wrong as a real-time
  guard. `/auth/key`'s `limit_remaining` is a different number (a provisioned spending cap, not real
  money) — both must be checked, and you stop on whichever is smaller.
- **Concurrent-load timeouts.** Heavier, multi-call-per-iteration templates (e.g. opt-eval-pre2) have hit
  `TimeoutError` under 4-way concurrency mid-race. Rerun once; a rerun that also faults is not retried
  again.
- **Per-race token budgets bite heavier topologies.** A fixed total-token budget that comfortably covers a
  12-iteration race for a lightweight arm can run out before iteration 12 for a 5-6-call-per-iteration
  pipeline (opt-eval-pre2 measured ~182k tokens/iteration vs. opt-solo's ~25k) — check the per-iteration
  token rate for any new topology before assuming 12 iterations will complete.

## Ideas to revisit, in this order

1. **An orchestrator-style team forked from the original LoopSense setup** — a genuinely different team
   shape built from first principles, not another muted/permissive variant of the two topologies already
   tested.
2. **A grounded second agent, matched by giving opt-solo the same check.** Every two-agent topology tested
   so far adds an ungrounded critic; before concluding "a second agent never helps," test whether a single
   agent given the *same specific check* the critic was supposed to perform (e.g. "does this design
   actually complete") closes the gap on its own — isolating whether the check matters, independent of
   whether a second voice delivers it.
3. **Reasoning enabled for all arms.** Confirmed (Gate 16): no `reasoning`/`thinking` parameter has ever
   been set on any call in this project. Untested whether any of the above results change with it on.
4. **A stronger model, or more iterations.** Neither has been tested on any topology here.

## Scope

Everything above is **one model** (Haiku 5.5), **one task** (this simulated line-following robot), **no
simulator tool access for any agent**, and **12 iterations per race**. Nothing here has been tested outside
that envelope.
