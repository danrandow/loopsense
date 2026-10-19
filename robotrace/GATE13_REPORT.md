# Gate 13: move-size audit, the zero race, key limits, and completing randow-maps-muted

Written 2026-10-19.

## Part 1, item 3: key limits (reported first, since Part 2 depends on it)

Both now well above the $2.00 stop threshold Dan set, confirmed before any Part 2 race ran:

| endpoint | meaning | value |
|---|---|---:|
| `/api/v1/credits` | real account balance | **$10.4667** |
| `/api/v1/auth/key` `limit_remaining` | distance to the per-key provisioned cap that actually rejects calls | **$19.4186** |

Both have been raised by Dan since Gate 12 (`total_credits` 40→50, key `limit` 20→40). `CLAUDE.md` updated so
every future balance check reports both numbers and stops on whichever is smaller — see the Budget and ops
section for the full rationale (Gate 12 found these answer genuinely different questions, not that one
endpoint was simply "wrong").

## Part 1, item 1: move size by arm

For every iteration-to-iteration transition, the number of fields changed and the size of the single
largest field change that iteration, as a fraction of that field's allowed range (`design_bounds`). A "bold"
move is one with any field change ≥25% of its range, per Dan's definition. Zero cost, offline, read-only.

| arm | n transitions | mean move size | median | bold share | mean fields changed/move | base_speed raised, of changes |
|---|---:|---:|---:|---:|---:|---:|
| opt-eval | 176 | 0.192 | 0.080 | 21.0% | 1.62 | 15/52 (28.8%) |
| opt-solo | 176 | 0.213 | 0.103 | 20.5% | 2.68 | 18/76 (23.7%) |
| opt-eval-muted | 87 | 0.225 | 0.071 | 27.6% | 2.48 | 12/38 (31.6%) |
| randow-maps | 176 | 0.228 | 0.143 | 28.4% | 1.90 | 3/13 (23.1%) |
| randow-maps-muted (all 10 races, incl. partial) | 96 | 0.365 | 0.236 | 50.0% | 2.73 | 2/9 (22.2%) |

**Does muted opt-eval look like solo or like opt-eval?** Like solo. Opt-eval-muted's mean fields-changed-
per-move (2.48) sits much closer to opt-solo's (2.68) than to opt-eval's own (1.62) — removing the
Evaluator's text didn't just move the score, it moved the Optimizer's *behaviour*: it starts touching more
design fields per move at once, the way the no-Evaluator-at-all arm does, not the way it did with the
Evaluator's critique narrowing its attention. Move size and bold-share point the same direction (0.225/27.6%
vs. solo's 0.213/20.5%, both well above opt-eval's own 0.192/21.0%).

**Does base_speed get raised disproportionately often?** No — the rate at which an already-identified
base_speed *change* turns out to be a *raise* is close to 1-in-4 or 1-in-3 in every arm (22-32%), no
standout. Gate 12's finding (base_speed changes are net harmful on average) isn't explained by a bias toward
raising it specifically; it holds across both raises and lowers.

**Do bolder moves precede larger score gains, within each arm?**

| arm | bold moves' mean next-score Δ | non-bold moves' mean next-score Δ |
|---|---:|---:|
| opt-solo | +82.8 | +58.1 |
| opt-eval-muted | +71.3 | +55.2 |
| opt-eval | +24.6 | +22.8 |
| randow-maps | +16.1 | +17.8 |
| randow-maps-muted | +45.6 | +16.2 |

Weakly yes in most arms (bold beats non-bold), clearly in opt-solo, opt-eval-muted, and randow-maps-muted;
essentially flat in opt-eval; marginally *reversed* in randow-maps (bold moves do very slightly worse).
None of these are strong correlations (Pearson r ranged 0.02-0.18 across arms, computed but not load-bearing
here) — "bolder tends to help a bit, inconsistently" is the honest summary, not "bold moves reliably drive
the gains."

## Part 1, item 2: the zero race

All six original randow-maps-muted races' per-iteration dev scores (entity2's own live score, not the
primary metric used for the improvement figure):

```
                     it0    it1    it2    it3    it4    it5    it6    it7    it8    it9   it10   it11
race-190:           35.8   55.8  171.3  503.2  657.9  684.9  883.9  889.3  939.3  902.0  864.9  939.3
race-191:           52.2   52.3   60.4   60.3   61.4   62.9   62.1   68.0   71.4   69.7   70.3   71.4
race-192 (the zero):356.6  341.7  304.9   66.4  118.9   78.5   78.8   65.0   78.4  356.6  204.1  356.6
race-193:          140.2  128.3  329.4  271.9  372.6  422.9  422.1  347.1  309.4  389.9  331.2  422.9
race-194 (partial): 64.3  482.7  411.7  357.3  517.1  546.1    --     --     --     --     --     --
race-195 (partial): 50.9  525.5    --   127.5  419.1  592.4    --     --     --     --     --     --
```

