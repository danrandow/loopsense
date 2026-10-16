# Gate 12: is the advice actually bad, and a second (partial) causal test

Written 2026-10-17. Part A is pre-registration-free, zero-cost, offline simulator work. Part B's
pre-registration is `PHASE0_FREEZE.md` §4g, committed `4265ef5d7` before any Gate 12 race ran.

## Flag first: Part B stopped at N=4 (+2 partial), not N=8 — a hard external block, not a graceful stop

The run hit **HTTP 403 Forbidden** partway through, and every retry and rerun also got 403'd. Checking
`/api/v1/auth/key` explains why: **the API key has a provisioned $20 hard limit, and spend crossed it**
(`limit_remaining: 0`, `spend_usd` slightly over `limit_usd`). This is a different thing from the account
running out of money — `/api/v1/credits` shows **$0.655 of real account balance still exists**
(`total_credits: 40`, `total_usage: 39.345`). The key itself is blocked from making any further request
regardless of that remaining balance; I cannot raise this limit myself. No further paid calls are possible
on this key until you raise it or provide a new one.

**This refines, not reverses, Gate 10's finding.** Gate 10 concluded `/credits` was "the right endpoint"
because it matches the dashboard — true for *how much money is actually left*. But `/auth/key`'s
`limit_remaining` is the thing that determines whether the *next call gets rejected* — a hard provisioned
ceiling, separate from account balance. Both numbers matter, for different questions. Also confirmed again:
`/credits` did not move once during the entire run (same lag Gate 11 found), so it genuinely could not have
served as the real-time guard either way — the per-race cap and, this time, the account's own 403 were the
only things that actually stopped spend.

**4 races completed in full (190-193).** Two more (194, 195) ran 6 of 12 iterations cleanly before the
block hit mid-race — real, usable data, reported separately below per the established truncated-race
convention, not discarded. Four reruns (196-201, three attempts total across the rerun-once logic) failed
immediately with $0 spent. Total logged cost: **$0.5582** (well under the per-race $0.35 cap on every
individual race that ran; the stoppage was the key limit, not the per-race or reserve guards tripping).

## Part A: is the second agent's advice actually bad?

**Method, stated plainly.** For every iteration ≥1 in all 16 races per arm, the prior review's
`requested_changes` branches were parsed heuristically into a (condition, single-field action) pair using
regex over the branch text — not a semantic reading. Each action was applied, alone, to the previous RACED
design, and scored on the dev tracks (seeds 1-20, the harness's own live-scoring convention) and on
`primary_metric` (fresh seeds). A branch's stated condition ("if max_error stays above X...") was checked
against that race's own actual telemetry mean. **Caught and fixed one real bug before trusting these
numbers:** an early version of the parser sometimes grabbed a number from a later, unrelated clause (e.g.
reading "0.6" out of "wheel_track 0.11 m **at 0.6** kg" instead of the real target 0.11) — fixed by
narrowing the extraction to a tight window right after the field name, with an explicit "from A to B"
override; the numbers below are post-fix. Coverage: opt-eval 480/527 branches parsed (91%); randow-maps
448/448 of the ones already filtered to a geometry ask (100%, since the filter itself required a
recognized geometry action).

### Opt-eval (176 iteration-transitions, 527 branches)

| condition status | n | improve % | worsen % | unchanged % | mean Δ (primary) |
|---|---:|---:|---:|---:|---:|
| matched | 132 | 16.7 | **31.1** | 52.3 | −3.4 |
| not matched | 105 | 20.0 | **32.4** | 47.6 | −8.6 |
| unknown/no condition | 243 | 20.6 | 23.5 | 56.0 | +1.4 |

Even when the branch's own stated telemetry condition held true, applying it alone worsens the score about
twice as often as it improves it. Applying a branch whose condition did *not* hold is worse still.

**By field** (mean primary_metric Δ, applied alone):

| field | n | mean Δ | improve % | worsen % |
|---|---:|---:|---:|---:|
| base_speed | 158 | **−9.33** | 24.7 | 38.6 |
| kd | 116 | **+8.35** | 23.3 | 27.6 |
| kp | 108 | −2.69 | 12.0 | 15.7 |
| ki | 33 | −1.85 | 6.1 | 33.3 |
| sensor_size | 26 | +6.08 | 26.9 | 7.7 |
| sensor_spread_x | 21 | −15.07 | 23.8 | 33.3 |
| line_loss | 18 | −0.29 | 0.0 | 11.1 |

**base_speed advice is net harmful and is the single most frequently offered lever (158 of 480 parsed
branches).** kd and sensor_size are the only two levers that are net *helpful* on average. ki and line_loss
are close to inert (switching line_loss policy essentially never measurably helps or hurts in this data).

**Optimizer's realized move vs. the best single branch on offer that iteration** (n=175, hindsight-best
among that iteration's own branches): mean realized Δ +22.17 vs. mean best-available-branch Δ +23.96 —
statistically indistinguishable. Race-by-race: beats the best branch 68/175, ties (within 1 point) 38/175,
falls short 69/175 — split almost exactly into thirds. **The Optimizer is not reliably better or worse than
its own best-available advice; it tracks it.**

### Randow-maps, geometry-only asks (176 iteration-transitions where the Integrator requested a specific
geometry change, 448 branches)

