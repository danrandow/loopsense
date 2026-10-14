# Gate 5: priced test of the Part C harness changes

Written 2026-10-14. Three real races run under the Part C changes (`sim-validity-fixes`, commit `1930a7dc`),
Haiku 5.5 via OpenRouter, under Dan's live cost guard. **Note on location:** these races (`race-105`,
`race-106`, `race-107`) landed inside `robotrace/` rather than at the repo root like races 100-104/race-40 did
— a path choice in the driver script, not deliberate; left in place rather than risk corrupting the stored
absolute paths in each race's `pair.json` by moving them after the fact.

## Live cost guard: what happened

Dashboard balance before: $10.94 (Dan's binding figure, 2026-10-14). Guard: poll OpenRouter usage after every
iteration; after iteration 0, project 12x that iteration's cost; kill if projection > $1.50 or actual cumulative
> $2.00 for that race; recheck before each subsequent race against a $4.00 total cap across all three; stop if
the dashboard balance would fall below $5.00.

| race | entrant | iteration-0 projection | killed? | actual total cost |
|---|---|---:|---|---:|
| race-105 | opt-eval | $0.00 (iteration 0 itself measured $0.00000 — see rate section) | no | **$0.09125** |
| race-106 | opt-eval | $0.1520 | no | **$0.08895** |
| race-107 | randow-maps | $0.0640 | no | **$0.11564** |

None of the guards tripped. **Total spend: $0.29584** of the $4.00 cap. API-measured remaining credit moved
from $9.81 to $9.49 over the whole session block including this; the dashboard, at this rate of spend, is
nowhere near the $5.00 floor (roughly $10.94 → ~$10.64, not re-confirmed with Dan mid-run since the movement is
negligible against the stated floor).

## Corrected $/token rate (the unit error, found and fixed)

Dan was right -- the error was a factor of 1000 in my division, not anything about the underlying $ amounts
(Gate 2/3/3b's recorded per-replicate spends were always correct). Recomputed cleanly:

| source | cost | tokens | $/token | $/million tokens |
|---|---:|---:|---:|---:|
| Gate 2 Arm A r1 | $0.0235 | 212,289 | 1.107e-7 | **$0.111** |
| Gate 2 Arm B r1 | $0.0478 | 364,789 | 1.310e-7 | **$0.131** |
| Gate 3 (5 reps) | $0.3992 | 3,525,971 | 1.132e-7 | **$0.113** |
| Gate 3b (5 reps) | $0.5842 | 5,263,469 | 1.110e-7 | **$0.111** |

Tight and consistent: **$0.111-0.131 per million tokens**, not per thousand. At this rate, race-103-opt-eval's
recorded 666,417 tokens (from its own `race-report.md`) project to ~$0.075 -- in the same range as what races
105/106 actually cost ($0.089-0.116), and comfortably under the old "~$0.30/race" note, not 250x over it as my
mistaken per-thousand math briefly implied. **`CLAUDE.md` corrected** (line 36) to the measured $0.089-0.116
range and the $0.11-0.13/million-token rate, with a note that this is measured from OpenRouter balance drops,
not cross-checked against published pricing.

## Did the Evaluator's budget claims now match the ledger?

**Yes.** Reconstructed the exact `remaining_budget` object (now including the two new Part-C fields) at every
one of the 24 opt-eval iterations across races 105/106, the same method used to diagnose the problem at Gate 4.
`action_runs_available_for_review_and_revision` was 4 at every first-round call (`action_runs_remaining_this_
iteration` 5, minus the 1 now reserved for the race) and `another_revise_round_fits_in_budget` was `True`
throughout. **Zero scarcity claims appear in any of the 24 iterations' feedback text** -- compared with Gate
4's races 102-104, where a version of "only one run remains" appeared in nearly every one of 28 approvals. The
specific false claim this session diagnosed and was asked to fix has not recurred once in this test.

## Per-iteration: revise/approve, rounds, tokens

**race-105-opt-eval** (12 iterations): 11 iterations approved on the first review; **iteration 10 revised once**
(the first revision seen anywhere in the current-template regime -- Gate 4 found zero across races 102-104).
Tokens per iteration climbed steadily with accumulated history (action0/Optimizer 6k→82k input across the race;
action1/Evaluator 7.7k→91k input), consistent with the growing-context pattern seen throughout this session.

**race-106-opt-eval** (12 iterations): all 12 approved on the first review, 0 revisions.

Combined: **1 revise, 24 approvals, mean 1.04 rounds/iteration** across the 24 iterations -- a small but
non-zero uptick in revise rate from Gate 4's races 102-104 (0 revise / 28 approvals), though n=1 revision is far
too small to call a trend; could as easily be ordinary replicate-to-replicate variation.

**The one revision, in detail (race-105 iteration 10):** the Evaluator's feedback was: *"The rationale describes
outer sensors at x = ±0.040 m with middle sensors at -0.02, 0, +0.02, but the geometry block still lists x =
±0.032 m at 0.016 m spacing. The submitted geometry therefore does not test the change the rationale
describes."* Checked directly against the stored payload: **the candidate's actual geometry was already x =
±0.04 m, 0.016 m sensor size** -- the Evaluator's claim about the candidate's own content was itself incorrect,
a different kind of misreading than the budget-scarcity one, not something this gate's fix targeted or could
have targeted. The Optimizer's "revision" resubmitted an **identical** geometry and controller (confirmed
byte-for-byte via the stored payloads), narrated as a correction. Net effect: two extra model calls, zero design
change.

## Offline re-score: did revisions help, on the new primary metric?

Using `tools/fresh_tracks.py`'s `primary_metric` (dev tracks + 9 fresh same-family tracks, fresh validation
seeds 5000-5029) -- zero token cost, read-only. With only one iteration where first draft != approved design
(race-105 iteration 10), and that pair being byte-for-byte identical designs, there is nothing to score a
difference on: **the one revision this test produced had no score effect, because it produced no design
change.** Every other iteration in both races needed no offline comparison at all (first draft == approved
design, same as every iteration in Gate 4's races 102-104). This is consistent with Gate 4's finding that the
current template's revise rate is low enough that "did revisions help" rarely has more than one data point to
answer from, and this test adds exactly one more inconclusive one, not a resolution.

## Did randow-maps (race-107) behave as before? Regression check: yes

All 12 iterations completed in exactly 1 round each (no iteration ever came close to needing the reserved-run
guard -- randow-maps uses only 2 of its 5 available model runs per iteration either way). The Integrator changed
the Builder's geometry in **0 of 12 iterations**, matching Gate 4's historical ~1-in-48 pattern. No forced
releases occurred (none were possible to trigger -- there is no release rule in this topology, confirmed by the
guard code doing nothing for it, as designed). The Part C changes are a no-op for randow-maps in every
observable way this test could check.

## Is `max_action_runs: 6` enough?

Kept at 6 as instructed. With 1 run now reserved for the race, 5 are available for model actions: a full
revise-and-re-review round costs 2, so **5 available runs cover 2 full rounds with 1 run to spare** (4 of 5
used), one short of a 3rd full round (which would need 6). Race-40's historical mean (2.0-2.5 rounds/iteration,
Gate 4) and this test's own (1.04, including the one real revision) both fit comfortably inside that headroom.
**6 looks sufficient** for the revise behaviour actually observed anywhere in this project's history; a team
that insisted on 3+ full revise rounds every iteration would still hit the reserved-run guard and get force-
released rather than get a 3rd review, but nothing measured here or in race-40's logs shows that happening.
