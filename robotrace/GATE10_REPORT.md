# Gate 10: cost reconciliation + iteration 0→1 mechanism analysis

Written 2026-10-15. Analysis-only, as instructed — zero model calls. The only network calls made were
read-only metadata lookups (OpenRouter's `/generation` and `/credits` endpoints, and balance checks), which
incur no inference cost.

## Budget-policy update applied

Per your last message: the $4.00 floor is removed; replaced with a $0.50 reserve-against-in-flight-requests
rule for future paid work, and the Gate 9 cost-reconciliation result is to be treated as a correction
factor. Recorded in `CLAUDE.md`'s Budget and ops section. Item 1 below changes what that correction factor
should actually be, so I've updated `CLAUDE.md` accordingly rather than leaving the provisional 1.59x figure
in place.

## 1. Cost reconciliation: why Gate 9's $0.877 differed from the ledger's $1.392

**Root cause found, and it's bigger than Gate 9 — it explains the dashboard/API gap seen since Gate 6.**

I queried OpenRouter's `/api/v1/credits` endpoint (account-wide credit pool) alongside the `/api/v1/auth/key`
endpoint (the one every balance check in Gates 6-9 used) at the same moment:

| endpoint | field | value just now |
|---|---|---:|
| `/auth/key` | `limit_remaining` | $2.23 |
| `/credits` | `total_credits − total_usage` | **$3.28** |
| — | **gap between them, right now** | **$1.05** |

Your dashboard read **$3.34** moments earlier. `/credits` ($3.28) matches it to within 6 cents.
`/auth/key` ($2.23) is over a dollar off. **`/auth/key`'s `limit`/`limit_remaining` tracks a $20 per-key
budget, a different, smaller scope than the account's actual $40 credit pool that the dashboard shows.**
Every balance check this project has done since Gate 6 — including the one that set Gate 8's and Gate 9's
caps — used `/auth/key`, not `/credits`. The ~$1.05-1.08 "unexplained dashboard offset" noted repeatedly
since Gate 6 is, as far as this evidence shows, not drift or lag — it's two different endpoints answering
two different questions, and the wrong one was being read against your dashboard-stated floor the whole
time. **Fix applied: all future balance/reserve checks should use `/credits`, not `/auth/key`.**

**What this does and doesn't resolve.** It explains why my balance checks never matched your dashboard. It
does **not**, on its own, explain the specific $0.877-vs-$1.392 gap in Gate 9's per-call cost bookkeeping,
since I have no `/credits` reading from before that batch started to compute its exact delta. I checked the
three specific failure modes you named, using the per-request records I have (every `request_id` in
`events.jsonl`, 230 of them, queried against OpenRouter's `/generation` endpoint — the authoritative,
settled per-call record):

- **In-flight requests killed when the cap triggered:** none found. `run_gate9_races.py` only checks the
  cap between iterations, never mid-call, and only race-180 was actually stopped (after iteration 10
  completed cleanly — confirmed via its own `outcome.json` files). No cancelled or orphaned requests appear
  among the 230 real calls (`cancelled: false` on all of them).
- **Retried or failed calls:** none found. Zero `action_rejected` or `budget_exhausted` events exist
  anywhere in this batch — every model action succeeded on its logged attempt.
- **Calls whose responses were never recorded:** none found among the 230 I could check — every
  `request_id` in `events.jsonl` resolved to a real generation record.

**What I did find, separately:** for 18 of the 230 calls, the cost embedded in the chat-completion response
at the time (what `events.jsonl` logged) is **roughly double** the authoritative settled cost from
`/generation`, queried moments later. All 18 are streamed, reasoning-heavy calls (`native_tokens_reasoning`
in the hundreds-to-thousands). Summed across all 230 calls: logged $0.8770, authoritative-settled $0.8143 —
so this anomaly, while real and reproducible, pulls the *per-call* total **down**, not up, and cannot
explain why the account ledger showed *more* spend ($1.392) than either figure. I cannot currently explain
that remaining gap from data I have access to.

**I could not get a before/after `/credits` reading for Gate 9's specific window** (I only read `/auth/key`
during that batch) — an OpenRouter Activity export covering that exact 17-minute window, if you're able to
pull one, would settle whether the $1.392 figure itself was ever a real dollar amount or a per-key artifact
of the same kind as the dashboard offset.

