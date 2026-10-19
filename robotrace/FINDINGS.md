# Robot Race: findings so far

One page, plain language, for sharing. Every number here comes from a completed, pre-registered gate
(GATE6-18_REPORT.md); nothing new is claimed here that those reports don't already show.

## Scope

Everything below is **one model** (Haiku 5.5, via OpenRouter, no reasoning/thinking parameter ever set —
confirmed by direct code inspection, Gate 16), **one task** (a simulated line-following robot, geometry +
PID-style controller), **12 iterations per race, no simulator tool access** (agents get summarised
feedback each iteration, not a live tool they can call). None of the findings below have been tested
outside that envelope — see "Not tested" at the end.

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
- **opt-eval-pre2** — opt-eval's Optimizer, but revising twice against two rounds of advisory critique
  before anything races (Draft → critique → Revise → critique → Finalize → Race). The Evaluator never has
  approve/decline power; only the Optimizer's own final submission ever races.
- **randow-maps** — Builder (geometry only) + Integrator (adds the controller, critiques the geometry).
- **randow-maps-muted** — randow-maps' structure, except the Builder never receives the Integrator's
  critique text (it still gets real race telemetry).
- **randow-maps-dialogue** — randow-maps' structure and budget, with instructions that explicitly permit
  the Builder to hold geometry and state whether it took the Integrator's last advice (and why not, if
  not), and let the Integrator recommend holding/changing/exploring instead of always naming a field to
  change. No design advice added either way.
- **matched hill-climb** — a free, non-LLM random search, run from each race's own starting design, same
  number of tries as that race. The reference line every arm is measured against.

## Results

| arm | n | mean paired improvement (95% CI) | margin vs. matched hill-climb (95% CI) | held-out score | cost/race |
|---|---:|---|---|---:|---:|
| opt-eval | 16 | +242 [+152, +333] | +209 [+126, +291] | 43 | $0.10 |
| **opt-solo** | 16 | **+665 [+586, +744]** | **+566 [+493, +638]** | **404** | **$0.04** |
| opt-eval-muted | 8 | +582 [+408, +757] | **+548 [+376, +720]** | **262** | $0.09 |
| opt-eval-pre2 | 6 | +211 [+66, +356] | not measured | 27 | $0.27 |
| randow-maps | 16 | +161 [+73, +249] | +80 [−5, +165] | 41 | $0.13 |
| randow-maps-muted | 8 (+2 partial, reported separately) | +171 [−27, +370] | **+138 [−61, +336]** | **25** | $0.12 |
| randow-maps-dialogue | 8 | +316 [+87, +545] | not measured | 74 | $0.12 |

New this gate (bold): both muted arms' margin and held-out cells, filled by the same method Gate 8-9 used
for the other three arms — 3 matched hill-climb replicates per race (rng seeds 1, 2, 3, 12 steps, full
design space, started from that race's own iteration-0 design — identical method to Gates 6-9's), scored
on `primary_metric` for the margin and on `hairpin`/`hairpin-b`/`slalom-b` seeds 101-110 (`score_heldout.py`'s
convention) for held-out. **Sanity check before trusting these:** this method reproduces both muted arms'
already-published improvement means exactly (582.46/249.44 and 171.17/286.56) from the same underlying race
data, which is strong evidence the margin/held-out numbers computed the same way are methodologically sound.
Opt-eval-pre2's and randow-maps-dialogue's margin cells are not yet measured (no matched hill-climb has been
run against their specific race sets); their held-out cells are filled, newly computed this gate at zero cost.

**Opt-eval vs. randow-maps, head-to-head (both n=16, on paired improvement):** Δ = +81.56, Welch 95% CI
[−49.86, +212.98] — includes 0. The two different two-agent topologies this project has tested are
statistically indistinguishable from each other, as well as each separately failing to clearly beat free
search. Neither is a stronger "second agent" design than the other on this evidence.

"Paired improvement" = final iteration's score minus iteration 0's, on the pre-registered out-of-sample
metric. "Held-out" = score on track shapes neither arm ever sees or optimizes against — the best check
against simple overfitting. All CIs use the same convention as every earlier gate: a one-sample 95% interval
(mean ± 1.96 × sd/√n) for improvement/margin columns, Welch's two-sample CI only where a head-to-head
comparison between two arms is being made explicitly (noted inline where used).

## What's established

- **A single agent (opt-solo) clearly beats free random search** — by a wide, repeated margin (Gate 8,
  replicated independently at Gate 9). It also generalizes better: its held-out score is proportionally
  *higher* than its primary-metric score, the opposite of what simple overfitting would predict.
