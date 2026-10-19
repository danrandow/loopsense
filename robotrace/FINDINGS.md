# Robot Race: findings so far

One page, plain language, for sharing. Every number here comes from a completed, pre-registered gate
(GATE6-13_REPORT.md); nothing new is claimed here that those reports don't already show.

## The question

Can a single LLM agent improve a line-following robot design from feedback in this simulator, beyond what a
free, non-LLM random search gets with the same number of tries? And if a second agent (a reviewer/critic)
is added to the team, does it help or hurt?

## The arms

- **opt-eval** — Optimizer + Evaluator. The Optimizer proposes a design; the Evaluator critiques it, tells
  the Optimizer what to change, and decides when to let it race.
- **opt-solo** — the same Optimizer, alone. No Evaluator at all.
- **opt-eval-muted** — opt-eval's exact structure, except the Optimizer never receives the Evaluator's
  critique text. The Evaluator still runs, still decides when the design races.
- **randow-maps** — Builder (geometry only) + Integrator (adds the controller, critiques the geometry).
- **randow-maps-muted** — randow-maps' structure, except the Builder never receives the Integrator's
  critique text (it still gets real race telemetry).
- **matched hill-climb** — a free, non-LLM random search, run from each race's own starting design, same
  number of tries as that race. The reference line every arm is measured against.

## Results

| arm | n | mean paired improvement (95% CI) | margin vs. matched hill-climb (95% CI) | held-out score | cost/race |
|---|---:|---|---|---:|---:|
| opt-eval | 16 | +242 [+152, +333] | +209 [+126, +291] | 43 | $0.10 |
| **opt-solo** | 16 | **+665 [+586, +744]** | **+566 [+493, +638]** | **404** | **$0.04** |
| opt-eval-muted | 8 | +582 (not measured vs. its own hill-climb) | not measured | not measured | $0.09 |
| randow-maps | 16 | +161 [+73, +249] | +80 [−5, +165] | 41 | $0.13 |
| randow-maps-muted | 8 (+2 partial, reported separately) | +171 [−27, +370] | not measured | not measured | $0.12 |

"Paired improvement" = final iteration's score minus iteration 0's, on the pre-registered out-of-sample
metric. "Held-out" = score on track shapes neither arm ever sees or optimizes against — the best check
against simple overfitting.

## What's established

- **A single agent (opt-solo) clearly beats free random search** — by a wide, repeated margin (Gate 8,
  replicated independently at Gate 9). It also generalizes better: its held-out score is proportionally
  *higher* than its primary-metric score, the opposite of what simple overfitting would predict.
- **The two-agent team (opt-eval) does not show a reliable edge over free search** — the CI on its margin
  includes zero at n=16.
- **Removing only the Evaluator's critique text from opt-eval — keeping the Evaluator running and gating
  the race — moves the result close to opt-solo's and clearly above opt-eval's own** (Gate 11, 95% CI vs.
  opt-eval excludes 0). This is a direct causal test, not a correlation: the critique *text* is implicated,
  not merely "having a second agent."
- **The critique has an identifiable weak spot: speed.** Applying the Evaluator's own base_speed
  suggestions individually, even when its own stated telemetry condition is true, hurts the score more
  often than it helps (Gate 12) — "too eager to raise speed before the design can handle it."
- **Randow-maps' Integrator critique is not the same story.** When its own stated condition holds, its
  geometry suggestions are net *helpful*; its weak spot is a different field (mass). And unlike opt-eval,
  **muting its critique text does not help** (Gate 13, full n=8): the result stays statistically
  indistinguishable from randow-maps' own un-muted performance (CI vs. randow-maps includes 0) and still far
  below opt-solo (CI vs. opt-solo excludes 0). The two topologies' second agents are not failing for the
  same reason.
- **Behaviourally, a muted opt-eval Optimizer moves more like opt-solo's** (more design fields touched per
  move, similar move-size distribution) **than like opt-eval's own un-muted version** (Gate 13) — the
  outcome shift has a matching behavioural shift, not just a score coincidence.
- **No race, in any arm, ever reached a genuinely curved sensor layout** — every final design in 48+ races
  examined is a straight row of 5 or 7 sensors.

## What's still uncertain

- **Why randow-maps' shortfall persists when muted, when opt-eval's doesn't.** Confirmed (Gate 13, n=8) that
  it isn't the critique text; the actual cause is open — something else about the Builder/Integrator split,
  the geometry-only Builder's narrower design space, or a different mechanism entirely.
- **Margin-vs-matched-hill-climb and held-out score have not been measured for either muted arm** —
  reported above as "not measured," not assumed.
- **A clean re-run of opt-eval-muted.** Gate 11 found a defect (muting the edge also silently broke a
  revise-retry trigger in ~7% of iterations) after the races had already run. The defect should have biased
  the result toward understating, not overstating, the effect — but it was never re-run clean to confirm.
- **Whether opt-solo's advantage holds at longer budgets**, with a different model, or on a different
  track family — none of that has been tested.

## What each next step would cost

| step | rationale | rough cost |
|---|---|---:|
| Clean re-run of opt-eval-muted, defect fixed, n=8 | confirm Gate 11 wasn't biased by the stall defect | ~$0.70 |
| Investigate what else randow-maps' Integrator/Builder split is missing, now that the critique text is ruled out | find the actual bottleneck | zero-cost analysis first, likely informs any further paid step |
| Matched-hill-climb margin + held-out, both muted arms | zero-cost, offline — just not done yet | $0 |
| Double the iteration budget for opt-solo, n=8 | test whether the single-agent lead holds or plateaus | ~$0.70-1.00 |
| Same opt-solo test on a stronger model (e.g. Sonnet) | test whether the result is model-specific | likely higher per-race cost; not yet measured |