| condition status | n | improve % | worsen % | unchanged % | mean Δ (primary) |
|---|---:|---:|---:|---:|---:|
| matched | 104 | **30.8** | 17.3 | 51.9 | **+1.61** |
| not matched | 86 | 17.4 | 27.9 | 54.7 | −5.81 |
| unknown/no condition | 258 | 16.3 | 29.8 | 53.9 | −12.47 |

**The direction is opposite opt-eval's for the matched case:** when the Integrator's own stated telemetry
condition is actually true, applying its geometry suggestion is net *helpful* here (improve nearly double
worsen), not a wash. Un-matched or unstated-condition geometry asks are net harmful, same pattern as
opt-eval.

**By field:**

| field | n | mean Δ | improve % | worsen % |
|---|---:|---:|---:|---:|
| wheel_track | 130 | −6.57 | 20.8 | 23.8 |
| sensor_y | 79 | −4.09 | 17.7 | 25.3 |
| sensor_size | 79 | −1.87 | 21.5 | 20.3 |
| mass | 63 | **−19.30** | 17.5 | 31.7 |
| sensor_spread_x | 50 | −7.51 | 28.0 | 42.0 |
| wheel_radius | 43 | −14.76 | 14.0 | 25.6 |

(Field means are pulled down by the large un-matched/unknown bucket, consistent with the condition-status
table above — a field itself isn't the problem so much as applying it off-condition is.) **mass** is the
single worst lever on average.

**Builder's realized move vs. best single branch on offer** (n=176): mean realized Δ +14.63 vs. mean
best-available-branch Δ +10.29 — the Builder's mean edges out the best-offered branch, but race-by-race it
beats the best branch only 61/176, ties 38/176, falls short 77/176 (a plurality of iterations). The mean and
the rate point in different directions here: the Builder loses more often than it wins against its own best
option, but its wins are larger than its losses.

### Plain answer

**The second agent's advice is not uniformly bad, but it is not reliable, and it has a specific, identified
weak spot: speed.** In opt-eval, base_speed changes — the single most commonly offered lever — are net
harmful on average and worsen the score more often than they help it, even when the Evaluator's own stated
condition for making that exact change is true. This reads as "too eager to raise speed before the design
is ready for it," consistent with Dan's example hypothesis. kd and sensor_size are the two levers that
reliably help. In randow-maps, geometry advice *conditioned correctly on telemetry* is genuinely helpful on
average (the opposite finding from opt-eval) — the problem there is mass specifically, and advice applied
when its own condition doesn't hold. Neither Optimizer nor Builder is shown to systematically beat or lose
to its own best-available advice in aggregate (opt-eval: dead even; randow-maps: mixed, mean favours the
Builder, rate favours the advice) — the two agents are not adding a second, independently-better opinion so
much as drawing on largely the same signal, with speed being the one place that signal is reliably wrong.

## Part B: randow-maps-muted causal test

**What the Builder receives each iteration, checked before building anything (per Dan's stop condition):**
`entityPub0` (design constraints), `entityR1` (Integration Feedback), `entityR2A` (Geometry Race Data — race
telemetry, confirmed in Gate 9 byte-identical to the Integrator's own copy). **Telemetry is not lost by
muting entityR1** — `entityR2A` is a separate edge. Proceeded without stopping. Worth flagging anyway:
entityR1's own topology description calls it the Builder's "main way to learn what the Integrator needs,"
since the Builder never sees the controller — muting it removes that specific channel even though raw
telemetry remains.

**Gate 11 defect check, done before building (not just after):** randow-maps has no release/gate structure
at all (`action1`'s runtime has no `release` field — unlike opt-eval), so there is no approve/revise loop to
break, and `action0`'s re-entry policy is `once_per_iteration`, not `on_new_inputs`, so there is no
input-triggered re-entry for the muted edge to silently break. Confirmed topologically, then by a clean
6-iteration mock smoke test, before any paid call. **No stall defect occurred in any of the 6 real races
that produced data.**

**Diff:** `actors`, `actions` (instructions), `entities` compare byte-identical to `randow-maps` (checked
programmatically). Only change: the entityR1-used-by-action0 edge removed, its paired edge's `direction:
return` tag dropped (same reasoning as both earlier muted templates).

**Primary result (n=4, full 12 iterations):**

| race | improvement |
|---|---:|
| race-190 | +831.51 |
| race-191 | +7.52 |
| race-192 | +0.00 |
| race-193 | +193.17 |
| **mean (sd)** | **+258.05 (392.61)** |

**Two additional races, truncated at 6 of 12 iterations by the key-limit block, reported separately per
convention, not pooled into the n=4 above:** race-194 +442.56, race-195 +536.91 — both substantial despite
half the horizon; included for completeness, not the decision.

| comparison | Δ | SE | 95% CI |
|---|---:|---:|---|
| muted − randow-maps (+160.90) | +97.15 | 201.38 | [−297.55, +491.85] — includes 0 |
| muted − opt-solo (+664.70) | −406.65 | 200.38 | [−799.40, −13.90] — excludes 0 |

**Mechanical application of the pre-registered rule: "not the feedback text."** Muted's mean (+258.05) is
within 100 points of randow-maps' (+160.90, gap 97.15), and the CI vs. opt-solo excludes 0.

**This is the opposite verdict from Gate 11's opt-eval-muted test, and I do not trust it at the same
confidence** — n=4 against a pre-registered N=8, one race scored 831.5 and another scored 0.0, and the
resulting sd (392.61) is more than double either comparison arm's. The CI vs. randow-maps is enormous
([−298, +492]) — "within 100 of randow-maps' mean" is true of the point estimate but says little given how
wide that band is; a mean anywhere in roughly [−140, +360] would also have landed "within 100" by chance at
this variance. **Read this as a preliminary, likely-underpowered signal pointing toward "not the feedback
text" for randow-maps, not a confirmed result** — a genuine asymmetry with opt-eval-muted's clean finding
might be real (the Builder's "main way to learn what the Integrator needs" framing in the topology itself
suggests Integration Feedback could matter more structurally here than opt-eval's Evaluator Feedback did),
or might simply evaporate at full N=8. Re-running to the full N once the key limit is resolved would settle
this; I have not done so without being asked.

## Tokens and cost per race (randow-maps-muted)

| race | cost | tokens |
|---|---:|---:|
| race-190 | $0.1295 | 935,761 |
| race-191 | $0.1090 | 768,286 |
| race-192 | $0.1348 | 966,176 |
| race-193 | $0.1121 | 806,777 |
| race-194 (6 iters) | $0.0430 | 267,789 |
| race-195 (6 iters) | $0.0298 | 239,758 |
| race-196 to 201 | $0 | 0 (blocked before any call) |

Full-length races average $0.1213/race (~75,900 tokens/iteration) — in line with randow-maps' historical
$0.13-0.18/race, not closer to opt-solo's cheaper single-agent cost, consistent with the two-call structure
being unchanged by muting feedback text alone.

## Learning curve (mean dev score, n=4 full-length races)

```
iteration:         0     1     2     3     4     5     6     7     8     9    10    11
randow-maps-muted:146.2 144.5 216.5 225.5 302.7 312.3 361.7 342.3 349.6 429.6 367.6 447.6
randow-maps:      114.8 131.4 132.6 114.2 164.2 187.1 189.5 219.2 213.9 255.0 272.7 305.6
opt-solo:          79.0 250.0 350.0 408.0 473.0 587.0 564.0 621.0 693.0 716.0 754.0 774.0
```
Muted's curve sits above randow-maps' throughout and well below opt-solo's — visually consistent with the
"not the feedback text" read, with the same n=4 caveat as above. The per-race spread behind this mean is
large: race-190 alone reaches 939 by the end; race-191 stays flat near 70 the whole race.

## Resource note, unrelated to the science

Several of this gate's offline analysis jobs got killed by the OS under memory pressure when run via this
session's auto-backgrounding (the machine is a shared personal laptop, not a dedicated compute box — dozens
of Chrome tabs and another active `claude` session were competing for RAM at the time). Switching to
explicit background launches with output redirected to a log file, polled directly, resolved it without
needing less parallelism. Noting this only so a future session doesn't waste time assuming a memory or
concurrency bug in the analysis code itself.