- **The two-agent team (opt-eval) does not show a reliable edge over free search** — the CI on its margin
  includes zero at n=16. **Neither does randow-maps, and the two are statistically indistinguishable from
  each other** (head-to-head CI includes 0, this gate) — two different two-agent topologies, the same
  non-result.
- **Removing only the Evaluator's critique text from opt-eval — keeping the Evaluator running and gating
  the race — moves the result close to opt-solo's and clearly above opt-eval's own** (Gate 11, 95% CI vs.
  opt-eval excludes 0; margin vs. matched hill-climb now also confirmed to exclude 0, this gate). **This now
  extends to generalization, not just the scored metric**: opt-eval-muted's held-out score (262) is roughly
  6× opt-eval's own (43) and over half of opt-solo's (404) — the causal effect of removing the critique text
  shows up on tracks the team never optimized against too, not only as an artefact of the scored metric.
- **A second, more elaborate critique structure (opt-eval-pre2: two advisory rounds, no approve/decline
  power) does not recover opt-eval's gap to opt-solo either** — if anything its race-level point estimate is
  lower than opt-eval's own, though not significantly so (Gate 15). **The first critique-and-revise cycle is
  destructive 96.5% of the time** (85/88 iterations worsen or are unchanged at draft→round-1, mean −343.62) —
  traced to a specific, checkable mechanism in at least one case: the critique makes a confident claim about
  whether the current design already completes, and is sometimes confidently wrong; the Optimizer, trusting
  the claim, discards a design that was already working.
- **The critique has an identifiable weak spot: speed.** Applying the Evaluator's own base_speed
  suggestions individually, even when its own stated telemetry condition is true, hurts the score more
  often than it helps (Gate 12) — "too eager to raise speed before the design can handle it."
- **Randow-maps' Integrator critique is not the same story.** When its own stated condition holds, its
  geometry suggestions are net *helpful*; its weak spot is a different field (mass). And unlike opt-eval,
  **muting its critique text does not help** (Gate 13, full n=8): the result stays statistically
  indistinguishable from randow-maps' own un-muted performance (CI vs. randow-maps includes 0) and still far
  below opt-solo (CI vs. opt-solo excludes 0) — now confirmed again on the held-out score (25, close to
  randow-maps' own 41, nowhere near opt-eval-muted's 262). The two topologies' second agents are not failing
  for the same reason.
- **A structural timing quirk, true of every two-agent topology tested:** the critiquing agent (Evaluator or
  Integrator) writes its feedback in the same iteration as the design it's reviewing, *before that design has
  raced* — its own instructions say so explicitly ("nothing has been measured for it yet... do not state how
  this robot will perform or has performed"). The Builder/Optimizer only reads that feedback on the *next*
  iteration, by which point the design's own race result is already available separately as telemetry. The
  critique text a team acts on is never about the result the team can already see; it is one full iteration
  older than the evidence sitting next to it.
- **Giving the Builder explicit permission to hold geometry and decline advice (randow-maps-dialogue) produces
  a large, measured behavioural shift without yet showing a significant score change** (Gate 17-18): hold
  rate roughly 3× randow-maps' own (34.1% vs. 11.9%), advice explicitly declined with a stated reason in about
  1 in 10 transitions, and holding rises sharply across a race (12.5% early → 62.5% late, p<0.0001). Its mean
  improvement (+316) sits above randow-maps' own (+161) but the CI between them includes 0 at n=8 — a real
  behavioural change, not yet a confirmed score change.
- **A controller-tuning gradient across all three topologies tested** *(exploratory, Gate 18, not
  pre-registered — n=8 for dialogue, descriptive comparison, no CI-based decision rule)*: opt-solo (single
  agent revising the whole design each iteration) touches a controller gain on 70.5% of its moves; randow-maps
  touches one on 29.5%; randow-maps-dialogue sits in between at 54.5%, despite holding geometry roughly 3×
  more often than randow-maps — consistent with a team leaning on controller tuning specifically when geometry
  is held, not just moving less overall. *Also exploratory, same gate:* within randow-maps-dialogue, the dev
  score after a hold beats the score after a geometry change in 7 of 8 races (paired diff +111, CI
  [−4, +226], p=0.057 — borderline, not significant at this n).
- **No race, in any arm, ever reached a genuinely curved sensor layout** — every final design in 56+ races
  examined (across opt-eval, opt-solo, both muted arms, opt-eval-pre2, randow-maps, and randow-maps-dialogue)
  is a straight row of 5 or 7 sensors. Dialogue's added freedom to hold or explore geometry (Gate 18) changed
  *how often* geometry changes, not *what kind* of layout gets tried — it never reached a curved row either.

## What's still uncertain

- **Why randow-maps' shortfall persists when muted, when opt-eval's doesn't.** Confirmed (Gate 13, n=8, and
  again this gate on held-out) that it isn't the critique text; the actual cause is open — something else
  about the Builder/Integrator split, the geometry-only Builder's narrower design space, or a different
  mechanism entirely.
