# Phase 1 results: does a single LLM agent beat the free baseline? (Gate 2)

Written 2026-10-12, after both arms completed, under the approval conditions Dan gave for this run: (1) two
arms — in-race-style (12 iterations, K=1) vs the K=1 random baseline, and a simulator-tool arm vs matched-budget
free baselines; (2) one replicate per arm first, cost reported, 10/arm confirmed to fit the $4 stop; (3) stop
Arm A early if criterion 1 is already impossible after 5 replicates. All runs use the frozen config in
`PHASE0_FREEZE.md` (`anthropic/claude-haiku-5.5` via OpenRouter, temperature 0.7, no reasoning effort).

## Cost

Single-replicate cost check (condition 2): Arm A $0.0235/replicate, Arm B $0.0478/replicate → projected 10/arm
≈ $0.72, comfortably under the $4 stop, so no reduction in evaluations/iterations was needed. Actual total new
spend this session (OpenRouter key balance, `/auth/key`, diffed against the $6.0064811 baseline recorded before
any Phase 1 call): **$0.80** for 10 Arm A replicates (1,985,623 tokens) + 10 Arm B replicates (4,379,473 tokens),
well inside budget. Condition 3's early-stop check was evaluated after Arm A's first 5 replicates (5/5 showed
learning; max possible 8/10 on criterion 2 was still reachable) — not triggered.

## Arm A: in-race-style, 12 iterations, K=1 (`tools/probe_step.py --loop 12`)

Each replicate pairs one agent run against one random-hill-climb run sharing the same start design and
evidence draw, matching `PHASE0_FREEZE.md` §4 exactly.

| rep | agent best-so-far | random best-so-far | margin |
|---:|---:|---:|---:|
| 1 | 122.4 | 70.1 | +52.3 |
| 2 | 53.5 | 186.0 | −132.5 |
| 3 | 41.4 | 7.0 | +34.4 |
| 4 | 233.3 | 259.0 | −25.7 |
| 5 | 213.3 | 72.0 | +141.3 |
| 6 | 256.7 | 241.0 | +15.7 |
| 7 | 83.0 | 39.0 | +44.0 |
| 8 | 37.3 | 10.0 | +27.3 |
| 9 | 178.6 | 116.0 | +62.6 |
| 10 | 61.2 | 209.0 | −147.8 |
| **mean** | **128.1** | **120.9** | **+7.1** |

- **Criterion 1 (learning, best-so-far@12 > 0): 10/10 → PASS.**
- **Criterion 2 (beats paired random hill-climb by >10): 7/10 → INCONCLUSIVE** (§4a-iv band: ≥8 pass, ≤6 fail,
  7 inconclusive). Two replicates (4, 10) show the random baseline getting lucky by well over 100 points —
  consistent with §3b's documented spread (sd 90.4 on a mean of 70.1), not a sign the agent did badly.

## Arm B: simulator-as-tool, matched N_evals (`tools/probe_tool.py`, eval budget 25)

The agent calls `evaluate_design` directly (one evaluation = one design scored on the three dev tracks over
seeds 1–20, same unit and grid Arm A uses) up to 25 times, then `submit_design`. The matched-budget free
baseline is computed at the agent's own `N_evals` for that replicate.

**Deviation to report:** `baseline_search.py`'s "(1+1) ES" and `probe_step.py`'s "random hill-climb" are the
*same* update rule (mutate → evaluate → keep-if-better) — PHASE0_FREEZE.md §3's two names differ only in scale
(evals, train-seed count), not mechanism. At a small matched N there is only one free baseline algorithm to
compare against, not two. `tools/probe_tool.py` reports two *independent draws* of that one algorithm
(`draw1`, `draw2`) so replicate-to-replicate noise is visible, and the table below uses their mean as the
baseline estimate (lower-variance than either draw alone) rather than quietly reporting it as if it were two
different search methods.

| rep | N_evals | agent | baseline (mean of 2 draws) | margin |
|---:|---:|---:|---:|---:|
| 1 | 23 | 254.2 | 140.9 | +113.3 |
| 2 | 22 | 257.0 | 101.5 | +155.5 |
| 3 | 20 | 259.0 | 61.7 | +197.3 |
| 4 | 23 | 69.2 | 237.8 | −168.6 |
| 5 | 24 | 76.6 | 119.4 | −42.8 |
| 6 | 25 | 106.1 | 257.6 | −151.5 |
| 7 | 22 | 136.7 | 133.9 | +2.8 |
| 8 | 24 | 69.3 | 109.6 | −40.3 |
| 9 | 24 | 84.7 | 158.4 | −73.7 |
| 10 | 23 | 174.6 | 78.8 | +95.8 |
| **mean** | **23.0** | **148.7** | **139.9** | **+8.8** |

