# Gate 11: opt-eval-muted causal test

Written 2026-10-16, per the pre-registration in `PHASE0_FREEZE.md` §4f (committed `ba2f4ee7a`, before any
Gate 11 race ran).

## Flag first: a real defect in the muted template, found during analysis — and which way it cuts

Removing the entityR1→action0 edge did exactly what it was meant to do (Optimizer never receives the
Evaluator's feedback text — confirmed and shown below), but it had a side effect I did not anticipate when
building the template: **it also silently breaks the Optimizer's re-entry trigger whenever the Evaluator
revises instead of approving.**

Mechanism, confirmed by reading the exact code path (`MapPackage.ready_actions` in
`orchestrator/map_package.py`): the Optimizer's `on_new_inputs` re-entry policy fires when its
`trigger_inputs` (the entities it reads, minus what it writes) show a new version since its last call.
`trigger_inputs` is derived from the topology edges — exactly the edge I removed. So when the Evaluator
writes a new `entityR1` with `decision: revise`, the Optimizer's `trigger_inputs` (now just `entityPub0` and
`entityR2A`) haven't changed, and it is never marked ready to produce a second candidate. `entity1` (the
approved build) never gets written, the race action is permanently blocked on it, and the whole iteration
ends `"workflow stalled: no action can run"` — unscored.

**This happened in 7 of 96 iteration-attempts, across 4 of the 8 races** (confirmed from each iteration's
own `outcome.json`): race-183 (iterations 6, 7), race-187 (iterations 2, 3, 7), race-188 (iteration 1), and
**race-182's iteration 11 — its last**, so race-182's effective final design is iteration 10's, not 11's
(handled the same way earlier gates handled truncated races: reported on its own last-complete iteration,
not discarded). The other 4 races (184, 185, 186, 189) never hit this — every Evaluator review in them
happened to approve on the first pass.

**This is a change to the two-call structure beyond what was asked** — Dan's spec was explicit that the
Evaluator "is still called, still approves, and its decision still gates the race," preserving the
revise-and-resubmit mechanic; this defect removes that mechanic's ability to ever resolve a revise within
opt-eval-muted. I did not catch it before running because the smoke test (2 mock iterations) happened not
to hit a revise decision.

**Why I don't think this invalidates the verdict below, and may understate it:** every one of the 7 lost
iterations is a wasted, unscored iteration — strictly less opportunity to improve, never more. If this
defect has any effect on the measured result, it should pull muted's improvement *down*, toward opt-eval's
(less effective time to get better), not up toward opt-solo's. The result below shows muted closer to
opt-solo despite this handicap, not because of it. I have not patched the template or re-run anything — no
extra races beyond the pre-registered 8 were run. If a clean re-run (fixing the re-entry condition, e.g. by
adding an explicit trigger on the Evaluator's own re-invocation rather than on entityR1's version) matters
to you, say so and I'll pre-register it as its own gate rather than doing it unprompted.

## The diff (confirmed before running anything, see commit `ba2f4ee7a`)

