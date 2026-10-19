# Gate 15: critique before commit (opt-eval-pre2)

Written 2026-10-19/20, per the pre-registration in `PHASE0_FREEZE.md` §4h, committed before any Gate 15
race ran.

## Topology, diff, and checks before spending

Covered in full in the pre-registration (§4h) — summary here. `opt-eval-pre2` is a new 5-step linear
pipeline per iteration: Draft (Optimizer) → Critique round 1 (Evaluator) → Revise (Optimizer) → Critique
round 2 (Evaluator) → Finalize (Optimizer) → Race. The Evaluator has no approve/decline power anywhere; the
Optimizer's own final submission races unchanged.

Built as 6 distinct actor instances (3 Optimizer-stage, 2 Evaluator-round, 1 Race Simulator), each owning
exactly one action, with **zero reentry** — the harness requires exactly one action per actor, and
representing one role acting multiple times needs either a reentry trigger (the mechanism Gate 11 found
could silently break) or multiple actor instances. Chose the latter specifically to make that defect class
structurally impossible here. Confirmed: the "Common to every agent" preamble is byte-identical to
opt-eval's across all 5 model actions; information parity holds exactly (round-2 critique's reads are only
`entity1`/`entityPub0`/`entityR2A` — not the draft, not the round-1 critique); an 8-iteration mock smoke
test ran clean with exactly 6 events/iteration every time; malformed output and a genuine out-of-range
validation failure were both tested directly against this package (monkeypatched, zero spend) and both
retried/rejected cleanly through the shared `controller.py` path, no crash; rationale confirmed present and
read along at every downstream step.

## A harness-level finding, found running the races: this topology strains the shared token budget

**Race-206 ran out of its total 2,000,000-token budget at iteration 10**, ending that race truncated at 9
complete iterations, not 12 — `outcome.json`: *"token budget exhausted: action1 needs about 12,390 input
tokens plus at least 500 to answer, but 10,474 remain."* This is a direct, structural consequence of the
measurement below: **this topology costs ~181,731 tokens/iteration on average, about 2.9x opt-eval's
~62,416 and about 7.4x opt-solo's ~24,501** — the same fixed 2,000,000-token total budget that comfortably
covers every other arm's 12 iterations is only barely enough here, and wasn't enough for one of eight races.
Not a bug — the budget field is genuinely shared and genuinely fixed across arms by design — but worth
flagging plainly for anyone running this topology again: it may need a larger total-token allowance to
reliably reach iteration 11.

**Race-209's iteration 0 never completed** either, for an unrelated, ordinary reason: `action1`'s first
critique attempt was cut off at the output-token limit and the retried attempts stayed malformed, exhausting
`repair_attempts`. The pipeline correctly stalled there and resumed cleanly at iteration 1, which is why its
first *complete* iteration is 1, not 0.

**Also, mid-run: all 4 races in the second concurrency wave (210-213) hit `TimeoutError: the read operation
timed out`**, a transient network/API issue under 4-way concurrent load for this heavier (5-call) template —
each had gotten partway through 5-9 iterations before failing. Treated as harness faults per the
pre-registered rerun-once rule: reran as races 214-217, all four completed cleanly on the rerun. $0.5468 was
spent on the failed attempts' partial progress before they were abandoned (rerun restarts from iteration 0,
not a resume) — included in the $2.6941 total below, well within the $3.00 gate cap.

## Race-level result

**Primary set, n=6** (races 207, 208, 214, 215, 216, 217 — complete, un-truncated 12-iteration races):

| race | improvement |
|---|---:|
| race-207 | +438.47 |
| race-208 | +155.63 |
| race-214 | +401.37 |
| race-215 | +26.14 |
| race-216 | +230.44 |
| race-217 | +13.46 |
| **mean (sd)** | **+210.92 (181.45)** |

**Reported separately, not pooled** (same convention as every earlier truncated-race case):
- race-206: truncated tail, complete only through iteration 9. Improvement over its own available range
  (iteration 0 → iteration 9): **+11.45**.
- race-209: missing iteration 0. Improvement computed from its first complete iteration (1) to iteration 11:
  **+294.56** — not on the same baseline as the other races, informational only.

| comparison | Δ | SE | 95% CI |
|---|---:|---:|---|
| pre2 − opt-solo (+664.70, n=16) | −453.78 | 84.30 | [−619.01, −288.55] — excludes 0 |
| pre2 − opt-eval (+242.46, n=16) | −31.54 | 87.23 | [−202.52, +139.44] — includes 0 |