- **Whether randow-maps-dialogue's behavioural shift (more holding, explicit decline reasons) will produce a
  statistically detectable score change at a larger n.** At n=8 the CI vs. randow-maps includes 0; the point
  estimate is higher but not confirmed.
- **A clean re-run of opt-eval-muted.** Gate 11 found a defect (muting the edge also silently broke a
  revise-retry trigger in ~7% of iterations) after the races had already run. The defect should have biased
  the result toward understating, not overstating, the effect — but it was never re-run clean to confirm.
- **Whether opt-solo's advantage holds at longer budgets**, with a different model, or on a different
  track family — none of that has been tested.

## What we learned

- **The first critique-and-revise cycle is overwhelmingly destructive, not just unhelpful**: opt-eval-pre2's
  draft→round-1 transition worsens or leaves unchanged 96.5% of the time (85/88 iterations, mean −343.62),
  traced in at least one concrete case to the critique confidently (and wrongly) asserting the current design
  doesn't complete, causing the Optimizer to discard a design that was already working.
- **The critique a team acts on is always one iteration stale**: every critiquing role (Evaluator, Integrator)
  writes its feedback before its own iteration's design has raced, by its own instructions' explicit
  admission. The Builder/Optimizer only reads that feedback the following iteration, after that same design's
  real race result is already available as separate telemetry — the advice and the evidence it should be
  checked against arrive on different clocks.
- **Geometry churns constantly in the base randow-maps team (88% of iterations change it), and holding is
  associated with better outcomes where it's allowed to be deliberate.** Randow-maps-dialogue, given explicit
  permission to hold, holds 3× more often and shows a (borderline, p=0.057, exploratory) better dev score
  after holding than after changing, paired within race.
- **Controller tuning absorbs the slack left by less geometry churn**: a clean three-way gradient
  (opt-solo > randow-maps-dialogue > randow-maps) in how often a move touches a controller gain,
  *(exploratory, Gate 18)*, consistent with a team compensating through the controller when it holds
  geometry rather than simply doing less work overall.
- **No arm, across every topology and 56+ races, has ever produced a curved sensor layout** — not the
  original teams, not either muted variant, not the dialogue arm given explicit freedom to explore. Whatever
  is keeping every design on a straight row, it isn't lack of permission to hold or deviate.

## Not tested

- Tool or live simulator access for the second/critiquing agent (it only ever gets summarised feedback,
  never a callable tool).
- A reasoning/thinking parameter enabled on any call (confirmed, Gate 16: none has ever been set).
- A stronger model than Haiku 5.5 (e.g. Sonnet) on any of these topologies.
- A longer budget than 12 iterations.
- Any task other than this one simulated line-following robot.
- A Builder/Optimizer role that can see the controller it's being built around (randow-maps' Builder never
  sees the controller at all, by design — untested whether that visibility gap is itself a constraint).

## What each next step would cost

| step | rationale | rough cost |
|---|---|---:|
| Clean re-run of opt-eval-muted, defect fixed, n=8 | confirm Gate 11 wasn't biased by the stall defect | ~$0.70 |
| Investigate what else randow-maps' Integrator/Builder split is missing, now that the critique text is ruled out | find the actual bottleneck | zero-cost analysis first, likely informs any further paid step |
| Matched-hill-climb margin for opt-eval-pre2 and randow-maps-dialogue | zero-cost, offline — not done yet (held-out is done) | $0 |
| Randow-maps-dialogue at a larger n | resolve the borderline (+155, CI crosses 0) improvement-vs-randow-maps gap | ~$1.00-1.50 for n=16 total |
| Double the iteration budget for opt-solo, n=8 | test whether the single-agent lead holds or plateaus | ~$0.70-1.00 |
| Same opt-solo test on a stronger model (e.g. Sonnet) | test whether the result is model-specific | likely higher per-race cost; not yet measured |