`actors`, `actions` (including every word of both roles' instructions), and `entities` compare
**byte-identical** between `opt-eval` and `opt-eval-muted` (checked programmatically, not just eyeballed).
The only topology change: `edge1R1U` (entityR1 used by action0) removed, and `edge1R1G`'s `direction:
return` tag dropped (required for the return-pair validator once the used-by edge is gone; `direction` is
read in exactly one place in the whole codebase — that validator — confirmed by search, so this has no
other effect).

Reconstructing the real rendered prompts (same method as Gate 9) at iteration 1 confirms the effect is
exactly as scoped:
- **Optimizer's prompt:** loses `entityR1` from `authorized_inputs` and from its one historical "received"
  record in `history`. `instructions`, `your_role`, `downstream_dependents`, `objective`, `response_shape`,
  `required_outputs`, and every output contract are byte-identical to opt-eval's.
- **Evaluator's prompt:** loses the now-readerless `entityR1` entry from its own `downstream_dependents`
  (it no longer has anyone to report as reading that output) — the one second-order consequence of the
  single edge change. Its own `instructions`, `your_role`, and `authorized_inputs` are unaffected.
- The release mechanism (`_apply_release` in `executors.py`) reads the Evaluator's decision directly from
  its in-memory output, not through any topology edge, so it is untouched — confirmed by the race data
  itself: every one of the 8 races' *approved* iterations raced normally with the Evaluator's decision still
  gating `entity1`.

## Pre-registered causal test result

| arm | n | mean improvement | sd | notes |
|---|---:|---:|---:|---|
| opt-eval (existing) | 16 | 242.46 | 184.27 | Gate 8 |
| opt-solo (existing) | 16 | 664.70 | 160.96 | Gate 8 |
| **opt-eval-muted** | 8 | **582.46** | 249.44 | race-182 scored on iteration 10 (its last complete), per above |

| comparison | Δ | SE | 95% CI |
|---|---:|---:|---|
| muted − opt-eval | +340.00 | 99.50 | [+144.99, +535.02] — **excludes 0** |
| muted − opt-solo | −82.24 | 96.94 | [−272.23, +107.76] — includes 0 |

**Decision, applying the pre-registered rule exactly:** muted's mean (582.46) is within 100 points of
opt-solo's (664.70) — gap 82.2 — **and** the CI for muted vs. opt-eval excludes 0. **Verdict: "feedback text
is the cause."** Removing only the Evaluator's feedback text and requested_changes, while keeping the
Evaluator called, approving, and gating the race, moves the Optimizer's outcome from opt-eval's territory
to within measurement range of opt-solo's — closer to a second-agent-removed arm than to the original
two-agent arm it was built from.

## Per-iteration learning curve (mean dev score, overlaid)

```
iteration:         0     1     2     3     4     5     6     7     8     9    10    11
opt-eval:         69   135   144   186   197   227   237   247   281   273   305   324
opt-eval-muted:   74   313   354   495   407   503   636   657   631   661   661   683
opt-solo:         79   250   350   408   473   587   564   621   693   716   754   774
```
(muted's curve is the mean over whichever of the 8 races actually scored that iteration — 6 to 8 races
contribute at any given point, fewer at the iterations lost to the stall defect above; every other point has
all 8.) Muted tracks far closer to opt-solo's trajectory than opt-eval's from iteration 1 onward, consistent
with the headline result.

## Tokens per iteration and cost per race

- Mean tokens per race: 660,759 (≈55,063/iteration). Every race ran exactly 12 Optimizer calls and 12
  Evaluator calls — no race in this batch ever needed a revision round that actually completed (the ones
  that didn't are the stalled iterations above; every approved iteration was approved on the Evaluator's
  first look, same single-pass pattern already seen in opt-eval).
- Mean Optimizer (`action0`) tokens per call: ≈23,580.
- **Mean cost per race: $0.0886 (sd $0.0061)** — in line with opt-eval's own historical $0.09-0.13/race,
  not closer to opt-solo's cheaper $0.042/race, since the two-call structure (and its token cost) is
  unchanged by muting the feedback text alone.
- **Total cost: $0.7088** for all 8 races — under the $1.00 estimate, well under the per-race $0.30 cap
  (highest single race: $0.0953), zero harness faults, zero reruns needed.

## Operational finding: `/credits` did not move during the run

Per Gate 10's fix, I checked `/api/v1/credits` before and after each wave, as instructed. **It read exactly
$3.1021 at all four checkpoints** (start, before wave 1, after wave 1, before/after wave 2, end) despite
~$0.71 of confirmed real spend (both from the summed per-call `cost_usd` and from `/auth/key`'s usage figure
moving over the same window). `/credits` is the right endpoint for an *absolute* balance figure (Gate 10),
but it appears to update on a lag of at least the ~11 minutes this run took, not in anything like real time.
**Practical consequence: checking `/credits` "after each batch" did not provide a working in-flight safety
net this run — it would not have caught an overrun during the batch, only sometime after.** No harm resulted
here since total spend stayed far under the reserve regardless, via the per-race cap. For any gate where the
reserve margin is tighter, the per-race cap (checked from that race's own live events, available
immediately) should be treated as the real-time guard; `/credits` is a trustworthy but slow-to-settle
sanity check, not a live one.
