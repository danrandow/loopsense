# Gate 19: finish Gate 14, close FINDINGS.md's gaps, merge to main

Written 2026-10-19. Free, offline, zero-cost analysis only — no races run. "Gate 14" was never completed
(no `GATE14_REPORT.md` exists; `FINDINGS.md` was last updated at Gate 13 and still had two "not measured"
cells). This gate finishes that work and adds the two newer arms.

## Checking the figure Dan quoted

`FINDINGS.md`'s opt-eval margin-vs-matched-hill-climb cell already read **+209 [+126, +291]** before this
gate — checked directly against `GATE8_REPORT.md`'s own table (208.59, CI [126.02, 291.16]). It was already
correct; no fix was needed there. Left unchanged.

## Filling the muted arms' margin and held-out cells

Computed with the same method Gates 6-9 used for the other three arms: 3 matched hill-climb replicates per
race (`tools/probe_tool.py`'s `hillclimb_independent_draw`, rng seeds 1/2/3, 12 steps, full design space,
started from that race's own iteration-0 raced design), scored on `primary_metric` for the margin and on
`hairpin`/`hairpin-b`/`slalom-b` seeds 101-110 (`tools/score_heldout.py`'s convention) for held-out.

**Sanity check, done before trusting any new number:** this method reproduces both muted arms' already-
published improvement means exactly from the same underlying race data — opt-eval-muted 582.46 (sd 249.44,
n=8, matches `GATE11_REPORT.md`) and randow-maps-muted 171.17 (sd 286.56, n=8, matches `GATE13_REPORT.md`).
Strong evidence the margin/held-out numbers computed the same way are methodologically sound, not a new,
unverified pipeline.

| arm | margin vs. matched hill-climb (mean, sd, 95% CI) | held-out score (mean, sd) |
|---|---|---|
| opt-eval-muted | +547.95, sd 247.65, [+376.33, +719.56] — excludes 0 | 261.67, sd 253.95 |
| randow-maps-muted | +137.61, sd 286.16, [−60.69, +335.90] — includes 0 | 25.34, sd 38.35 |

Opt-eval-muted's margin now confirms what the improvement-vs-opt-eval comparison already showed: a real,
decisive effect of removing the critique text, and — new this gate — that effect extends to held-out
generalization (262, vs. opt-eval's own 43 and not far from opt-solo's 404). Randow-maps-muted's margin
stays indistinguishable from 0, and its held-out score (25) sits close to randow-maps' own (41), consistent
with Gate 13's "muting does not help" finding holding on a second, independent metric.

Also computed, zero cost: held-out scores for opt-eval-pre2 (mean 27.31, sd 31.42, n=6, primary set) and
randow-maps-dialogue (mean 74.16, sd 128.72, n=8) — both newly filled; their margin-vs-hill-climb cells are
left "not measured," since no matched hill-climb has been run against either's specific race set yet
(flagged in the cost table, not silently omitted).

## Opt-eval vs. randow-maps, head-to-head

Welch two-sample CI on paired improvement, both n=16: Δ = +81.56, 95% CI **[−49.86, +212.98]** — includes 0.
The two different two-agent topologies this project has tested are statistically indistinguishable from
each other, in addition to each separately failing to clearly beat free search. Added to `FINDINGS.md`'s
results section.

## Scope line

Added, per Dan's wording: one model (Haiku 5.5, no reasoning parameter ever set — Gate 16), one task (this
simulated line-follower), 12 iterations per race, no simulator tool access for any agent.

## New rows: opt-eval-pre2 and randow-maps-dialogue

Both added to the results table with n, mean improvement with its own one-sample 95% CI (same ±1.96·sd/√n
convention the existing table already used — confirmed by reverse-engineering the existing randow-maps-muted
CI, which only reproduces with z=1.96, not a t-distribution), cost/race, and held-out score (margin left
"not measured" for both, per above).

## "What we learned" and "Not tested"

Added both sections as asked, covering: the 96.5% first-critique degradation (Gate 15); the structural
timing fact, true of every critiquing role tested, that feedback is written before its own iteration's race
and only read the following iteration, after that race's real telemetry is already separately available;
geometry churn and the hold effect; the controller-tuning gradient across opt-solo/dialogue/randow-maps; and
that no arm, across any topology, has ever reached a curved sensor layout. The controller-tuning-gradient
and hold-effect items are explicitly labelled "(exploratory, Gate 18, not pre-registered)" per Dan's
instruction, since they come from Gate 18's descriptive analysis, not a pre-registered decision rule.

"Not tested" lists exactly the six items Dan named: tool/simulator access for the second agent; reasoning
enabled; stronger models; more iterations; other tasks; a Builder that sees the controller.

## Housekeeping: the now-stale "not measured" uncertainty bullet

`FINDINGS.md`'s "What's still uncertain" section previously stated the muted arms' margin/held-out were
"not measured" — now false, since this gate fills them. Replaced with an uncertainty that is actually still
open (whether randow-maps-dialogue's behavioural shift will produce a detectable score change at a larger
n) so the document doesn't contradict its own results table.

## Tests

`132 passed, 6 subtests passed` — full suite, run before the merge below.

## Merge: sim-validity-fixes → main

Tests passed, so the merge proceeded. What changed, `main` before vs. after (full `git log main..sim-validity-fixes` range, Gates 15 through 19):

- **New templates**: `opt-eval-pre2` (5-step critique-before-commit pipeline, Gate 15) and
  `randow-maps-dialogue` (hold/decline-permissive instructions on randow-maps' own topology, Gate 16-17).
- **New race data**: races 206-217 (opt-eval-pre2, 8 races + reruns) and 218-225 (randow-maps-dialogue, 8
  races), committed in full.
- **`PHASE0_FREEZE.md`**: two new pre-registration sections, §4h (opt-eval-pre2) and §4i
  (randow-maps-dialogue, plus a Gate 17 addendum fixing its decision rule to explicitly cover hold-rate,
  advice-decline quoting, controller-edit share, and a Gate-11-class defect check).
- **New reports**: `GATE15_REPORT.md` through `GATE19_REPORT.md` (this one) — critique-before-commit
  (destructive 96.5% of the time at the first round), geometry-change diagnostics on randow-maps, the
  randow-maps-dialogue run, free analysis across 24 races, and this gate's FINDINGS.md completion.
- **`FINDINGS.md`**: rewritten — scope line; both muted arms' margin/held-out filled; opt-eval-pre2 and
  randow-maps-dialogue added as rows; opt-eval-vs-randow-maps head-to-head; "What we learned" and "Not
  tested" sections added; the stale "not measured" uncertainty bullet replaced.
- No changes to the orchestrator, simulator, or test suite itself in this range — every change in this
  merge is new templates, new race data, and documentation/analysis.

**No further runs. Stopping here per Gate 19's instruction.**