- **Criterion 1 (learning, final gain > 0): 10/10 → PASS.**
- **Criterion 2 (beats matched-N baseline by >10, mean-of-draws): 4/10 → FAIL** (≤6 band). Reported for
  transparency against each single draw too: 3/10 vs draw1 alone, 6/10 vs draw2 alone — neither reaches 8/10
  either, so the mean-based reading is not hiding a pass.
- Headroom closed (§4a-ii, non-gating): mean agent gain 148.7 / ES ceiling headroom 253.6 ≈ **59%**.

## Reading

Both arms show the agent reliably improving on its own starting design (criterion 1 passes cleanly, 10/10, in
both arms — the model is using the feedback). Neither arm shows the agent clearing the free search baseline at
the pre-registered rate: Arm A is inconclusive at 7/10 (one replicate either way of a clean call), Arm B fails
at 4/10 even giving the agent direct, repeated simulator access at roughly double Arm A's effective search
budget (N_evals ≈ 23 vs 12 iterations). Giving the agent the simulator as a tool did not change the answer to
the mandate's question 1 — Haiku 5.5 with direct sim access still does not clearly beat a free (1+1) hill-climb
at matched effort.

## Recommendation (not actioned without sign-off)

- Per `CLAUDE.md`'s Phase 1 plan ("if not, try Sonnet 5.5 on the identical setup"), the next step contemplated
  for a non-pass is a Sonnet 5.5 replication of Arm B at the same eval budget — not run here, as it is a new
  model/spend decision belonging at this gate.
- Arm A's 7/10 is close enough to the pass boundary that a few more paired replicates (e.g. 10 more) could
  resolve it either way relatively cheaply (~$0.25 at the measured per-replicate cost) if that's worth doing
  before concluding.
- As things stand, this is not a pass of G2 under the pre-registered criteria, which argues against proceeding
  to Phase 2 (G3) on the current evidence.

## Gate 2b: Sonnet 5.5 single-replicate cost check — STOPPED, did not reach 10/arm

Approved: replicate both arms on `anthropic/claude-sonnet-5.5`, `--reasoning medium`, identical frozen setup and
unchanged pass criterion. Required steps before scaling: check remaining OpenRouter credit, cap new spend at
`min(remaining_credit, $3)`, run one replicate per arm, report cost, confirm 10/arm fits before continuing.

Remaining credit at the time of this check: $13.19 (limit $20, spend $6.805136) → cap = **$3.00**.

| | N_evals / iters | agent gain (best-so-far / final) | matched baseline | margin | tokens | **cost** |
|---|---|---:|---:|---:|---:|---:|
| Arm A rep 1 (12 iters, K=1) | 12 | +3.7 | +70.1 (paired random) | **−66.4** | 232,641 | **$0.4059** |
| Arm B rep 1 (sim-as-tool) | 14 of 25 | +263.2 | +44.7 (mean of 2 draws) | **+218.5** | 294,826 | **$0.7921** |

Total spent on this cost check: **$1.198** (new spend since the $6.805136 baseline recorded at the start of
Gate 2b). Per-replicate cost is **~17x Haiku's** for Arm A ($0.406 vs $0.0235) and **~16x** for Arm B ($0.792 vs
$0.0478) — Sonnet 5.5 is a substantially larger model and `--reasoning medium` adds billable reasoning tokens on
top of that.

**10/arm does not fit under the $3 cap.** Projected at the measured per-replicate rate: Arm A alone ≈ **$4.06**,
Arm B alone ≈ **$7.92**, combined ≈ **$11.98** — roughly 4x the cap for Arm A alone, ~8x for Arm B alone. Only
about 1-2 more replicate-pairs (one Arm A + one Arm B rep ≈ $1.20 combined) fit in the $1.80 left under the cap,
nowhere near enough for an 8-of-10-style read in either arm.