**Applying the pre-registered decision rule exactly as written: "hurts."** Opt-solo's improvement exceeds
pre2's with a CI that excludes 0, the direction the rule calls "hurts." For context, pre2 is statistically
indistinguishable from opt-eval itself — adding a non-gating, two-round critique on top of opt-eval's
original structure does not recover any of opt-eval's gap to opt-solo; it lands in the same place opt-eval
already was.

## Stage-level result — the more powerful test, and the headline finding of this gate

Across 85 iterations with complete draft/round-1/final stage data (8 races, fewer than ~96 because of the
truncation above):

| transition | n | improve | worsen | unchanged | mean Δ (primary) | 95% CI |
|---|---:|---:|---:|---:|---:|---|
| **draft → round 1** | 85 | 3.5% | **96.5%** | 0.0% | **−343.62** | [−387.80, −299.45] |
| round 1 → final | 85 | 21.2% | 28.2% | 50.6% | +7.14 | [−5.51, +19.79] |
| draft → final | 85 | 3.5% | 96.5% | 0.0% | −336.48 | [−379.29, −293.67] |

(Dev-track numbers are the same shape: draft→round1 worsens 97.6% of the time, mean −363.33.)

**The first critique-and-revise cycle is not a wash or a mild negative — it is overwhelmingly,
consistently destructive.** The design changes at the draft→round-1 step in 100% of iterations (85/85); the
round-1→final step changes the design in 61% (52/85), meaning the Optimizer resubmits unchanged about 39%
of the time at the second step. The second critique round (round1→final) does not show the same pattern —
its CI crosses 0, essentially a wash.

**Verified this is a real effect, not a scoring artifact**, by re-running `primary_metric` directly on one
concrete pair (race-206, iteration 3): the draft (`base_speed` 0.9, `kp` 1.2, `kd` 0.8, `ki` 0.3) scores
**638.8**, finishing the oval 100% of trials and the s-bend 93% of trials. The round-1 critique's
`design_critique` states: *"At base_speed 0.9, base_pwm is about 1843 (roughly 45 percent of full PWM).
Ground speed will be well under 1.5 m/s, so the draft will not complete..."* — this is simply wrong; the
draft was completing on two of three tracks. The Optimizer, apparently trusting that claim, revised to
`base_speed` 1.0, `kp` 1.5, `kd` 0.1, `ki` 0.8 — a design that scores **42.0**, finishing almost nothing.
This single case illustrates the most likely mechanism behind the aggregate 96.5% figure: **the critique
makes a confident, checkable claim about whether the current design completes, and is sometimes
confidently wrong — the Optimizer acts on it anyway, discarding a design that was already working.** This
is offered as the best-supported explanation found, not a claim that every one of the 85 cases shares
exactly this mechanism — a full per-case text/outcome match was not run.

## Tokens per iteration

| arm | mean tokens/iteration |
|---|---:|
| opt-solo | 24,501 |
| opt-eval | 62,416 |
| **opt-eval-pre2** | **181,731** |

Per-action breakdown (opt-eval-pre2, mean tokens/call): Draft 22,773; Critique round 1 47,918; Revise
40,290; Critique round 2 34,140; Finalize 25,443 (Race Simulator: 0, component action, no tokens).

## Cost

$2.6941 total against the $3.00 gate cap: $2.1472 on the 8 successful races (mean $0.2684/race, roughly
2.6x opt-eval's ~$0.10 and 6.4x opt-solo's ~$0.042, consistent with the token-cost ratios above), plus
$0.5468 wasted on the 4 timed-out attempts' partial progress before they were abandoned and rerun. Zero
per-race cap hits ($0.60 cap, highest successful race $0.30); `/credits` and `limit_remaining` both moved
in step with logged cost this time (no repeat of earlier gates' reconciliation gaps).

## Plain summary

Critique-before-commit, with no approval power and both rounds purely advisory, does not recover opt-eval's
gap to opt-solo — if anything the race-level point estimate is lower than opt-eval's own (though not
significantly so). The stage-level data says why plausibly: the Evaluator's first critique round routinely
makes a specific, checkable claim about completion that is sometimes wrong, and the Optimizer's own revision
discards an already-good design on the strength of that claim 96.5% of the time. The second critique round
does not show the same destructive pattern — by that point either the design has already been pulled down,
or the Optimizer is less willing to act on a second round of advice the same way. This is a different,
more specific failure mode than Gate 12's "base_speed advice is net harmful on average" finding for opt-eval
proper — here the mechanism is a verifiably wrong claim about whether the current design already works, not
a direction-of-change bias.
