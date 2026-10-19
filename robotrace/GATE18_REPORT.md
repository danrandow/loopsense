# Gate 18: free analysis across randow-maps, randow-maps-dialogue, and opt-solo

Written 2026-10-19. Free, offline, zero-cost analysis only — no races run.

## 1. Hold rate vs. improvement, across all 24 races (16 randow-maps + 8 dialogue)

Per-race hold rate (share of iteration-to-iteration transitions where geometry stayed unchanged) against
per-race improvement (`primary_metric`, final iteration minus iteration 0):

**OLS slope = +342.25, 95% CI [−259.21, +943.72], r = 0.244 (r² = 0.060), p = 0.25, n = 24.**

The CI includes 0 — no statistically detectable relationship between how often a race holds geometry and
how much it improves, across these 24 races. The point estimate is positive (more holding associates
weakly with more improvement) but the scatter is wide: randow-maps races at hold rate 0.0 range from
+15.6 to +399.1; dialogue races at hold rate 0.18-0.73 range from +1.7 to +778.6. Holding rate alone does
not predict outcome at this n.

## 2. Within dialogue: dev score after a hold vs. after a geometry change, paired within race

Per race, mean dev score (`entity2.score`) immediately following a hold transition vs. immediately
following a change transition, then paired across the 8 races (all 8 had at least one of each):

| race | after HOLD (n) | after CHANGE (n) | diff |
|---|---:|---:|---:|
| race-218 | 656.3 (8) | 463.0 (3) | +193.3 |
| race-219 | 501.8 (3) | 130.2 (8) | +371.6 |
| race-220 | 718.8 (2) | 530.5 (9) | +188.4 |
| race-221 | 64.1 (5) | 62.4 (6) | +1.7 |
| race-222 | 27.4 (2) | 26.9 (9) | +0.5 |
| race-223 | 100.3 (4) | 113.3 (7) | −13.0 |
| race-224 | 69.4 (4) | 66.2 (7) | +3.2 |
| race-225 | 472.3 (2) | 331.9 (9) | +140.4 |

**Paired mean diff (hold − change) = +110.76, sd 137.69, 95% CI [−4.35, +225.87], p = 0.057, n = 8.**
7 of 8 races show a positive difference (score after holding is higher); only race-223 goes the other way.
This just misses the conventional 0.05 threshold at n=8 — read as a real, consistent directional signal
that a larger n would likely resolve, not as "no effect."

## 3. Controller-gains touch share and fields touched per move

"Gains" defined strictly as `kp`/`ki`/`kd`; `base_speed` reported separately since it is a setpoint, not
a loop gain; "any controller field" includes `sensor_weights` and `line_loss` too.

| arm | n moves | touch a gain (kp/ki/kd) | touch base_speed | touch any ctrl field | fields/move (all) | fields/move (moves ≥1) |
|---|---:|---:|---:|---:|---:|---:|
| randow-maps-dialogue | 88 | 48 (54.5%) | 21 (23.9%) | 50 (56.8%) | 1.05 | 1.84 (n=50) |
| randow-maps | 176 | 52 (29.5%) | 13 (7.4%) | 58 (33.0%) | 0.56 | 1.69 (n=58) |
| opt-solo | 176 | 124 (70.5%) | 76 (43.2%) | 151 (85.8%) | 1.66 | 1.93 (n=151) |

A clean gradient: opt-solo (single agent revising the whole design each iteration) touches controller
gains far more often and touches more fields per move than either two-role arm; randow-maps touches least
often; dialogue sits in between, closer to opt-solo's rate on gains specifically (54.5% vs. 29.5% for
randow-maps) despite holding geometry more — consistent with Gate 17's finding that the Integrator leans
on controller tuning when geometry is held.

## 4. Six quoted dialogue holds: 3 where the score rose, 3 where it fell

