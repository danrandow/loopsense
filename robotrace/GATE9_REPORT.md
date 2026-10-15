# Gate 9: verification of the Gate 8 opt-solo result

Written 2026-10-15, per the pre-registration in `PHASE0_FREEZE.md` §4e (committed `89ff4a2fd`, before any
Gate 9 race ran).

## Flag first: likely cost overrun, please re-check the dashboard before any further paid gate

The per-call cost mechanism built for Gate 8 (and trusted there, where it matched the API's balance delta
to the cent) **did not match in this gate's replication batch**. Summed `cost_usd` across the 12 races'
`events.jsonl` = **$0.8770** (the figure the automated cap used, and the figure consistent with the
$0.11-0.13/M-token rate seen in every prior gate). But the OpenRouter account's own usage ledger moved by
**$1.3920** over the same window (confirmed by reading `limit_remaining` immediately before and after: $3.79
→ $2.29) — a $0.52 gap, implying an effective rate of $0.213/M tokens, about 60% above the established rate.

I checked the one mechanism that could plausibly explain a silent undercount — an action that exhausts all
repair attempts raises `ContractFailure` or `BudgetExhausted` without `spent_cost`, so a failed call's cost
never reaches `events.jsonl` — and ruled it out: **zero** `action_rejected` or `budget_exhausted` events
exist anywhere in this batch, only clean `action_completed`. I have not found the root cause from already-
logged data, and I have not patched anything: fixing a cost-accounting path without understanding why it
failed risks hiding the next instance rather than catching it. Logged in `CHANGELOG-autonomous.md`.

**Practical consequence:** the automated stop triggered at $0.8770 against the $0.87 effective cap (tighter
of the $1.00 nominal cap and the $4.87-dashboard-minus-$4.00-floor headroom) — but if the API's $1.3920
figure is the true spend, the gate **exceeded both the $1.00 nominal cap and the floor-derived headroom**.
Using the same ~$1.08 dashboard/API offset observed at the start of this gate ($4.87 dashboard vs $3.79 API
remaining), the dashboard is now likely around **$3.3-3.8, below your $4.00 floor**. No further paid work has
been run or is planned in this report. Please re-check the dashboard directly before authorising any further
spend — I am not treating the $1.08 offset as reliable enough to self-certify we're still above the floor.

## 1. Context diff: opt-eval vs opt-solo Optimizer prompt at iteration 1

Reconstructed the exact `base_prompt` dict the harness built for `action0` at iteration 1 in a matched pair
(race-108-opt-eval, race-144-opt-solo), re-running the harness's own prompt-assembly code (`role_brief`,
`downstream_dependents`, `objective_for_prompt`, `build_history`, etc.) against the real stored inputs and
events for that exact call — zero network calls, zero spend, byte-faithful (cross-checked: the
reconstructed token-estimate for opt-eval, 9,536, is within 1% of the real OpenRouter-measured
`input_tokens` logged for that call, 9,619).

**Every field that differs, and why:**

| field | opt-eval | opt-solo | assessment |
|---|---|---|---|
| `this_call_input_tokens_estimate` | 9,536 | 7,870 | opt-eval's prompt is **larger**, not smaller — it carries the Evaluator's feedback text. Opt-eval's Optimizer has strictly *more* context than opt-solo's, not less. |
| `action_runs_available_for_review_and_revision` | 5 | 5 | same number, different meaning: opt-eval's workflow needs at least 2 of these runs per iteration (one review, one revision) to produce a scored design; opt-solo needs only 1. Not a prompt-content difference — a structural fact about the topology. |
| `teammate_calls_not_yet_run_this_iteration` | 1 | 0 | accurately reflects "no Evaluator exists" for opt-solo — exactly the kind of accurate-constraint information the charter requires, not an added advantage. |
| `your_role.about_you` | "...from evaluation and race evidence." | "...from race evidence." | one clause, already shown in the Gate 8 diff. |
| `downstream_dependents.entity0` | points to action1 (Evaluator) | points to action2 (Race Simulator) | accurately reflects where each team's candidate goes next. |
| `iteration_plan.iteration_completes_when_present` | includes `entityR2B` | does not | opt-eval's Evaluator has its own race-data entity; opt-solo has none. |
| everything else (`authorized_output_contracts`, `public_contracts`, `objective`, `response_shape`, `required_outputs`, `history` structure) | identical | identical | same design contract, same scoring, same tracks, same history-pack shape. |