**Stopped here per the approval's own condition** ("confirm 10 per arm fit before continuing") rather than
unilaterally reducing the replicate count or the model/reasoning settings, since this approval (unlike the
original Phase 1 one) did not pre-authorize a reduction — that choice is left to Dan. The two single replicates
are directionally interesting but are single data points, not evidence at the pre-registered N:
- Arm A: Sonnet did markedly *worse* than Haiku's typical pattern — mostly negative gains for 7 of 12
  iterations, ending at a best-so-far of only +3.7 against a paired random baseline of +70.1.
- Arm B: Sonnet did markedly *better* than Haiku's typical pattern — a clear win (+218.5 margin), and used
  only 14 of its 25-evaluation budget (vs Haiku's ~23/25 average), suggesting more decisive use of the tool.

Options for Dan to choose between (none actioned): (a) raise the Sonnet cap to let 10/arm run at the measured
rate (~$12 all-in for both arms, or ~$4 for Arm A only / ~$8 for Arm B only); (b) drop `--reasoning` to cut cost
and re-check; (c) run a smaller N (e.g. 3-5/arm) as an exploratory read rather than the full pre-registered
design; (d) stop here and treat the single replicates as directional only.

## Gate 2b-2: Arm B only, Sonnet 5.5, budget re-capped at $2.80 — STOPPED, no setting reaches minimum 6

Approved: Arm B only (no more Arm A runs), reasoning ladder low → off → "as many as fit, minimum 6,
labelled exploratory" if 10 doesn't fit. Dan's OpenRouter dashboard showed $3.13 remaining against this key, not
the $11.997 the `/auth/key` API reported at the same moment (API: limit $20, spend $8.003102) — **this
discrepancy is unresolved and worth checking** (possibly a different budget scope, e.g. a workspace or
per-model sub-limit, than the key-level `limit`/`usage` fields this session has been reading). Per instruction,
used the dashboard figure: cap = min($3.13, $2.80) = **$2.80**, tracked as incremental API-usage spend from the
$8.003102 baseline at the start of this sub-task (the API's absolute "remaining" is not trusted per Dan's
correction, but a *diff* of its usage field across two calls seconds apart is still an accurate $ meter
regardless of which total is right).

| reasoning | N_evals | agent gain | matched baseline (mean of 2 draws) | margin | tokens | cost/rep | 10-rep cost | min-6 cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| low | 0 (both tries) | −11.8 | +0.0 (trivial — 0 search steps) | n/a, degenerate | 12,719 | ~$0.00 | ~$0.00 | ~$0.00 |
| off (no `--reasoning` flag) | 22 | +249.6 | +140.95 | +108.65 | 529,367 | $1.2018 | $12.02 | $7.21 |
| medium (for reference, priced in Gate 2b above) | 14 | +263.2 | +44.7 | +218.5 | 294,826 | $0.7921 | $7.92 | $4.75 |

**`low` is free but behaviorally degenerate**, not just cheap: tested twice (different rng), both times the
model called `submit_design` immediately with zero `evaluate_design` calls, so the matched baseline is also
forced to 0 steps (always the unmodified start design, gain +0.0) — the comparison measures nothing about
search ability. This is a genuine finding about `reasoning=low`'s effect on tool-use propensity in this
harness, not a cost result, and 10 (or 6) replicates at this setting would not be valid data regardless of how
cheap they are.

**`off` priced more expensive than `medium`**, not less — the reasoning ladder's implicit assumption (lower
effort → lower cost) did not hold here; omitting the `reasoning` parameter entirely apparently lets the model
use more extended thinking than `effort: medium` explicitly caps it to (22 evals / 529k tokens vs 14 evals /
295k tokens). `medium` remains the cheapest *valid* (non-degenerate) setting found across both Gate 2b and
2b-2.

**Spent this sub-task: $1.2018** (the `off` pricing replicate; the two `low` replicates cost $0.00 at this
precision). Remaining under the $2.80 cap: **$1.60**.

**Stopped per the approval's own minimum-6 floor**, not the cumulative-spend stop (not yet reached): neither
tested valid setting reaches 6 replicates within budget — `off` needs $7.21 for 6, `medium` needs $4.75 for 6,
and only $1.60 is left (or $2.80 if starting fresh with `medium` instead of pricing `off` first, still short of
$4.75). No reasoning setting tested lets "minimum 6" happen under this cap, so no batch was run — running 1-2
replicates would undershoot the floor Dan set rather than fit it.

