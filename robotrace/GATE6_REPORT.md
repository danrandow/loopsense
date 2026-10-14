# Gate 6: the real topology comparison

Written 2026-10-14, after all races completed, per the pre-registration in `PHASE0_FREEZE.md` §4c (committed
`76bae36c`, before any race in this gate ran).

## Execution summary

**Cost:** $3.8711 of the $4.00 cap. **Wall clock:** 3558s (~59 min) for the first pass of 32 races at 4-way
concurrency, 5117s (~85 min) total including reruns. **Driver fixed** to land races at the repo root
(`/Users/danrandow/github/loopsense/race-N-{team}`), matching races 100-104's convention — 105-107 (Gate 5,
landed inside `robotrace/` by a path mistake) were left in place, not moved.

**A real, useful finding from running this concurrently:** individual per-race cost figures logged during
concurrent execution are **not reliable** — polling a shared OpenRouter balance before/after each iteration
only correctly attributes cost to that iteration if no other concurrent race is also spending during the same
window, which is false with 4 workers. The gate-wide cumulative check (total drop from one fixed start point)
remained valid throughout and is what actually enforced the $4.00 cap; the per-race numbers quoted below are
indicative, not exact.

**Race accounting, against the pre-registered failed-race rule (§4c):**

| category | opt-eval | randow-maps |
|---|---:|---:|
| Completed all 12 iterations (full target) | 16 | 10 |
| Harness fault, rerun once, rerun succeeded | 2 (108→140-pattern: races 122,124 → reruns 140,141) | 1 (race 121 → rerun 143) |
| Harness fault, rerun once, rerun **also** faulted | 0 | 1 (race 123 → rerun 142, both `TimeoutError: read operation timed out`) |
| Killed by the $0.50 per-race cap **after** reaching iteration 12 (counts as scored, full data) | included above | included above |
| Killed by the $0.50 per-race cap **before** reaching iteration 12 (genuinely truncated) | 0 | 4 (races 113, 117, 119, 135 — stopped at 11, 9, 11, 11 iterations) |
| **Achieved N** | **16** | **11** |

The 4 truncated-early races and the 1 twice-faulted slot are **not covered by §4c as written** — the
pre-registered rule anticipated a race either completing 12 iterations (scored as delivered, however bad) or
crashing (rerun once). A per-race cost kill landing *before* iteration 12 is a third thing: not a harness
fault (nothing crashed) and not a completed race either. Decided here, logged rather than resolved
retroactively in secret: **truncated-early races are excluded from the N=16 comparison** (not comparable to a
12-iteration race) and **a twice-faulted slot is left unfilled, not retried again** (the rule says rerun once).
This is the reason `randow-maps` ends at N=11 against the pre-registered N=16 — entirely a cost-cap
consequence (randow-maps costs more per race than opt-eval, consistent with every prior gate), not a
data-quality problem with the 11 it has.

**Parallelism:** 4 concurrent workers (threads; each race's work is network-I/O-bound, so this avoided
multiprocessing complexity while still getting real wall-clock benefit). Safe because each race's files live in
an isolated, uniquely-named directory, and the shared OpenRouter balance is a valid shared ground truth for
cost tracking even when read concurrently from multiple threads.

---

## Per-arm results

### Primary metric (`primary_metric` on the final delivered design, fresh seeds 5000-5029 + fresh same-family tracks, §4b/§4c)

| arm | n | mean | sd |
|---|---:|---:|---:|
| opt-eval | 16 | **309.86** | 231.55 |
| randow-maps | 11 | **230.03** | 212.83 |
| *(reference, not a race)* untouched start design | 1 | 658.16 | — |
| *(reference, not a race)* random hill-climb, 12 steps | 16 | 729.54 | 52.06 |

### Learning curve (dev score per iteration — the race's own live score, seeds 1-20, the 3 literal dev tracks;
not the primary metric, which is only computed on the final design)

```
            it0  it1  it2  it3  it4  it5  it6  it7  it8  it9  it10 it11
opt-eval:    69  135  144  186  197  227  237  247  281  273  305  324
randow-maps: 74   82  100  100  121  151  154  171  165  207  231  266
```

Both arms show a clean, steady upward trend on their own live feedback loop — real, visible within-race
learning by the metric the race itself reports every iteration.

### Secondary metric (held-out tracks, hairpin/hairpin-b/slalom-b, seeds 101-120 — reported, not gating)

| arm | mean | sd |
|---|---:|---:|
| opt-eval | 44.04 | 63.88 |
| randow-maps | 27.11 | 24.60 |

### Tokens per iteration, per action (mean)

| arm | action0 | action1 |
|---|---:|---:|
| opt-eval (Optimizer / Evaluator) | 29,686 | 30,683 |
| randow-maps (Builder / Integrator) | 32,909 | 46,554 |

Consistent with every prior gate: randow-maps's second role (Integrator) spends notably more tokens than
opt-eval's (Evaluator), driven by its dual job (complete robot *and* Integration Feedback, every iteration).