**The 0.0 result (race-192) is real, not a harness fault and not caused by the 403.** Checked directly:
`entity1`'s geometry and controller at iterations 0, 9, and 11 are **byte-identical**. The team explored
away from its starting design through the middle of the race (dropping to a dev score as low as 65 at
iteration 7) and then landed back on the exact same design it started with by the final iteration — a
genuine net-zero result under the final-minus-iteration-0 metric, not a bug. It raced normally throughout
(no rejected attempts, no incomplete iterations) and completed well before the 403 block (which first hit at
race-194, two races later). The §4c rerun-once rule does not apply to it, because it isn't a fault.

**Race-195's one gap (iteration 2, dev score missing) is also unrelated to the 403**, and also not a harness
fault in the sense that would call for a rerun: `iteration-2/outcome.json` shows `action0`'s output was
rejected after exhausting repair attempts (extra unauthorized top-level keys, and one attempt cut off at the
output token limit) — an ordinary, already-anticipated team-output failure, handled by the harness exactly
as designed (skip the iteration, continue). It happened during the same early batch that completed cleanly,
well before the block.

**Races 194 and 195 are trustworthy up to the block.** Every iteration they completed (0-5, minus 195's
iteration 2) is genuine, harness-correct race data — the 403 only affected what would have been their
iteration 6 onward. They remain reported separately from the primary n=8 below, per the pre-registration,
not because their earlier iterations are suspect, but because their race length differs (6 iterations vs.
12) and pooling unequal-length races would bias the paired-improvement comparison.

## Part 2: completing randow-maps-muted to n=8

**Pre-flight check, as instructed:** `/credits` $10.4667, `limit_remaining` $19.4186 — both far above the
$2.00 stop floor. Proceeded.

**4 new races (202-205), 4-way concurrency, $0.35/race cap:** all completed cleanly, zero harness faults,
zero cap hits. Total cost this batch: **$0.4762** (within the $1.00 cap). `/credits` and `limit_remaining`
both moved normally and in step with the per-call-logged cost this time (no repeat of Gate 11/12's lag or
reconciliation gap).

| race | improvement | cost |
|---|---:|---:|
| race-202 | −1.14 | $0.1213 |
| race-203 | +3.94 | $0.1299 |
| race-204 | +56.45 | $0.1087 |
| race-205 | +277.90 | $0.1162 |

**Full pre-registered primary set, n=8:**

| race | improvement |
|---|---:|
| race-190 | +831.51 |
| race-191 | +7.52 |
| race-192 | 0.00 |
| race-193 | +193.17 |
| race-202 | −1.14 |
| race-203 | +3.94 |
| race-204 | +56.45 |
| race-205 | +277.90 |
| **mean (sd)** | **+171.17 (286.56)** |

(Races 194, 195 — +442.56, +536.91 on their own 6-iteration horizon — stay separate, not pooled, as above.)

| comparison | Δ | SE | 95% CI |
|---|---:|---:|---|
| muted − randow-maps (+160.90) | +10.27 | 110.83 | [−206.96, +227.50] — includes 0 |
| muted − opt-solo (+664.70) | −493.53 | 109.01 | [−707.20, −279.87] — excludes 0 |

**Applying the pre-registered decision rule exactly as written: "not the feedback text."** Muted's mean
(+171.17) is within 100 points of randow-maps' own (+160.90, gap only 10.27) — and now cleanly, not by a
coincidence of a wide CI as the n=4 interim result was: the CI vs. randow-maps is [−207, +228], a real band
around zero, and the CI vs. opt-solo excludes 0 by a wide margin. **This supersedes Gate 12's preliminary
n=4 read with the same verdict, now at full pre-registered power.**

This stands in direct contrast to Gate 11's opt-eval-muted result ("feedback text is the cause," CI vs.
opt-eval excluding 0). Muting the Evaluator's critique moved opt-eval's result close to opt-solo's; muting
the Integrator's critique leaves randow-maps statistically indistinguishable from its own un-muted
performance, and still far below opt-solo. The two topologies' second agents are not failing for the same
reason.

### Learning curve, overlaid (n=8, mean dev score per iteration)

```
iteration:              0     1     2     3     4     5     6     7     8     9    10    11
randow-maps-muted:   117.3 142.3 156.2 182.5 229.7 228.4 215.9 249.0 253.9 291.2 266.0 310.5
randow-maps:         114.8 131.4 132.6 114.2 164.2 187.1 189.5 219.2 213.9 255.0 272.7 305.6
opt-solo:             79.0 250.0 350.0 408.0 473.0 587.0 564.0 621.0 693.0 716.0 754.0 774.0
```

Muted's curve tracks almost on top of randow-maps' own, both well below opt-solo's throughout — visually
consistent with the decision-rule verdict.

### Cost reconciliation across all 8

Total logged cost across the full n=8 (today's 4 races plus Gate 12's original 4): **$0.9615**, mean
$0.1202/race (sd $0.0102) — consistent with randow-maps-muted's earlier-measured rate and with randow-maps'
own historical $0.13-0.18/race; no cost anomaly this gate.

## Updated FINDINGS.md

`robotrace/FINDINGS.md`'s randow-maps-muted row is updated to the full n=8 result below, replacing the
Gate 12 interim figure.