Options for Dan (none actioned): (a) raise the cap to ≥$4.75 (the `medium`, minimum-6 cost) or ≥$7.92 (`medium`,
full 10); (b) accept the single already-run `medium`-reasoning Arm B replicate (margin +218.5, from Gate 2b) as
the only Sonnet-on-Arm-B data point and stop; (c) resolve the dashboard/API discrepancy first in case more
credit is actually available than either figure suggests; (d) try `reasoning=high` (untested, likely pricier
still, not run without sign-off).

## Gate 3, part 1: what the agent sees after each evaluation (zero cost)

Both arms draw on the exact same function, `tools/probe_step.py`'s `evidence_for` → `orchestrator/evidence.py`'s
`summarise_trials`, for every piece of evidence shown to the model: Arm A's per-iteration evidence block, Arm
B's `starting_design_evidence` and every `evaluate_design` tool result. **There is no granularity difference
between the two arms** — only how often and when the agent sees a fresh evaluation differs, not what one
evaluation's result looks like. This also matches the real race templates exactly: both
`package-templates/randow-maps/config/race.yaml` and `.../opt-eval/config/race.yaml` set
`evaluation.evidence_to_agents: summary`, the same mode these probe tools use unconditionally — so this is not a
simplified stand-in, it is what a real race shows.

A real example (start design, oval/s-bend/slalom, seeds 1-20):

```json
{"n_trials": 60, "per_track": {
  "oval":    {"trials": 20, "finished": 20, "finish_rate": 1.0, "ended_by": {"finished": 20},
              "mean_score": 947.3, "min_score": 940.21, "max_score": 955.49, "mean_finish_time_s": 2.109,
              "mean_metrics": {"progress": 0.9982, "rms_error": 0.0039, "max_error": 0.0088,
                               "line_loss_events": 0.55, "steering_oscillation": 0.2479, "control_effort": 5.8223}},
  "s-bend":  {"trials": 20, "finished": 19, "finish_rate": 0.95, "ended_by": {"finished": 19, "off_track": 1}, ...},
  "slalom":  {"trials": 20, "finished": 0,  "finish_rate": 0.0,  "ended_by": {"off_track": 20},
              "mean_score": 179.1, "mean_finish_time_s": null, "mean_metrics": {"progress": 0.4322, ...}}}}
```

**Fields present, per track, per evaluation:** `trials` (count), `finished` (count), `finish_rate`, `ended_by`
(a histogram of termination reasons across the group, e.g. `{"finished": 19, "off_track": 1}` — reasons are
`finished` / `off_track` / `stalled` / `timeout` / `controller_error` / `invalid_design`), `mean_score`,
`min_score`, `max_score`, `mean_finish_time_s` (finished trials only, `null` if none finished), and
`mean_metrics` with exactly six keys: `progress`, `rms_error`, `max_error`, `line_loss_events`,
`steering_oscillation`, `control_effort` — each a mean across every trial in the group (not just finished ones),
so a bad run still pulls the mean down rather than being excluded.