**Safer guard, proposed regardless of whether the root cause is ever fully pinned down:** check `/credits`
(not a per-call cost sum) immediately before authorizing each new wave of concurrent races, not just once at
the start and end of a batch; size the check's frequency to the concurrency level (at 4 concurrent races,
check after every ~4 completed iterations, not only between full races) so no more than a bounded number of
calls can be in flight, unaccounted, when a stop decision is made; and keep the $0.50 reserve as a floor
under whatever the *lowest* of the two endpoints reports, not the per-call sum, until the per-call mechanism
itself is trusted again.

## 2. Solo vs. opt-eval at iteration 0 → 1 (all 16 races per arm)

| | opt-eval | opt-solo |
|---|---:|---:|
| mean dev-score delta (iter0→1) | **+65.9** | **+171.5** |
| median delta | +48.8 | +177.0 |
| races where a controller field (`base_speed`/`kp`/`ki`/`kd`) changed | 16/16 | 16/16 |
| races where any sensor-layout field changed (count, x, y, or size) | 10/16 | 14/16 |
| races where `sensor_y_positions` changed | **0/16** | **10/16** |
| races where sensor count changed (5→7) | 0/16 | 2/16 |

(These dev-score numbers are per-race entity2 scores — the +65.9/+171.5 means reproduce the earlier-reported
dev-curve means of 69→135 and 79→250 closely enough to be the same signal, not identical since those were
rounded curve means and these are the raw per-race deltas.)

**A clean, consistent asymmetry exists: opt-eval never touches the sensor row's y-offset (lookahead
distance) at iteration 1, in any of its 16 races. Opt-solo does so in 10 of 16.** Opt-solo also reaches a
7-sensor layout by iteration 1 in 2 races; opt-eval never does by iteration 1 (it does, once, by a later
iteration — see item 3).

**But this does not explain the score-jump gap by itself.** Checked whether touching sensor layout at
iteration 1 predicts a bigger score jump *within* each arm — it doesn't:

| arm | mean delta, geometry touched | mean delta, controller-only | n (touched / untouched) |
|---|---:|---:|---|
| opt-eval | +50.0 | **+92.4** | 10 / 6 |
| opt-solo | +171.8 | +169.4 | 14 / 2 |

In opt-eval, touching geometry is associated with a *smaller* iteration-1 jump, not a larger one (n=6
controller-only races average more than n=10 geometry-touched races). In opt-solo the two groups are
statistically indistinguishable (and n=2 for the controller-only group is too small to read anything into).
Controller-gain magnitudes are also similar between arms (mean |Δkp| 0.96 opt-eval vs 1.16 opt-solo; mean
|Δkd| 0.18 vs 0.30) — not a large enough gap to read as the explanation either. **Stated plainly: nothing in
the iteration 0→1 transition specifically — neither "solo touches sensors more" nor "solo makes bigger
controller moves" — is shown by this data to drive the score-jump gap at that one transition.** Opt-solo's
advantage is visible from iteration 1 onward as a broad, pervasive gap, not traceable to one identifiable
choice at this single step.

**Optimizer's iteration-1 change vs. the Evaluator's iteration-0 requested changes (opt-eval):** the
Evaluator's `requested_changes` are almost entirely controller-only (see item 4 below — 13 of 16 don't
mention sensors at all). Where the Optimizer *did* touch sensor layout at iteration 1 (10 of 16 races,
e.g. race-110, 112, 116, 118, 128, 132, 136, 140, 141), **I did not find a single case where that geometry
move was something the iteration-0 Evaluator had actually suggested.** The controller-field changes track
the Evaluator's conditional branches closely (already established in Gate 9); the geometry changes, when
they happen, are the Optimizer acting outside what the Evaluator's feedback covered.

