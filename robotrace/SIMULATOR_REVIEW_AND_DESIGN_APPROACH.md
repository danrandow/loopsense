# Robot Race: simulator review and approach to a consistently strong robot

Date: 2026-10-12
Scope: the upstream RobotraceSim GUI ([Koyoman/robotrace_Sim](https://github.com/Koyoman/robotrace_Sim)) and how the loopsense Robot Race actually scores robots (`simulator/adapter/headless.py`, `package-templates/randow-maps/config/race.yaml`). "All the races" is read as the six tracks the harness uses: three development tracks (oval, s-bend, slalom) and three held-out tracks (hairpin, hairpin-b, slalom-b).

---

## 1. Summary

- **The race does not run the GUI simulator.** It runs a headless adapter with synthetic sinusoidal tracks, fixed battery and motor constants, and a simple weighted-sensor PID. Only chassis geometry and sensor layout feed the physics. A robot designed in the GUI does not transfer directly, and the GUI track and motor files are ignored by the race.
- **Simulation is cheap; search is the bottleneck.** One trial takes about 0.01–0.03 s. The harness's own `tools/baseline_search.py` (zero tokens) found a design in 129 s that finishes **all six tracks, 120/120 runs, on unseen seeds**, and holds at ±20% motor bias.
- **The race teams did not reach that.** They spent about 2.1M tokens and ended at 688.5 (development) and 142.1 (held-out) for opt-eval, and 210.0 and 8.7 for randow-maps. Both teams had 0/20 slalom finishes in their final designs.
- **Sensor layout is the decisive lever** in the adapter. Gains, base speed, wheel track and line-loss policy mattered little in the ranges tested. The race teams kept a narrow, straight five-sensor row and tuned gains around it.
- **The adapter's disturbance model is thin.** The only randomness is one right-motor bias per seed (±2% in the race config) and sensor noise with standard deviation 0.001. Passing it is necessary, not sufficient.

---

## 2. How a run is scored (race template config)

Source: `package-templates/randow-maps/config/race.yaml`. Note that `experiment.yaml` (smoke mode) says `max_steps: 1200`, but the race template says **300**. Confirm which one the race uses before quoting time numbers.

- Weights: completion 500, progress 250, robustness 120, precision 70, time 60.
- Per run:

```
score = 500*completed + 250*progress
      + progress * (120*(1 - line_loss_events/8) + 70*(1 - rms_error/0.15))
      + 60*(1 - completion_time/3.0)          [only if completed]
```

- Ends when: progress ≥ 0.995 (finished); centre-line error > 0.06 m (off_track); 300 steps = 3 s (timeout); or progress rises < 0.002 over 50 steps (stalled).
- The off-track threshold is `max(0.06, tape_half + body_width/4)`. Across the design bounds it is always 0.06 m, so a robot can drift 6 cm from the line before it is cut.

**What this means for priorities.** Finishing is worth 750 of roughly 1000 points. Each line-loss event costs 15 points. Speed is worth 20 points per second of lap time (60 points over 3 s). The order is: finish every track on every seed, then minimise line losses and RMS error, then go faster. The 3 s cap binds: the best design finishes in about 2.0–2.4 s, so there is little slack.

---

## 3. What the adapter models, and what it leaves out

| Element | What the race does | Consequence |
|---|---|---|
| Track | Centre line `y = A·sin(2π·c·x/L)`, with `A = (40 + 150·difficulty) mm`, `L = length × 200 mm`, `c` by family; hairpin amplitude ×1.7 | Not closed loops; "oval" is one sine period. Peak heading: slalom ~24°, hairpin-b ~52°. The names describe frequency and amplitude, not shape. |
| Sensors | Tape coverage per sensor square from the C library; positions and size are design variables (3–7 sensors) | This is the dominant design variable. |
| Controller | `signal = Σ wᵢ·sᵢ / Σ sᵢ`; `turn = kp·signal + ki·∫signal + kd·d(signal)/dt`; PWM offset `±350·turn` | The derivative is unfiltered and scaled by 1/dt = 100, so kd amplifies noise heavily. |
| Motor and battery | **Hard-coded** in the step call: 7.4 V, 3 Ω, 3 A limit, gear 20, η 0.9 | The motor section of the robot spec is not used in the race, so motor choice is not a design variable. |
| Chassis | Mass, wheel track, wheel radius, yaw inertia and envelope are used | Real geometry effects are modelled to a first approximation. |
| Disturbance | Per seed: right-motor PWM × (1 ± 0.02); sensor noise sd 0.001 | Almost no noise. Seeds barely differ. |
| Latency | None: sensing, control and actuation share one 10 ms step | Real line followers have delay; a design tuned here will be too aggressive for hardware. |
| Stall rule | Active under the template config (50 steps, 0.002 progress) | Seen in practice: hairpin-b produced "stalled" terminations. |

---

## 4. What the race-103 results show

| Entrant | Development | Held-out | Tokens charged |
|---|---:|---:|---:|
| opt-eval | 688.5 (oval 20/20, s-bend 20/20, **slalom 0/20**) | 142.1 (mixed: some hairpin runs finish near 920–940, others leave the track early at 25–380) | 666k |
| randow-maps | 210.0 | 8.7 (hairpin runs leave the track almost immediately) | 1.45M (335k rejected) |

Reading of the team reports:

- Both teams searched one lever at a time from an incumbent. The opt-eval notes list speed, sensor spread, kd, kp and sensor size as each "tried against the slalom without clearing it."
- The sensor *y* placement was never varied together with *x* until the last iteration. The spread tests used a straight row.
- Slalom max error stayed at about 0.062 m, just over the 0.06 m cut-off, in every iteration.
- The opt-eval final design ran on a seed set where the held-out score fell by about 80% from development. Overfitting to three development tracks is the most likely explanation.

---

## 5. Experiments I ran (against the repo's own adapter and tools)

All runs used `tools/baseline_search.py` helpers, the template race config, dev seeds 1–20 and held-out seeds 101–120, on the Mac that hosts the loopsense folder.

**E1. Reconstructing the race-103 best design.** I rebuilt it from the iteration-11 notes (kp 2.8, kd 0.9, ki 0, base 1.1, weights [-2,-1,0,1,2], sensor size 0.012, spread ±0.024 m at y = 0.04 m). Body and mass were not in the notes, so I used the harness starting values.
Result: oval 20/20, **s-bend 1/20** (the report says 20/20), slalom 0/20.
Interpretation: the reconstruction does not reproduce the reported s-bend result. Body and mass matter, and I could not verify the race's final design file (the payload files in the repo are trial records, not designs). Treat race-103 as partly verified.

**E2. Harness search on the slalom track.** Command: `tools/baseline_search.py --track slalom --space full --evals 400 --train-seeds 10` (129 s).
- Start design: slalom 0% finish, mean 176.
- Best found: train 949, fresh validation seeds 947 (100% finish), held-out 945 (hairpin 947, hairpin-b 947, slalom-b 941; all 100%).

**E3. Found design on every track (20 seeds each).**

| Track | Finished | Mean | Min | Mean completion time |
|---|---:|---:|---:|---:|
| oval | 20/20 | 954.7 | 941.0 | 1.93 s |
| s-bend | 20/20 | 947.9 | 934.0 | 2.34 s |
| slalom | 20/20 | 946.8 | 932.3 | 2.31 s |
| hairpin | 20/20 | 947.6 | 936.6 | 2.02 s |
| hairpin-b | 20/20 | 947.6 | 937.0 | 1.96 s |
| slalom-b | 20/20 | 940.5 | 925.1 | 2.44 s |

**E4. Stress: larger motor bias.** Right-motor bias of ±2%, ±5%, ±10%, ±20%, 120 runs at each level (six tracks × 20 seeds): **120/120 finished at every level.**

**E5. Ablation from the found design (20 seeds each).**

| Change | slalom | s-bend | hairpin-b |
|---|---:|---:|---:|
| None (found design) | 20/20 | 20/20 | 20/20 |
| Sensors → race layout (5 sensors, ±24 mm straight row, weights [-2..2]) | **0/20** | **0/20** | 12/20 |
| Wheel track 0.18 → 0.14 | 20/20 | 20/20 | 20/20 |
| Gains → race gains (kp 2.8, kd 0.9, ki 0) | 18/20 | 19/20 | 17/20 |
| Base speed → 1.1 | 20/20 | 20/20 | 20/20 |
| Line-loss policy → last_direction | 20/20 | 20/20 | 20/20 |

Interpretation: in this adapter, the layout of the sensor array is what decides whether a robot can hold the slalom. Gains matter somewhat. The other levers are weak in the ranges tested.

---

## 6. The design the search found

Adapter-only. Not a physical recommendation.

```json
{
  "geometry": {
    "body_length": 0.1116, "body_width": 0.0882, "mass": 0.7101,
    "sensor_size": 0.012, "wheel_radius": 0.0241, "wheel_track": 0.18,
    "sensor_positions": [
      {"x": -0.0655, "y": 0.0365}, {"x": -0.0437, "y": 0.0423},
      {"x": -0.0218, "y": 0.0481}, {"x":  0.0000, "y": 0.0539},
      {"x":  0.0218, "y": 0.0481}, {"x":  0.0437, "y": 0.0423},
      {"x":  0.0655, "y": 0.0365}
    ]
  },
  "controller": {
    "base_speed": 1.0742, "kp": 8.0, "ki": 0.3713, "kd": 2.4657,
    "line_loss": "search_right",
    "sensor_weights": [-2, -1.1881, -0.3466, 0.0010, 0.2566, 0.8149, 1.7746]
  }
}
```

Shape of the solution: seven sensors on a shallow forward-curving arc, ±65 mm wide, with the outer sensors about 2 cm further back. This lets the edge sensors see the line earlier. The wheel track sits at its upper bound and the robot is light. The weight vector is asymmetric and the outer weight sits at the −2 bound.

The file is at `/tmp/robot_search_slalom.json` on the Mac. It is not in the repo.

---

## 7. How I would design a robot that performs consistently

1. **Pin the evaluation first.** Freeze the adapter and config, log every trial, and use common random numbers: each candidate sees the same seeds.
2. **Separate optimisation, validation and final test.**
   - Optimise on the three development tracks.
   - Validate on a separate set of generated sinusoid tracks with new amplitudes, frequencies and lengths, not the three held-out ones.
   - Final test on unseen seeds, with a sealed track set.
3. **Score the worst case, not the mean.** Use the minimum over tracks of mean score, or a low quantile over seeds. Bimodal failures (finish or leave early) are what hide in a mean.
4. **Widen the disturbance model before trusting any number.** Add:
   - sensor noise of 0.02–0.05;
   - 1–3 steps of control and sensing latency;
   - line contrast and brightness variation;
   - wheel radius and mass tolerance;
   - ±10–20% motor gain asymmetry;
   - an initial lateral offset of 1–2 cm.
   Require a pass rate of at least 95% on each axis.
5. **Search numerically, reason about structure.**
   - Use a (1+1) evolution strategy as in `baseline_search.py`, or CMA-ES, over the continuous variables (sensor positions, weights, gains, base speed, geometry).
   - Enumerate discrete choices: sensor count (3–7), sensor size, line-loss policy.
   - Multi-start from at least five random starts.
   - Cost: about 3–4 s per candidate on all six tracks with 20 seeds, so roughly 1000 candidates in an hour.
6. **Use the LLM where it adds value.** Use it to interpret search results, propose new layout families (e.g., sensor count, curvature, spacing), and check the search's blind spots. Do not use it to pick gains one at a time.
7. **Keep the design buildable.** Enforce sensor spacing of at least the sensor size, realistic mass and wheel size, and a cost or complexity penalty.
8. **Select for robustness, not the top score on the narrow model.** Pick the candidate that holds under the wider model, and keep the sealed test set untouched until the end.
9. **Validate on hardware.** Build the array, measure latency, noise and motor asymmetry, put those numbers back into the model, and re-run the search.

---

## 8. Limitations

- Six synthetic sinusoid tracks. Generalisation to other shapes is untested.
- Disturbances are narrow, and sensor noise is effectively zero (sd 0.001).
- No latency. Real hardware will likely need lower kd and softer gains than the found design.
- Motor and battery are fixed, so the robot-spec motor data does not affect race results.
- The race-103 reconstruction did not reproduce the reported s-bend result, so exact body and mass values matter and I could not verify the race's final design.
- One search run with one seed set. Repeat runs with different seeds would show whether the 947 result is stable.
- Nothing here is validated on hardware.
- The config inconsistency (`max_steps` 1200 in `experiment.yaml` vs 300 in `race.yaml`) should be resolved before comparing results across runs.

---

## 9. Implications for the Robot Race experiment

- A zero-token search reached 100% completion on all six tracks in about two minutes of compute. The two LLM teams spent about 2.1M tokens and did not clear the slalom. The score ceiling in this adapter is clearly well above what either team reached.
- If the experiment's question is about team topology, a non-LLM search baseline is a useful reference point. It shows what the simulator permits, separate from how well the teams organise their work.
- The teams' failure looks like a search-and-representation problem, not a physics one. The layout lever was never varied as a whole.

---

## 10. Reproduce

```bash
cd robotrace
python3 tools/baseline_search.py --track slalom --space full --evals 400 --train-seeds 10 --out best.json
```

Checks used in this report are E1–E5 above. They are short Python snippets that import `tools.baseline_search` and `simulator.adapter.headless` and call `run_trial` on the six tracks; they are not saved in the repo.