**Dropped vs the raw per-trial record** (what `simulator/adapter/headless.py`'s `run_trial` actually returns, and
what the real race stores for replay — `orchestrator/evidence.py`'s own docstring: "the stored entity payload,
the published trial artefacts, the replay and the scores still hold every trial in full"):
- **All per-step telemetry**, for every trial: `x`, `y`, `heading`, `speed`, per-step `sensors[]` readings,
  per-step `error`/`progress`, and `line_lost` — none of it reaches the agent in either arm. The agent cannot
  see *where on the track* a run failed, only that it did and by what aggregate margin.
- **Per-trial/per-seed identity.** The agent sees "1 of 20 went off_track" but not *which* seed, nor that
  seed's individual score — only the pooled `ended_by` counts and `min`/`max_score` across the group hint that
  variance exists.
- **Two metrics fields computed by the adapter but never summarised at all:** `controller_errors` (a per-trial
  exception counter) and `noise_robustness` (`1 − noise − max_error`, already computed per trial) are both
  present on every raw trial record but are not in `summarise_trials`'s `METRICS` tuple, so they never appear in
  any evidence block in either arm, by any route.
- **The raw `completion` boolean, `run_id`, `adapter_version`.** Redundant with `finish_rate`/`ended_by` or
  irrelevant to a design decision, so not a meaningful loss, but confirmed dropped for completeness.

## Gate 3, part 2: Arm B at 100 evaluations, 5 paired replicates, Haiku 5.5 only

Same harness as Gate 2's Arm B (`tools/probe_tool.py`), eval budget raised from 25 to 100, Sonnet excluded per
instruction (credit on hold). Baseline OpenRouter usage at the start of this sub-task: $9.204928. Single-
replicate price check (required before scaling): **$0.1081** (N_evals=47, well under the 100 cap) → projected
5-replicate cost ≈ $0.54, comfortably inside the $1.20 cap, so all 5 ran. **Actual total spend: $0.3992** — the
agent used fewer evaluations on average than projected from replicate 1 (see below), so this undershot even the
linear projection.

| rep | N_evals (of 100) | agent gain | matched baseline (mean of 2 draws) | margin |
|---:|---:|---:|---:|---:|
| 1 | 47 | 229.7 | 132.75 | +97.0 |
| 2 | 46 | 254.1 | 148.2 | +105.9 |
| 3 | 26 | 223.2 | 72.85 | +150.4 |
| 4 | 30 | 265.1 | 235.85 | +29.3 |
| 5 | 42 | 253.1 | 161.2 | +91.9 |
| **mean** | **38.2** | **245.0** | **150.2** | **+94.9** |

- **Criterion 1 (learning, final gain > 0): 5/5 → PASS.**
- **Criterion 2 (beats matched-N baseline by >10, mean-of-draws): 5/5 → PASS** (every margin is at least ~3x
  the 10-point floor; even the weakest replicate, #4, clears it by +29.3).
- Headroom closed (§4a-ii): mean agent gain 245.0 / ES ceiling headroom 253.6 ≈ **97%** — essentially the full
  headroom available to the large-scale search in `PHASE0_FREEZE.md` §3a, reached with a budget two orders of
  magnitude smaller (mean 38 evaluations here vs 300 evaluations × 10 train seeds there).

**This reverses Gate 2's Arm B result (25-eval budget: learning 10/10, win-margin 4/10 fail).** At a larger
evaluation budget, Haiku 5.5 with direct simulator-tool access clears both pre-registered criteria cleanly, 5/5,
at n=5. Two things to flag about reading this as a clean answer to the mandate's question 1:
- **n=5, not the pre-registered n=10** — this is the first required pricing/confirmation step of a design meant
  to scale to 10; it was not extended to 10 in this instruction. The result is unanimous at n=5, which is itself
  informative (5/5 both ways, including the ES ceiling comparison, is a stronger signal than 7-8/10 would be),
  but it is a smaller sample than the pre-registered design calls for.
- **The agent did not use its full budget.** Mean N_evals was 38.2 of 100 — nowhere near the cap, unlike the
  25-eval-budget runs in Gate 2 which averaged ~23/25 (agent routinely wanted more room than it had). Given more
  room, Haiku stopped well short of using it, submitting once it judged the design good enough rather than
  continuing to search. Whether 100 specifically vs some other number in between (e.g. 50) would hold the same
  result is untested — this run shows that the 25-cap in Gate 2 was a binding constraint that mattered, not
  that 100 is some special value.

## Gate 3, part 3: proposed richer-diagnostics evidence variant (NOT run)

A proposal only — nothing below is implemented or tested. Scoped to stay inside `CLAUDE.md`'s charter: every
addition is a *fact about how a run failed* (where, how consistently, how close to a threshold), never a
suggestion about what to change. None of it is design advice, and none of it exposes per-step telemetry (which
would blow the prompt up by orders of magnitude for little gain, per `orchestrator/evidence.py`'s own rationale
for having a `summary` mode at all).

1. **Stop silently dropping metrics the adapter already computes.** `controller_errors` and `noise_robustness`
   are on every raw trial record today and cost nothing extra to summarise — add them to `summarise_trials`'s
   `METRICS` tuple. This is closer to a bug fix than a new feature (the loss looks incidental, not deliberate),
   but it's listed here because it changes what agents see, so it belongs at a gate, not quietly patched.
2. **Failure-location, not just failure-count.** For non-finished trials, report the *progress fraction reached
   at termination* (already computed, just not surfaced: `telemetry[-1]["progress"]` at the moment of
   `off_track`/`stalled`/`timeout`) as a per-track distribution — e.g. `"failure_progress": {"mean": 0.41,
   "min": 0.12, "max": 0.78}`. This says *how far around the track* a design typically gets before failing,
   without saying why or what to change about the sensors/gains causing it.
3. **Spread, not just min/mean/max.** Add `score_sd` and `progress_sd` per track. Today an agent sees
   `min_score`/`max_score` but has to infer consistency; a design that is "always mediocre" and one that is
   "usually great, occasionally catastrophic" can share a mean and be indistinguishable without this.
4. **A worst-trial snapshot, not full telemetry.** One compact record per track for the single worst trial by
   score — `{"seed": 7, "termination_reason": "off_track", "progress": 0.34, "error_at_termination": 0.063}` —
   four numbers, not the ~300-row per-step trace. Lets the agent see a concrete worst case to reason about
   (e.g. "even my worst case is 85% progress" vs "my worst case died at 12%") without per-step positions.
5. **Finish-time spread for finished trials**, not just the mean: `min`/`max` alongside `mean_finish_time_s`,
   since the score's time term rewards consistency as well as mean speed.

Rough size: each addition is O(1) numbers per track (3 tracks), so this adds roughly 15-20 extra fields to a
~40-field evidence block — nowhere near the per-step telemetry this session confirmed is categorically excluded
in both arms today, and far short of anything that tells the agent *what* to change rather than *what
happened*. Whether this is worth building (and whether it should go in Arm A, Arm B, or the real race template)
is Dan's call, not run here.

## Gate 3b: Arm B at 100 evals extended to n=10; which seed set "final gain" uses; held-out scoring

No Sonnet, no harness changes. Haiku 5.5 only, same `tools/probe_tool.py` / eval-budget-100 settings as Gate 3
part 2, extended from 5 to 10 paired replicates, hard cap $0.80 (cost-guard kill-switch on cumulative OpenRouter
usage, same mechanism as prior gates).

### (2) Which seed set "final gain" is scored on — confirmed in writing

From `tools/probe_tool.py` (`main()`): `seeds = list(range(1, args.evidence_seeds + 1))` → **seeds 1-20** is the
grid the agent's `evaluate_design` tool actually runs on every call, and is also what `starting_design_evidence`
is computed on. Separately, `fresh = list(range(5000, 5000 + args.fresh_seeds))` → **seeds 5000-5029**, used
*only* inside `score()`:

```python
def score(design: dict) -> float:
    return evaluate(design, tracks, dev, fresh, config)["mean"] - base["mean"]
```

`agent_gain = score(result["final_design"])` — so **"final gain" is the submitted design's mean score on the 30
fresh validation seeds (5000-5029), on the three development tracks (oval, s-bend, slalom), minus the start
design's mean score on that same fresh block.** The agent's tool never sees seeds 5000+ under any code path —
every `evaluate_design` call and the upfront `starting_design_evidence` are fixed to seeds 1-20, so there is no
leakage between what the agent optimised against and what "final gain" reports. This is the same fresh-seed
convention Arm A (`probe_step.py`) and Phase 0's `baseline_search.py --validation-seeds` (also offset at 5000)
all use, so the three arms' "gain" numbers are on a consistent basis. Held-out tracks (hairpin, hairpin-b,
slalom-b) are not involved in "final gain" at all — that is the separate held-out scoring in (3) below.

### (1) 5 more replicates (10 total)

Cost-guard cap $0.80, tracked from the $9.6040923 OpenRouter-usage baseline at the start of this sub-task. These
5 ran noticeably more expensively than Gate 3's first 5 (similar `N_evals`, but $0.256/replicate here on average
vs ~$0.08/replicate there, for reasons not investigated — possibly prompt-caching discounts not applying the
same way across separate process invocations) — flagging this cost variance since it's real and unexplained,
not because it caused a problem: all 5 completed naturally, total $0.5842, under the $0.80 cap with headroom to
spare.