## 3. Layout exploration by arm (all three)

| arm | first layout change: mean iter (median) | races changing layout at iter 1 | mean # layout changes (iters 1-11) | final layout class distribution |
|---|---:|---:|---:|---|
| opt-eval | 2.12 (1.0) | 10/16 | 3.81 | 5-sensor straight ×15, 7-sensor straight ×1 |
| opt-solo | 1.19 (1.0) | 14/16 | 5.44 | 7-sensor straight ×8, 5-sensor straight ×8 |
| randow-maps | 1.00 (1.0) | **16/16** | 6.25 | 7-sensor straight ×3, 5-sensor straight ×13 |

**No race in any arm — 48 races total — ever reaches a genuinely curved layout** (more than one distinct
sensor y-value within a single design). Every final layout in this entire dataset is a straight row at
5 or 7 sensors. Randow-maps' Builder — whose only job each iteration is geometry — starts exploring layout
in literally every race by iteration 1 and makes the most total layout changes (6.25 mean), but ends up at
7 sensors in only 3 of 16 races, fewer than opt-solo (8 of 16) despite exploring geometry more often and
earlier. Opt-eval reaches 7 sensors in only 1 of 16.

## 4. Evaluator and layout (opt-eval, iteration 0 only)

Checked all 16 iteration-0 Evaluator feedbacks (`entityR1`, written before any race has happened, the
earliest possible feedback) for any mention of sensor layout, count, or spacing:

**3 of 16 mention sensors at all. Of those, 2 of 16 recommend an actual conditional layout change; the
third only tells the Optimizer to keep the existing layout.** The other 13 of 16 never mention sensors —
every branch in those is about `base_speed`/`kp`/`ki`/`kd`/`line_loss`.

Two quoted examples:
1. *race-120, iteration 0* — mentions but does not recommend a change: *"If steering_oscillation is high,
   especially on the slalom: reduce kp by about 20 percent, or raise kd from 0.15 toward 0.3, and **keep
   sensor_weights unchanged**."*
2. *race-136, iteration 0* — recommends an actual layout change: *"If line_loss_events is above 0, **add a
   sensor at x = ±0.03, y = 0.03 with a matching weight of ±0.75 to widen the span**, and test line_loss =
   last_direction against search_left."*

## 5. Which hypotheses the data supports

**(a) Early layout exploration drives solo's lead.** Supported as *description*: solo starts exploring
layout earlier (mean first-change iteration 1.19 vs 2.12), explores more overall (5.44 vs 3.81 changes),
and ends up at 7 sensors far more often (8/16 vs 1/16). **Not supported as the proximate cause of the
iteration-1 jump specifically** — item 2's within-arm check found no association between touching layout
and a bigger score jump in either arm at that transition. Exploration frequency and score advantage are both
true of solo, but this data does not show one causing the other at this step.

**(b) Evaluator advice anchors opt-eval to gain tuning.** Supported, and the clearest, best-evidenced
finding in this gate: 13 of 16 iteration-0 Evaluator feedbacks never mention sensors; only 2 of 16 ever
recommend a layout change, in branches conditioned on telemetry that may not even fire. Every geometry
change opt-eval's Optimizer makes at iteration 1 happens outside what the Evaluator suggested, not because
of it. The Evaluator's own scope of advice is overwhelmingly, almost exclusively, about controller gains.

**(c) Neither, and the difference lies elsewhere.** Cannot be ruled out, and the within-arm null result in
item 2 points this way for the *specific* iteration-0→1 transition: whatever drives opt-solo's larger
jumps, it isn't shown to be "touched geometry" or "made a bigger gain move" at that one step, in either
arm. The overall multi-iteration gap (Gate 8/9's headline result) is not explained by this transition alone.
This analysis cannot decide between exploration-driven, Evaluator-anchoring, or some other compounding
mechanism (e.g. token/attention budget per call, number of action-runs available per iteration) as the
dominant cause of the full-race gap — only that neither (a) nor (b) is shown to operate at the single
iteration-0→1 step examined here.
