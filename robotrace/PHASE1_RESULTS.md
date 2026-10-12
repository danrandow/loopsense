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