| rep | N_evals | agent gain | matched baseline (mean of 2 draws) | margin |
|---:|---:|---:|---:|---:|
| 1 | 47 | 229.7 | 132.75 | +97.0 |
| 2 | 46 | 254.1 | 148.2 | +105.9 |
| 3 | 26 | 223.2 | 72.85 | +150.4 |
| 4 | 30 | 265.1 | 235.85 | +29.3 |
| 5 | 42 | 253.1 | 161.2 | +91.9 |
| 6 | 47 | 234.4 | 225.05 | **+9.4** |
| 7 | 53 | 254.7 | 228.75 | +26.0 |
| 8 | 37 | 250.1 | 191.8 | +58.3 |
| 9 | 54 | 203.9 | 239.7 | **−35.8** |
| 10 | 32 | 264.0 | 81.05 | +183.0 |
| **mean** | **41.4** | **243.2** | **167.7** | **+71.5** |

- **Criterion 1 (learning, final gain > 0): 10/10 → PASS**, unchanged from the n=5 subset.
- **Criterion 2 (beats matched baseline by >10, mean-of-draws): 8/10 → PASS** (the ≥8/10 pre-registered band),
  but **not the unanimous 5/5 the first half suggested**. Replicate 6 is a near-miss tie (margin +9.4, just
  under the 10-point floor) and replicate 9 is an outright loss (−35.8) — both are among the 5 new replicates.
  The headline verdict is still a pass, exactly at the boundary the pre-registered criterion treats as a clean
  pass (not the 7/10 "inconclusive" band), but the margin of the pass is thinner than n=5 alone implied: this is
  a useful reminder that a small, unanimous early sample can overstate how clear-cut a result is.
