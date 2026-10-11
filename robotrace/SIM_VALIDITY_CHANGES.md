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

## Not done

- Tracks are not recalibrated for v2 (hairpin-b is now unsolved by that design but solvable; slalom tracks remain unsolved by it).
- The precision term (RMS error scale 0.15 m) is unchanged and still gives little gradient.
- Tests that need the Randow Maps checkout were not run.
- Finish rate over many seeds, rather than the mean score, is the more robust readout for learning.