**Nothing found that advantages opt-solo for a reason other than "no Evaluator."** If anything, the one
clear asymmetry (prompt size) runs the other way — opt-eval's Optimizer sees more raw context per call, not
less, so an "information starvation" story for why opt-eval does worse does not hold up.

## 2. What the Evaluator reads vs. the Optimizer

From the topology (`base.yaml`) directly, cross-checked against a real stored payload:

- **Optimizer (`action0`) reads:** `entityPub0` (design constraints, public), `entityR1` (Evaluator
  Feedback, carried from the previous iteration), `entityR2A` (race telemetry, carried from the previous
  iteration).
- **Evaluator (`action1`) reads:** `entity0` (the candidate it's reviewing), `entityPub0` (same design
  constraints the Optimizer sees), `entityR2B` (race telemetry).

**`entityR2A` and `entityR2B` are byte-identical** (checked directly: `race-108-opt-eval/iteration-0`'s two
payloads compare equal field-for-field). The simulator writes the same evidence dict into both entities —
they are two topology-bookkeeping addresses for one race result, not a full view and a restricted one.

**So yes, the Evaluator sees real race telemetry — the same telemetry the Optimizer already has.** It does
not have access to anything the Optimizer lacks. Combined with item 1's finding (the Optimizer in opt-eval
has *more* total context than opt-solo's), this rules out an information-asymmetry explanation for Gate 8's
result in either direction.

## 3. Absolute final scores, held-out, and hill-climb references (all three arms)