- Headroom closed (§4a-ii): mean agent gain 243.2 / 253.6 ≈ **96%**, materially unchanged from the n=5 figure.

### (3) Zero-cost held-out scoring: every Arm B design vs the Phase 0 ES ceiling designs

`tools/score_heldout.py` (new, read-only analysis script — no harness change) scores all 10 agent-submitted
designs, both matched-baseline draws reconstructed deterministically at each replicate's own `(rng, n_evals)`
(pure function of already-known seeds, zero tokens), and the 5 Phase 0 ES ceiling designs
(`phase0/ceiling_rng{1..5}.json`), all on **held-out tracks (hairpin, hairpin-b, slalom-b) and held-out seeds
101-110** — the same convention `PHASE0_FREEZE.md` §3a uses. As a cross-check, the 5 recomputed ES held-out
means (794.2, 578.5, 720.7, 265.6, 639.2) reproduce §3a's reported values (794, 579, 721, 266, 639) almost
exactly; §3a's reported sd of 203.6 only reproduces with *sample* sd (ddof=1), not population sd — a reporting
convention, not a data discrepancy, now matched in the script.

| kind | n | held-out mean | held-out sample sd |
|---|---:|---:|---:|
| Arm B agent (10 submitted designs) | 10 | **545.3** | 155.4 |
| Matched baseline, pooled both draws | 20 | 517.0 | 143.1 |
| ‣ draw1 alone | 10 | 576.6 | 169.1 |
| ‣ draw2 alone | 10 | 457.3 | 81.9 |
| Phase 0 ES ceiling (5 designs, §3a) | 5 | 599.6 | 203.8 |

**Reading:** on held-out *track shapes* (not just held-out seeds), the agent's advantage over the matched free
search **does not clearly hold up**. Agent mean (545.3) sits only +28.3 above the pooled matched baseline
(517.0), well inside one sample sd of either (143-170), and below draw1 alone (576.6). The ES ceiling (599.6)
is highest of the three but is itself the noisiest (sd 203.8, n=5) — consistent with `PHASE0_FREEZE.md` §3a's
own warning that held-out-track generalization has roughly 34% CV and depends heavily on search-seed luck, not
a stable property of any one method. Per-track detail shows why: nearly every design (agent, matched baseline,
and ES alike) handles `hairpin` well (usually 90-100% finish) but is inconsistent on `hairpin-b` and `slalom-b`
(many 0% finish rates across all three kinds) — the dev-score win in (1) does not translate into a visibly
better held-out track-shape generalization, it is still dominated by which specific designs happen to transfer,
for all three methods alike.

This is the first result in this session that cuts against a clean "the agent wins" reading: dev-score gain
(in-distribution, same track shapes, unseen seeds) shows a real pass; held-out generalization (unseen track
shapes) shows no clear separation from the free matched baseline. Both are true at once and answer different
questions — Dan's mandate's question 1 ("improve a design from feedback... beyond a free... baseline") was
pre-registered on dev-score gain specifically (`PHASE0_FREEZE.md` §4), so the Gate 3/3b pass stands on its own
terms, but this held-out comparison is relevant context for any Phase 2 decision about what "winning" should be
measured on.