### Cost per race (indicative given the concurrency caveat above)

opt-eval ranged roughly $0.09-0.42/race (sequential reruns landed near $0.09; concurrent runs $0.28-0.42).
randow-maps ranged roughly $0.10-0.55/race, consistently higher than opt-eval, consistent with its higher
token spend.

---

## The decision rule

**Opt-eval vs randow-maps.** Δ = 309.86 − 230.03 = **+79.83** (opt-eval ahead). Welch 95% CI: **[−89.56,
+249.21]**. The CI does not exclude 0. **No detectable difference at this power.** Pooled sd ≈ 222.4; detecting
a 15-point gap at this sd would need **~3,447 races per arm** — not a realistic next-round target at any
budget this project has used. If the topology question matters enough to pursue further, it needs either a
much larger real effect (sd this size can only resolve very large gaps at affordable N) or a fundamentally
less noisy metric, not more races at the current one.

**Opt-eval vs the random hill-climb baseline.** Δ = 309.86 − 729.54 = **−419.68**. 95% CI: **[−535.97,
−303.39]**. CI excludes 0, |Δ| ≫ 15. **The hill-climb baseline wins, decisively.**

**Randow-maps vs the random hill-climb baseline.** Δ = 230.03 − 729.54 = **−499.51**. 95% CI: **[−627.84,
−371.17]**. CI excludes 0, |Δ| ≫ 15. **The hill-climb baseline wins, decisively.**

**Each arm vs the untouched start design (658.16, single fixed reference).** Opt-eval's 95% CI [196.40,
423.32] excludes 658.16. Randow-maps's 95% CI [104.26, 355.81] excludes 658.16. **Both arms end up
significantly below even doing nothing to the design at all.**

**Reading this together:** the live, per-iteration dev score each race reports to its own agents climbs
steadily all race long (the learning-curve table) — real, visible improvement on the metric the race scores
itself against every iteration (3 dev tracks, seeds 1-20). But on the pre-registered primary metric — fresh
validation seeds *and* freshly generated tracks from the same families — both teams' final designs land
**below the untouched starting design and far below a free random search given the same 12 evaluations.**
The most likely explanation: whatever is improving the live dev score is overfitting to the exact
tracks/seed-1-20 combination the race scores against every iteration, not learning something that
generalizes even one step away (new seeds, new same-family track parameters) — precisely the failure mode
§4b's metric reversal was designed to expose, and precisely why `PHASE2_DESIGN.md` §3 flagged the old
held-out-ranking assumption as unreliable in the first place. This is a stronger, more direct version of that
same concern, now with real multi-agent race data behind it rather than a single-agent probe.

---

## Free log-mining: does the Optimizer's next design follow the Evaluator's previous feedback?

Heuristic, not semantic: for each iteration's `requested_changes` text, extract mentioned design-field names
(`base_speed`, `kp`, `ki`, `kd`, `sensor_weights`, `sensor_positions`, `sensor_size`, `wheel_track`,
`wheel_radius`, `body_width`, `body_length`, `mass`, `line_loss`), then check whether that field's value
actually changed between the reviewed candidate and the Optimizer's next submission. **This checks that a
mentioned field moved at all, not that it moved in the requested direction** — a loose, generous test, stated
plainly so the number below isn't read as more rigorous than it is.

**151 followed, 25 not followed, across 176 scored iteration-transitions in the 16 opt-eval races (86%).**

Examples:
- *race-108, iteration 1* — requested: "...raise controller.base_speed from 1.6 to about 1.8..." → changed:
  `base_speed, kd, ki, kp` (the requested field moved, along with others).
- *race-108, iteration 5* — requested: "...move geometry.sensor_positions forward to y about 0.06 (from
  0.04)..." → changed: `sensor_positions` (followed precisely).
- *race-110, iteration 4* — requested: "...keep geometry.sensor_positions at x = −0.07, −0.035, 0, 0.035,
  0.07 with y = 0.05, and raise controller.base_speed..." → changed: `base_speed` only (the "keep" instruction
  for sensor_positions was correctly honoured — not a counted miss, since nothing was asked to change there).

The 25 "not followed" cases are where a mentioned field's value was left untouched despite the feedback citing
it — not inspected further here (out of scope for this gate), but available in `/tmp/gate6_analysis.json` if
worth a closer read later.

---

## Plain-language answer

**Do the agents show learning beyond what the random hill-climb achieves with the same number of evaluations?**

**No.** Both teams improve steadily on their own live scoreboard over the 12 iterations, but on the
pre-registered, out-of-sample primary metric, both teams' final designs land significantly *below* a free,
no-token random hill-climb given the identical evaluation count — and below just leaving the starting design
untouched. The gap between the two teams is not resolvable at any affordable N (pooled sd ≈ 222, ~3,450 races
per arm needed for a 15-point gap) — but that question is secondary to the headline one, which both arms
answer the same way: neither clears the free baseline, and both likely only *appear* to learn because the
metric they're scored against during the race is the same one their proposals are implicitly tuned against,
every iteration.