Computed offline (zero cost) on every arm's actual final (iteration 11) design: `primary_metric` (fresh
validation seeds 5000-5029 + 9 fresh same-family tracks), and the held-out secondary metric
(`tools/score_heldout.py`'s convention: hairpin/hairpin-b/slalom-b, seeds 101-110). The hill-climb reference
is each race's own matched 3-replicate (1+1) hill-climb, reconstructed bit-for-bit from the same rng seeds
used in Gates 6-8 (1/2/3), scored the same two ways.

| arm | n | final primary_metric | final held-out | hill-climb final primary | hill-climb final held-out |
|---|---:|---|---|---|---|
| opt-eval | 16 | 309.86 (sd 231.55) | 42.58 (sd 59.42) | 101.27 (sd 97.96, n=48) | 10.24 (sd 4.10, n=48) |
| **opt-solo** | 16 | **738.11** (sd 171.10) | **404.44** (sd 250.40) | 172.38 (sd 134.19, n=48) | 14.06 (sd 13.58, n=48) |
| randow-maps | 16 | 273.88 (sd 261.71) | 40.69 (sd 77.98) | 193.76 (sd 204.12, n=48) | 18.79 (sd 22.73, n=48) |

(opt-eval's 309.86/231.55 reproduces Gate 6's own reported figure exactly — a useful cross-check that this
offline pipeline is consistent across gates.)

**The held-out numbers are the most important new fact in this gate.** Held-out tracks are never scored
against during the race and never influence what either team optimizes — a design that merely overfits the
primary metric should not show an advantage there. Opt-solo's held-out score (404.44) is **~10× opt-eval's
(42.58) and randow-maps' (40.69)**, and **~29× its own matched hill-climb's held-out score (14.06)** — a far
larger relative margin than even its primary-metric margin. This is evidence against "opt-solo just
overfits the scored metric better than opt-eval does" — if that were the whole story, the held-out gap
should be much smaller than the primary-metric gap, not several times larger.

## 4. Mechanism mining: opt-eval iterations 1-3, all 16 races (48 Optimizer calls)

**Correction to my own first pass:** my initial field-overlap heuristic truncated the Evaluator's feedback
text before scanning it for mentioned fields, understating how much it actually covers. Re-run on the full
text, 43 of 48 calls show the mentioned-field/changed-field overlap Gate 6 used — because the Evaluator
writes **conditional, branch-structured advice** ("if telemetry shows X, do A; if it shows Y, do B"), which
routinely names 4-5 of the ~6 controller fields across its 2-3 branches. This makes the field-overlap test
nearly uninformative here (a ceiling effect) — it cannot distinguish "followed" from "ignored" when almost
everything is mentioned somewhere. Reporting this corrected, weaker reading rather than the stronger, buggy
number from my own first attempt.

**Quantitative read (loose field-overlap, now correctly computed):** "followed" n=43, mean next-iteration
delta +42.3 (27 up / 16 down); "ignored" (no mentioned field moved) n=5, mean delta +9.0 (3 up / 2 down). The
groups are not clearly separated and n=5 is too small to draw a reliable conclusion either way — this
heuristic does not support a strong claim in this data.

**Contradiction check:** the Evaluator's `requested_changes` are written as telemetry-conditioned if/then
branches, not flat assertions — each branch is tied to a specific, future telemetry pattern ("if
line_loss_events stays at 1 per trial... test line_loss = search_right"; "if steering_oscillation rises
above 0.2... raise kd"). Reading all 48 calls' full text, **I found zero cases where the Evaluator's own
cited evidence logically contradicted its own recommended action at the time it was written** — the branch
structure makes a same-time contradiction structurally unlikely. What does happen, searching the Optimizer's
own next-iteration rationale text for falsification language ("did not fix," "not supported," "did not
improve," "regression," "fell"): **8 of the 45 iteration-2/3 transitions** (iteration 1 has no prior change
to falsify) explicitly state that the previous iteration's hypothesis was rejected by the next race's
telemetry — ordinary empirical correction, not a same-time contradiction.

**Three quoted examples**, chosen to show the range:

1. **Followed, large win** (race-108, iteration 0→1, score 26.04→71.22, +173%). Evaluator (iteration 0,
   branch 2): *"If the next race shows line_loss_events above 0 or max_error above about 0.05 m on the
   bends, lower controller.base_speed to about 1.3-1.4 and raise controller.kd from 0.05 to about
   0.15-0.2."* Telemetry: 60/60 trials off-track, 1 line-loss event/trial. Optimizer's change:
   `base_speed` 1.6→1.3, `kd` 0.05→0.15 — the branch's condition was met and its exact action taken.

2. **Ignored, flat result** (race-110, iteration 1→2, score 38.61→38.47, −0.4%). Evaluator (branch 1):
   *"After the race, if line_loss_events stays at 1 per trial and the robot still goes off track early,
   test line_loss = search_right or search_left in place of last_direction."* Telemetry: exactly that
   condition (1 line-loss event/trial, all 60 off-track). The Optimizer did not change `line_loss` at all —
   instead it raised `ki` from 0.0 to 0.4, an action not named in any of that call's three branches. Score
   essentially unchanged.

3. **Hypothesis rejected by the next race's telemetry** (race-108, iteration 2→3, score 71.22→64.26→62.48
   over two further iterations). Optimizer's own iteration-3 rationale: *"Iteration 2 (ki 0.9) scored 64.3,
   below iteration 1 (ki 0.3, score 71.2)... So the 'raise ki to cancel a steady bias' hypothesis is not
   supported."* The hypothesis (shared by the Evaluator's own prior branch) was tested and explicitly
   abandoned once telemetry disagreed with it.

## 5. Randow-maps diagnosis (zero cost)

**Structural fact, not a behavioural choice:** the Builder's output contract (`entity0`) contains only
`geometry` — no `controller` field exists in it at all. The Builder *cannot* touch the controller; that is
entirely the Integrator's domain by construction.

**What the Builder actually changes** (176 iteration-to-iteration transitions, iterations 1-11 across 16
races): `sensor_positions` 54×, `wheel_track` 46×, `mass` 38×, `sensor_size` 32×, `body_length` 15×,
`wheel_radius` 12×. `body_width` never changed once.

**What the Integrator changes:** `kp` 38×, `kd` 31×, `base_speed` 13×, `sensor_weights` 11×, `ki` 5× —
and it overrides the Builder's own geometry proposal in only **3 of 176** iterations (the Integrator almost
always passes the Builder's geometry straight through unchanged).

**Does the Builder follow the prior Integration Feedback?** Loose field-overlap test (same caveat as item
4): 103 of 172 geometry changes (60%) overlap a field named in the prior feedback; 69 do not.

**Learning curve (mean dev score per iteration) vs. opt-solo:**
```
iteration:         0     1     2     3     4     5     6     7     8     9    10    11
randow-maps:    114.8 131.4 132.6 114.2 164.2 187.1 189.5 219.2 213.9 255.0 272.7 305.6
opt-solo:        79.0 250.0 350.0 408.0 473.0 587.0 564.0 621.0 693.0 716.0 754.0 774.0
```
randow-maps starts higher (a better iteration-0 design) but grows far more slowly and plateaus around
one-third of opt-solo's final level.

### Additional item: classifying the 125 zero-finish iterations by cause

Checked all 11,520 recorded trials (16 races × 12 iterations × 60 trials) across the four candidate causes:

| cause | count |
|---|---:|
| Design failed validation/schema (rejected before racing) | **0** |
| Geometry-controller mismatch (sensor count ≠ `sensor_weights` length) | **0** |
| Runtime or controller error (`controller_errors`, invalid-design termination) | **0** |
| Ran, but never finished the track | **125** |

Every one of the 125 zero-finish iterations is the same mode: a valid design raced normally, and all 7,500
trials inside them ended with `termination_reason: "off_track"` — none stalled, none hit the step limit,
none errored, nothing was rejected. There is no schema failure, no mismatch, and no runtime error anywhere
in this dataset. 7 of the 16 races — race-111, 125, 129, 137, 139, 166, 168 — never finished a single trial
in any of their 12 iterations.

**On the mismatch category, cause attribution (facts, no design advice):** no mismatch ever occurred, but
there is a real structural gap in the contract: because the Builder's output has no `controller` field, the
harness's own cross-check (`validate_controller`, which verifies `len(sensor_weights) == sensor_count`) can
only ever run on the Integrator's call, never the Builder's. The Builder changed sensor count 7 times across
the 16 races (5↔7 sensors: race-109 iter 1 and 2, race-125 iter 1, race-127 iter 1, race-137 iter 1 and 6,
race-169 iter 1). In all 7 cases the Integrator resized `sensor_weights` to match, with zero rejections. So
the gap is real and structural — the Builder has no visibility into controller compatibility when it acts —
but it has not caused a failure in this data (7/7 clean handoffs).

**Did opt-eval or opt-solo ever hit the same failures?** No. Across their combined 88 rejected-attempt
files, zero cite a sensor-count/weights mismatch. Their rejections are a different failure mode entirely:
61/88 are output-*shape* errors (wrong top-level JSON nesting, missing `_presentation`, or an answer cut off
at the token limit) — all repaired within the same call's retry budget, never reaching a raced design.
Randow-maps had **zero** rejected attempts of any kind across all 16 races — its two-role split never
produced a malformed response, where opt-eval/opt-solo's single Optimizer occasionally did.

## 6. Paid replication (§4e)

**Pre-registered decision rule:** holds if opt-solo's mean paired improvement exceeds opt-eval's with a
Welch 95% CI on the difference that excludes 0.

**Execution:** 6 opt-eval + 6 opt-solo races, interleaved (race-170 through race-181), fresh model calls,
hill-climb baseline on fresh rng seeds 21/22/23 as pre-registered. **race-180 (opt-eval) hit the cost cap
mid-race**, after cleanly completing iterations 0-10 (confirmed via its own `outcome.json` files — iteration
11 is simply absent, not a harness fault). Scored on its last complete iteration (10) and reported
separately below, not pooled into the n=6 comparison — the same convention Gates 6-8 used for truncated
races. All 6 opt-solo races and 5 of 6 opt-eval races completed fully.

| race | team | status | iter0 primary | final primary | improvement | margin vs. matched hill-climb |
|---|---|---|---:|---:|---:|---:|
| race-170 | opt-eval | complete | 87.9 | 670.6 | +582.8 | +434.2 |
| race-172 | opt-eval | complete | 27.0 | 83.6 | +56.6 | +42.0 |
| race-174 | opt-eval | complete | 132.9 | 235.4 | +102.5 | +16.7 |
| race-176 | opt-eval | complete | 49.0 | 394.5 | +345.5 | +211.2 |
| race-178 | opt-eval | complete | 46.2 | 64.5 | +18.3 | −26.3 |
| race-180 | opt-eval | **truncated (iter 10)** | 39.9 | 42.6 | +2.7 | +16.4 |
| race-171 | opt-solo | complete | 56.1 | 895.6 | +839.5 | +798.1 |
| race-173 | opt-solo | complete | 82.4 | 767.7 | +685.3 | +563.3 |
| race-175 | opt-solo | complete | 62.9 | 923.6 | +860.7 | +821.6 |
| race-177 | opt-solo | complete | 32.6 | 735.5 | +702.9 | +685.8 |
| race-179 | opt-solo | complete | 50.5 | 771.9 | +721.4 | +674.7 |
| race-181 | opt-solo | complete | 26.8 | 730.0 | +703.1 | +676.2 |

**opt-eval (n=5 complete):** mean improvement **+221.14** (sd 239.01). **opt-solo (n=6 complete):** mean
improvement **+752.15** (sd 77.0, strikingly tight — every one of the 6 landed between +685 and +861).

**Decision:** opt-eval − opt-solo = **−531.01**, SE 111.42, 95% CI **[−749.39, −312.63]** — excludes 0 by a
wide margin. **The replication holds.** The direction and rough magnitude reproduce Gate 8's finding
(−422.24, CI [−542.13, −302.35]) on an entirely fresh set of races with fresh model calls; if anything the
gap is slightly larger here. Margin vs. matched hill-climb: opt-eval mean +135.6 (4 of 5 positive), opt-solo
mean +703.3 (6 of 6 positive, uniformly large) — consistent with Gate 8's finding that opt-solo beats free
search by a wide margin in essentially every race, where opt-eval's edge over free search is real but much
smaller and less consistent.

## Plain summary

- **Opt-solo's Gate 8 result replicates** on a fresh 5-vs-6 sample with fresh model calls: the CI excludes 0
  both times, with consistent sign and magnitude.
- **No prompt-content or information advantage explains it** — opt-eval's Optimizer has *more* context per
  call than opt-solo's, and the Evaluator sees the same race telemetry the Optimizer already has, not
  additional information.
- **It is not simple overfitting to the scored metric** — opt-solo's held-out advantage (tracks neither arm
  ever optimizes against) is proportionally larger than its primary-metric advantage, not smaller.
- **Randow-maps' learning is real but far slower than opt-solo's**, and two-thirds of its raced iterations
  never complete a single trial — exclusively from ordinary off-track failures, not validation, mismatch, or
  runtime errors; a structural contract gap around sensor-count changes exists but has never caused a
  failure (7/7 clean handoffs).
- **The one thing that needs your attention before anything else continues: the cost-tracking discrepancy
  above.** Please confirm the current dashboard balance.