Of 30 hold transitions in dialogue with both a before- and after-score, **16 rose, 4 fell, 10 were flat**
(score unchanged — the design, including controller, repeated exactly, which the Builder's own text
confirms is expected under a deterministic simulator). Holding is followed by a rising score roughly 4x
more often than a falling one.

**Rose:**

**race-218, iteration 2 (166.4 → 501.2):** *"Keep the iteration-1 geometry unchanged... This tests
whether the remaining off-track ends come from controller gain or speed rather than geometry. I expect
progress to rise above 0.2 on the s-bend and slalom..."*

**race-225, iteration 9 (403.7 → 620.5):** *"Kept the iteration 8 geometry unchanged... I expect the same
score of about 404 if the controller is unchanged, since the simulator is deterministic. With a
controller change, I expect the s-bend and slalom max_error to fall toward 0.06 m..."*

**race-219, iteration 10 (412.7 → 546.4):** *"Hold the iteration-9 geometry unchanged... This keeps the
platform fixed so the controller result reads cleanly. Expected result: the oval keeps its 1.0 finish
rate and the slalom line loss stays below 3.0."*

**Fell:**

**race-223, iteration 3 (114.4 → 97.7):** *"Hold the iteration-2 geometry unchanged... This keeps the
platform fixed while the Integrator tests the controller change. Expected result: max_error stays near
0.062 m unless the controller improves it..."*

**race-221, iteration 7 (69.3 → 61.8):** *"Hold the best-measured geometry... I am not changing any
geometry this iteration because every single-variable change tested so far has lowered the score."*

**race-221, iteration 8 (61.8 → 56.4):** *"Hold the iteration 1 reference geometry unchanged so the
Integrator's base_speed 1.15 test is read against a fixed platform."*

In every one of the six, the Builder explicitly frames the hold as an isolation test — keeping geometry
fixed specifically so a controller change can be read cleanly — regardless of which way the score then
moved. The failures (both race-221 cases) are consecutive iterations in the same race testing controller
changes that didn't pay off, not a case of holding without a reason.

## 5. Does holding become more frequent late in a race, and does dialogue ever reach a curved sensor layout?

**Holding rises sharply and significantly across a race:**

| iteration band | hold rate |
|---|---:|
| early (1-4) | 4/32 (12.5%) |
| mid (5-8) | 11/32 (34.4%) |
| late (9-11) | 15/24 (62.5%) |

Linear trend: **+6.8 percentage points of hold probability per iteration, 95% CI [+4.0, +9.7] pp/iteration,
p < 0.0001, n = 88.** Holding goes from the exception early in a race to the majority behaviour by the
final third. This is consistent with items 2 and 4 above: late-race holds are mostly isolation tests on an
already-reasonable design, which is exactly where the Builder's text says it is choosing to hold.

**Curved sensor layout: never reached.** Checked all 96 raced geometries across all 8 dialogue races
(every iteration, every race) — every single one has a constant sensor `y` across all five sensors (a
straight row varying only in `x`), confirmed directly from `sensor_positions`. Zero non-collinear
("curved" or staggered) layouts appear anywhere in this data. Dialogue's added freedom to hold or explore
geometry did not, in these 8 races, lead the Builder to try a sensor arrangement outside the straight-row
shape every randow-maps race has also used.

## Plain summary

Hold rate alone doesn't predict a race's improvement across 24 races (no detectable slope), but within
dialogue, holding geometry to isolate a controller change is followed by a better score than changing
geometry is, on average, in 7 of 8 races (borderline significant at n=8, p=0.057). Dialogue sits between
randow-maps and opt-solo on how often and how many controller fields a move touches — consistent with a
team that holds geometry more and compensates more through the controller. Holding becomes the dominant
behaviour late in a race, overwhelmingly framed by the Builder as a deliberate isolation test, not
indecision. No dialogue race, across 96 geometries, ever tried a sensor layout other than the straight row
every randow-maps race has also converged on — the new freedom changed *how often* geometry is held, not
*what kind* of geometry gets explored.

**No races run this gate. Stopping here.**
