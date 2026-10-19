# Simulator adapter v2 (`robottracesim-native-v2`)

Prompted by a reassessment of how RobotraceSim is used. **Scores are not comparable with earlier races**; this is a new race configuration and must not be applied to a frozen or running race.

## Changes

1. **Disturbance no longer depends on the design.** The noise generator was seeded from `seed:digest(package):track`, so any change to the package, including a change that does not alter the robot, drew different sensor noise and motor mismatch. It is now seeded from `seed:track` only. Before the change, physically identical robots finished hairpin-b 18 to 25 times out of 30 depending only on the `observation_request` text. After it, they give identical results.
2. **Body size now has an effect.** `body_length` and `body_width` were inert (the off-track threshold always evaluated to 0.06 m). Yaw inertia is now `mass * (body_length^2 + body_width^2) / 12` instead of `mass * wheel_track^2 / 12`. The design contract (`entityPub0`) says so. Smaller bodies now turn faster; there is currently no benefit to a larger body, so expect teams to move to the minimum. Track difficulty needs recalibration (see below).
3. **Time term scaled to the run cap.** It used a 60 s scale although runs end at `max_steps * 0.01` s (3 s), so it was about 0.96 for every finisher. It is now `1 - completion_time / (max_steps * DT)`, so faster finishes score more. Finished runs now score roughly 950 rather than 990.
4. The robot spec's unused `simulation_step_dt_ms: 50` now reads the step actually used (10 ms).
5. README credit reworded to say what is taken from RobotraceSim.

## Effect on the race-40-c randow-maps final design (10 seeds per track)

| Track | v1 finishes | v2 finishes |
|---|---:|---:|
| oval | 10 | 10 |
| s-bend | 10 | 9 |
| hairpin | 10 | 10 |
| hairpin-b | 8 | 0 |
| slalom, slalom-b | 0 | 0 |

The same design with the minimum body (0.08 x 0.10) finishes hairpin-b 10/10 in v2.

## Track recalibration for v2

Under v2 both slalom tracks were unsolvable by every design from races 33, 34 and 40 (65 distinct designs, 0 finishes even with the minimum body), so they gave no gradient. Slalom settings were searched over difficulty 0.15 to 0.55 and length 14 to 26 (seeds 41 to 50); finishing is easiest near length 22.

| Track | v1 setting | v2 setting |
|---|---|---|
| slalom (development) | difficulty 0.6, length 24 | difficulty 0.25, length 22 |
| slalom-b (held-out) | difficulty 0.7, length 28 | difficulty 0.35, length 18 |

oval, s-bend, hairpin and hairpin-b are unchanged. Verified on fresh seeds 101 to 110 over the same 65 designs, mean finish rate (as-is design / same design with the minimum body):

| Track | as-is | minimum body |
|---|---:|---:|
| oval | 0.67 | 0.66 |
| s-bend | 0.36 | 0.49 |
| slalom | 0.00 | 0.35 |
| hairpin | 0.38 | 0.56 |
| hairpin-b | 0.00 | 0.35 |
| slalom-b | 0.00 | 0.16 |

As-is designs from earlier races fail slalom, hairpin-b and slalom-b outright; the improvement that unlocks them is discoverable (body size is one lever). No track is all-finish or all-fail for the minimum-body population. Scripts: `tools/calibration/`.

## Harder held-out tracks (second calibration)

A free (1+1) search (`tools/baseline_search.py`, no model) trained on the development tracks reaches about 930 to 940 on all of them, so development scores saturate. Held-out scores for four such designs (different search seeds) ranged from 391 to 895, so held-out tracks are what separate them. They were then made harder so the best development-trained design does not reach 100%:

| Track | Before | After |
|---|---|---|
| hairpin (held-out) | difficulty 0.78, length 22 | difficulty 0.85, length 16 |
| hairpin-b (held-out) | difficulty 0.85, length 12 | difficulty 1.0, length 12 |
| slalom-b (held-out) | difficulty 0.35, length 18 | difficulty 0.45, length 20 |

Check on fresh seeds 201 to 220, four development-trained search designs, finish rate and held-out mean score:

| Track | rng1 | rng2 | rng3 | rng4 |
|---|---:|---:|---:|---:|
| hairpin | 100% | 100% | 0% | 100% |
| hairpin-b | 65% | 40% | 0% | 0% |
| slalom-b | 45% | 0% | 25% | 0% |
| held-out mean score | 759 | 611 | 161 | 402 |

Feasibility: designs optimised directly on the held-out tracks solved them (hairpin 100%, hairpin-b 100% in a 70-evaluation search; slalom-b 93% to 100% in two of three 350-evaluation searches, 0% in the third). One design (rng13) generalised, scoring 880 over all three held-out tracks. The tracks are hard but solvable, and generalisation is what separates designs.

## Not done

- Calibration used past teams' designs; agents under v2 may find other levers, so recheck after the first replicate races.
- The precision term (RMS error scale 0.15 m) is unchanged and still gives little gradient.
- Tests that need the Randow Maps checkout were not run.
- Finish rate over many seeds, rather than the mean score, is the more robust readout for learning.
