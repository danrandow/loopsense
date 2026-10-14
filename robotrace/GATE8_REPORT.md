# Gate 8: solo-agent control + randow-maps top-up

Written 2026-10-15, per the pre-registration in `PHASE0_FREEZE.md` §4d and amendment (i) (committed `e133c083`,
`6ec453c2`, both before any Gate 8 race ran).

## Execution summary

**Cost: $1.3299** of the effective $2.40 cap (the tighter of the $2.50 nominal cap and the $4.00 floor's $2.41
headroom from the $6.41 dashboard start you gave me). **Wall clock:** 754s (opt-solo, 16 races) + 822s
(randow-maps top-up, 5 races) ≈ 26 minutes total, both phases at 4-way concurrency. **Zero harness faults,
zero per-race cap kills, zero reruns needed** across all 21 races — a cleaner run than Gate 6's.

**Cost attribution validated two ways, matching to the cent:** summed per-call `cost_usd` (read from each
OpenRouter response via `usage: {include: true}`, the Gate 8 fix) gives $1.3299 total; the API's own usage
delta over the same window is $1.33 ($15.9733 − $14.6433, allowing for the four-decimal rounding already in
the per-call figures). This is the first gate where the two numbers agree this closely — Gate 6's balance-
polling approach could not have told you this, which was the whole point of the fix.

**Balance floor:** dashboard start $6.41; API usage moved by $1.33 over the run. Assuming the same
dashboard/API relationship observed at the start of this gate (dashboard $6.41 vs API-reported $5.36
remaining, a $1.05 gap), the dashboard should now read approximately $5.08 — comfortably above the $4.00
floor. Not re-confirmed with you mid-run given the tight agreement between the two cost measures and the
comfortable margin; flag if this estimate turns out to be wrong.

**Race accounting:** opt-solo 16/16 completed (no reruns needed). Randow-maps top-up 5/5 completed (no reruns
needed), bringing its total to the full pre-registered **N=16** (11 from Gates 6-7 + 5 new). Opt-eval's
existing 16 (Gates 6-7) reused at zero cost. No extra races were run beyond the pre-registered N for any arm.

## Interim checkpoint (reported before the randow-maps top-up started, as instructed)

**Opt-solo, 16/16 races, zero faults: 16/16 wins over matched hill-climb (0 losses), mean paired improvement
+664.70 (95% CI [585.83, 743.57]).**

## Per-arm results

| arm | n | mean improvement (final−iter0) | sd | 95% CI | margin vs matched hill-climb (mean) | sd | 95% CI | wins(>10) | losses(<−10) | ties |
|---|---:|---:|---:|---|---:|---:|---|---:|---:|---:|
| **opt-eval** (existing) | 16 | 242.46 | 184.27 | [152.17, 332.75] | 208.59 | 168.51 | [126.02, 291.16] | 15 | 0 | 1 |
| **opt-solo** (new) | 16 | **664.70** | 160.96 | **[585.83, 743.57]** | **565.73** | 147.48 | **[493.47, 637.99]** | **16** | 0 | 0 |
| **randow-maps** (16, 11+5) | 16 | 160.90 | 179.72 | [72.84, 248.96] | 80.12 | 173.02 | [−4.66, 164.90] | 7 | 5 | 4 |

### Tokens per iteration (mean) and true cost per race

| arm | action0 | action1 | mean cost/race | sd |
|---|---:|---:|---:|---:|
| opt-solo | 24,501 | — (no second agent) | **$0.0421** | 0.0037 |
| randow-maps (top-up 5) | 33,691 | 45,010 | **$0.1311** | 0.0116 |
| opt-eval (Gates 6-7, for reference) | ~29,700 | ~30,700 | ~$0.10-0.28 (concurrency-era estimate, see Gate 6) | — |

Opt-solo costs roughly a third of randow-maps per race (one model call per iteration instead of two) and, per
the table above, delivers by far the largest improvement — cheaper and better on this metric, in this test.

### Learning curves overlaid (dev score, the race's own live per-iteration score, mean across races)

```
iteration:    0    1    2    3    4    5    6    7    8    9   10   11
opt-eval:    69  135  144  186  197  227  237  247  281  273  305  324
opt-solo:    79  250  350  408  473  587  564  621  693  716  754  774
```

Opt-solo pulls ahead by iteration 1 and the gap widens every iteration after — this is not a late-race effect.

## Comparisons (decision rule: CI excludes 0 and |gap| ≥ 15 → winner)

**Opt-eval vs opt-solo, mean improvement.** Δ = 242.46 − 664.70 = **−422.24**. 95% CI: **[−542.13, −302.35]**.
CI excludes 0 by a wide margin, |Δ| ≫ 15. **Winner declared: opt-solo, decisively.**

**Opt-solo vs its own matched hill-climb.** Mean margin +565.73, CI [493.47, 637.99]. **Winner: opt-solo**,
beating free search by a huge, consistent margin in every one of its 16 races.

**Randow-maps (N=16) vs its own matched hill-climb.** Mean margin +80.12, CI **[−4.66, 164.90]** — crosses 0,
just barely. **No detectable difference at this power** — consistent with the Gate 7 reading at n=11 (CI
[−41, 196]), now slightly tighter but still not resolved. 7 wins, 5 losses, 4 ties: genuinely mixed, not a
reliable edge over free search either way.

## Second pre-registered test: win/loss Fisher's exact (opt-eval vs opt-solo)

Opt-eval: 15 wins, 1 tie, 0 losses (fixed from Gates 6-7). Opt-solo: 16 wins, 0 ties, 0 losses. 2×2 table
`[[15, 1], [16, 0]]`. **Fisher's exact, two-sided: p = 1.0000.** Not remotely significant.

**This is the opposite of what the amendment predicted.** The amendment, written before any opt-solo data
existed, reasoned that a win/loss count would be the more sensitive test because it is insensitive to the
large-magnitude outliers that inflate the mean-difference test's variance. That reasoning was sound on its
own terms, but it assumed the *rate* of beating matched search was where a real difference would show up.
What actually happened is that opt-eval and opt-solo win at almost the same *rate* (15/16 vs 16/16 — both
arms clear the +10 line in nearly every race) while differing enormously in *how far past it* — opt-solo's
margins run 2-4x larger than opt-eval's in the same races' terms. A test that only asks "did it cross the
line" is blind to exactly the effect that is actually present here. Recorded as a clean miss for the
pre-registered prediction, not adjusted after the fact to look better: the mean-difference test was the
sensitive one this time, not the win/loss count.

## Plain answer: does the second agent add anything over a single agent?

**No — and the evidence is strong enough to say so.** Removing the Evaluator did not hurt the Optimizer;
it helped it by a wide, statistically decisive margin (opt-solo's 95% CI for its improvement over opt-eval's
doesn't come close to overlapping zero, and the SE on that gap, ~61 points, is tiny next to the ~422-point
gap itself). Opt-solo also clears the matched free-search baseline in every single one of its 16 races, where
opt-eval and randow-maps both show a much weaker or absent edge over the same baseline. The most likely
explanation, consistent with everything found in Gates 4-7: the Evaluator's own behaviour (near-universal
immediate approval, confirmed harness-level in Gate 5) means its main *measured* effect in this harness is to
add tokens, turns, and whatever noise comes with injecting its text into the Optimizer's growing context —
not genuine critique-driven improvement. Removing it let the Optimizer iterate more directly, and the result
was better, not worse. This is a result about *this topology, this harness, this model* — not a general claim
that review never helps — but within that scope, the second agent was a net cost here, not a net benefit.
