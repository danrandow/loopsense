# Phase 2 design proposal — for Dan's approval before any Phase 2 spend or code change

Written 2026-10-13. No spend, no code changes were made producing this document; everything below is a
proposal against the measured Phase 0/1 record in `PHASE0_FREEZE.md` and `PHASE1_RESULTS.md`. Six sections,
matching what was asked for. Section 3 contains a decision that reverses an earlier design assumption and is
flagged for an explicit approve/reject, not folded in as if settled.

---

## 1. Giving each topology the simulator as a tool, with a shared budget

### 1.1 What exists today

Both templates (`package-templates/randow-maps`, `package-templates/opt-eval`) share identical `evaluation`,
`simulator`, and `score` config blocks (confirmed in `PHASE0_FREEZE.md` §1) and the same three-action skeleton,
but wire it differently — this wiring *is* the topology difference the mandate's Phase 2 question is about:

| | `randow-maps` | `opt-eval` |
|---|---|---|
| action0 (`kind: model`) | Designer. Entry action, `once_per_iteration`. Writes `entity0`. | Optimizer. `on_new_inputs` — can re-run within an iteration. Writes `entity0`. |
| action1 (`kind: model`) | Reviewer. `on_new_inputs`. Writes `entity1` (the design that races) + `entityR1` directly, every time it runs. | Evaluator. `on_new_inputs`. Writes only `entityR1` (a decision). A `release` rule promotes `entity0` → `entity1` only when `entityR1.decision == "approve"`. |
| Within-iteration loop | None — one pass through action0 → action1 per iteration. | `stop_reentry_when_present` lets action0/action1 negotiate repeatedly (bounded by `budget.max_action_runs: 6`) until the Evaluator approves, *then* one design races. |
| action2 (`kind: component`, `robotrace.simulator`) | `once_per_iteration`. Evaluates `entity1`, writes `entity2`/`entityR2A`/`entityR2B`. Identical in both templates. | Same. |

So today, **both topologies get exactly one simulator evaluation per iteration** (12 iterations → 12 evaluations
per race), matching Arm A's structure (`tools/probe_step.py --loop 12`), not Arm B's (many evaluations before
one submission). `opt-eval` spends more model calls per iteration (up to 6, on internal negotiation) for the
same one evaluation; `randow-maps` spends fewer calls but has no internal critique-and-revise step before the
design races. That asymmetry in calls-per-evaluation, under an identical per-evaluation structure, is exactly
what Phase 2 was meant to compare — Phase 1 changed the question underneath it by showing that giving a *single
agent* many evaluations before one submission (Arm B) beats giving it one evaluation per round (Arm A), at a
large enough budget. Carrying that into team topologies means changing the harness, not just raising a counter.

### 1.2 What has to change

**A fork in the design, to resolve before anything else:** does Phase 2 (a) replace the current 12-iteration,
one-evaluation-per-round structure outright with a single exploration phase (team explores via the tool up to a
shared budget `N`, submits once, is scored once) — the direct team-level analogue of Arm B — or (b) keep the
12-iteration shape but let each iteration's model action(s) spend tool calls from a *running, cross-iteration*
shared pool before that iteration's one official design is simulated? (a) is the cleaner test of what Phase 1
actually measured; (b) preserves more of the existing race structure (iteration count, per-iteration feedback,
`carry_forward`) but answers a subtly different question (does *within-iteration* tool access help, iteration
by iteration, rather than one large up-front exploration). This document assumes (a) below, since it is what
Phase 1's pass is actually evidence for, but (b) is a real alternative and not run or recommended over (a) here
without a decision.

Concrete changes, assuming (a):

1. **`orchestrator/executors.py`**: a new executor path for `kind: model` actions that support tool calls — the
   current `PackageExecutor` machinery (`executors.py:202+`) builds one prompt, makes one call, and expects one
   structured JSON payload back (with `repair_attempts` only for *contract* repair, not iterative exploration).
   This needs a tool-calling loop like `tools/probe_tool.py`'s `run_agent`: send `tools: [evaluate_design,
   submit_design]`, execute `evaluate_design` calls against the simulator component, feed results back as tool
   results, force `submit_design` once budget is exhausted.
2. **A new, race-scoped (not iteration-scoped) evaluation-budget counter.** Today's budget machinery
   (`orchestrator/controller.py:90-194`) tracks *action runs* and *tokens*, reset or capped per iteration/total —
   there is no concept of a spendable, cross-iteration "evaluations used" counter, because today the simulator
   only ever runs as the deterministic once-per-iteration `action2`. A shared pool spent by tool calls from
   whichever role(s) get access needs new state that persists and is checked atomically regardless of which
   action or iteration spends it — `carry_forward` (already used for `entityR1`/`entityR2A`/`entityR2B`) is the
   existing mechanism closest to this and is the natural place to add it, but it does not today enforce a
   decrementing shared cap across actions.
3. **Which role(s) get tool access, and whether that is topology-symmetric.** The natural candidate in
   `randow-maps` is action0 (Designer) and/or action1 (Reviewer, since it is the one that actually writes
   `entity1`); in `opt-eval` the natural candidate is action0 (Optimizer, the one that revises the design)
   while action1 (Evaluator) could plausibly keep its current gate-keeping role without tool access. Giving
   tool access to a different *number* or *role* of actions per topology would itself confound the comparison —
   per `CLAUDE.md`'s charter ("Both teams get identical information and budgets"), this needs an explicit,
   matched choice (e.g., "the role that ends up writing `entity1` gets the tool, in both templates") stated and
   fixed before Phase 2 runs, not left as an implementation detail.
4. **Tool wiring reuses, not duplicates, existing code.** `evaluate_design`'s return value should be exactly
   `orchestrator/evidence.py`'s `summarise_trials` output (zero new evidence code — see
   `PHASE1_RESULTS.md`'s Gate 3 part 1 for the exact shape) and tool-call argument validation should reuse
   `orchestrator/validators.py`'s `validate_geometry`/`validate_controller` (as `tools/probe_tool.py` already
   does), feeding rejections back as tool-call errors, never aborting — consistent with the charter's "harness
   must be resilient" rule.
5. **`config/race.yaml` (both templates)**: add the shared `evaluation_budget: N` field. Decide whether
   `iterations: 12` and `max_action_runs: 6` still mean anything under design (a) (probably not — the
   evaluation budget replaces the iteration count as the thing that bounds the race) or need to be re-purposed.
6. **`action2`/`entity2`/`entityR2A`/`entityR2B`** keep their current job but run once, at the end, after the
   team submits — the final score, on the fresh validation seeds (primary metric, §3) and held-out tracks
   (secondary metric, §3), computed once per race rather than once per iteration.
7. **Entity contracts that differ today between templates** (`entity0`, `entity1`, `entity3`, `entityR1`) encode
   topology-specific role content and stay as-is — the tool-access mechanism is orthogonal to them.

None of this has been built or tested. A first team-topology race under this design should be run once, read
in full, and priced before any replicate count is committed to — the same discipline this session has used for
every single-agent change so far.

---

## 2. Which evaluation budgets to test, and why

Measured so far, single agent, Haiku 5.5, Arm B structure:

| budget cap | mean `N_evals` actually used | win-margin criterion | headroom closed |
|---:|---:|---|---:|
| 25 | ~23 (92% of cap — **budget-constrained**) | 4/10 fail | not computed (Gate 2) |
| 100 | 41.4 (41% of cap — **not budget-constrained**) | 8/10 pass | ~96% |

The agent's own behaviour at cap 100 (self-stopping at a mean of 41.4, every replicate between 26 and 54) is
itself evidence about where to look next: the natural stopping point is close to 40, well below 100. That
makes **40** the single most informative new level to test — it sits right where the cap might start to bind
again (unlike 100, which clearly does not bind), so it directly tests whether a materially cheaper budget still
clears the pass criterion, or whether 100's margin was partly a function of the agent having slack it did not
strictly need but which still helped.

**Proposed: three levels — 25 (already measured, reused at zero new cost, known fail), 40 (new, primary
target), 60 (new, only if 40 is ambiguous — bisects 40 and 100 rather than guessing a fourth point blind).** 100
itself is not proposed to be re-run; it is the already-established upper anchor. This also matters for Phase
2's cost (§5) and ceiling-effect risk (§6): a budget that passes clearly without being close to 100's ~96%
headroom closure leaves room for topology differences to actually show up in the score, rather than both teams
saturating near the same ceiling regardless of structure.

A caution on projecting cost from the cap alone: because the agent does not use its full budget, cost tracks
*actual* evaluations spent, not the nominal cap — see §5's note on why a 40-cap is not straightforwardly
"40/100 of the cost" of a 100-cap race.

---

## 3. Primary metric — proposed reversal, needs explicit approve/reject

**Proposal:** primary metric = mean score on the 30 fresh validation seeds (5000-5029, confirmed in
`PHASE1_RESULTS.md` Gate 3b part 2 as never seen by the agent's tool) **plus freshly generated tracks from the
three development families** (oval, s-bend, slalom) at zero token cost — new `{difficulty, length}` draws
within each family, scored exactly like the held-out evaluation in `tools/score_heldout.py` but staying inside
the dev families rather than switching to the fixed hairpin/hairpin-b/slalom-b set. This is mechanically cheap:
`simulator/adapter/headless.py`'s `_track_polyline` is a pure function of `{family, difficulty, length}` (e.g.
dev `slalom` is `difficulty 0.25, length 22.0`; held-out `slalom-b` is the *same family*, `difficulty 0.45,
length 20.0` — the held-out tracks are already just resampled dev-family parameters with the flag flipped), so
generating e.g. 5-10 fresh tracks per dev family by sampling difficulty/length in a range already spanned by
the existing dev/held-out pairs is a few lines, not new simulator work. **The fixed hairpin-style held-out
tracks become a secondary transfer metric, reported alongside but not used to rank teams.**

**This reverses the standing design assumption, not just a reporting preference.** Every prompt built for an
agent in this session (`probe_step.py`'s `build_loop_prompt`, `probe_tool.py`'s task block) tells it: "Your
[...] design will be raced [...] once on unseen tracks of a different shape" — the held-out race, not the
dev-score loop, was always framed to the agent (and in every evidence document this session has written,
including `SIMULATOR_REVIEW_AND_DESIGN_APPROACH.md`'s race-103 table) as the number that actually counts. This
proposal demotes that number to secondary and promotes a dev-score-family metric that is new, not previously
used for ranking anything.

**Why propose it anyway:** `PHASE1_RESULTS.md`'s Gate 3b held-out comparison is the direct evidence. The
agent's held-out mean (545.3, sd 155.4, n=10) is not clearly separated from the matched free-search baseline's
held-out mean (517.0, sd 143.1, n=20) — well inside one sd either way — while the same agent's dev-validation
score is extremely tight (sd 19.8 across the same 10 replicates) and clearly beats the baseline (8/10, §4a-ii
margins). Ranking two *teams* on held-out performance, given this much noise relative to signal, risks the
comparison being dominated by which team's designs happened to transfer to three specific unseen track shapes —
closer to measuring search-seed luck (`PHASE0_FREEZE.md` §3a already found ES held-out sd/mean ≈ 34% CV) than
measuring topology quality. Freshly generated same-family tracks test a real, if narrower, form of
generalization (new parameters, not just new noise seeds) at the same zero cost as the held-out check, and — per
§4's power calculation — the tighter sd on dev-family metrics means **far fewer replicates are needed to detect
a real topology gap** than a held-out-based comparison would need.

**This is not decided.** If rejected, §4's power calculation and §5's cost estimate should be read using the
held-out sd column instead of the dev column, which raises the required replicate count by roughly an order of
magnitude for the same effect size (see the table below).

---

## 4. Power calculation

Inputs are the only variance data this session has: Arm B's single-agent, Haiku-5.5, 100-eval-budget replicates
(`PHASE1_RESULTS.md` Gate 3/3b, n=10). These are a *proxy* for team-vs-team variance, not a measurement of it —
the caveat in §6 applies directly here. Two input columns:

- **Dev-validation** (§3's proposed primary metric): sd = **19.8** (agent's own final-score sd across the 10
  measured replicates — remarkably tight; the wide margins reported in Gate 3b came from the matched baseline's
  noise, not the agent's).
- **Held-out** (fixed tracks, §3's proposed secondary metric): sd ≈ **143-204** depending on which measured
  column — pooled matched-baseline sd 143.1, agent sd 155.4, ES-ceiling sd 203.8 (n=5, noisiest). Using 150 and
  200 below as a plausible range.

Standard two-sample, two-sided α=0.05, 80% power formula: n per arm ≈ 2·(1.96+0.84)²·σ²/Δ² ≈ 15.7·σ²/Δ², where
Δ is the minimum mean-score gap between the two teams you want to be able to detect.

| assumed team-vs-team gap Δ | n/arm, dev-validation (σ=20) | n/arm, held-out (σ=150) | n/arm, held-out (σ=200) |
|---:|---:|---:|---:|
| 10 pts | 63 | 3,533 | 6,280 |
| 20 pts | 16 | 884 | 1,570 |
| 30 pts | 7 | 393 | 698 |
| 50 pts | 3 | 142 | 252 |
| 100 pts | 1 | 36 | 63 |
| 150 pts | 1 | 16 | 28 |

**Reading:** if the dev-validation metric is adopted as primary (§3) and the real topology gap is anywhere
above ~20-30 points (on a scale where the measured agent mean score itself is ~900+ and matched-baseline runs
spread over a ~250-point range), single-digit-to-teens replicates per arm are enough. If ranking stays on
held-out score, detecting anything but a very large gap (100+ points) needs 30-60+ replicates per arm, and a
modest gap (20-30 points, plausible for a real but not dramatic topology effect) needs 400-900+ — not a
realistic Phase 2 budget. This is the sharpest, most concrete version of §3's tradeoff: the metric choice
determines whether Phase 2 is answerable with ~8-16 replicates per team (`CLAUDE.md`'s own "≥8 replicates per
team" plan) or not.

---

## 5. Cost estimate

### 5.1 Measured single-agent $/evaluation

| budget cap | measured cost | measured `N_evals` | $/evaluation |
|---:|---:|---:|---:|
| 25 (Gate 2, 1 priced replicate) | $0.0478 | 23 | $0.00208 |
| 100 (Gate 3+3b, 10 replicates pooled) | $0.9834 | 414 total | $0.00238 |

$/evaluation rises slightly with cap (larger accumulated context per call as a replicate's conversation grows),
not dramatically. **A cap of 40 should NOT be assumed to cost ~40% of a cap-100 race** — because the agent
self-stops at a mean of 41.4 even when given 100, the *actual* evaluations spent (and therefore the cost) at a
40 cap is likely close to what was already measured at the 100 cap (~$0.098/replicate), not a new, smaller
number extrapolated linearly from the nominal cap. This must be priced with one real replicate at 40 before any
replicate count is committed to, per this session's standing practice — the projection here is a starting
estimate, not a substitute for that check.

### 5.2 Why the n=10 extension (Gate 3b) cost ~1.46x more per replicate than Gate 3's first 5

Looked into, since asked: it is **not a flat $/token-rate increase across the whole batch** — it concentrates
in the batch's *first* call. Gate 3b's replicate 1 cost $0.2562 for 1,002,793 tokens; Gate 3's replicate 1 (same
cap, same model, same `N_evals` of 47) cost $0.1081 for 970,687 tokens — essentially identical tokens, 2.4x the
$/token rate. Gate 3b's remaining four replicates cost $0.328 total for 4,260,676 tokens ($0.077/1000 tokens) —
*cheaper* per token than Gate 3's own average ($0.113/1000 tokens). The likely explanation: every replicate's
prompt shares a large fixed prefix (system message, starting design, contract schema, task block), and
Anthropic/OpenRouter prompt caching discounts repeated prefixes within a short TTL (commonly ~5 minutes) — the
first call in a batch, run after the idle gap spent writing up Gate 3's results, pays full price on a cold
cache; the next four, run back-to-back seconds apart, benefit from the cache the first call just populated.
This is a plausible, evidence-consistent explanation, not a confirmed one — `tools/probe_tool.py` does not
request or log OpenRouter's cache-hit token breakdown, so it cannot be verified further without a code change
(not made here, per this instruction's "no code changes"). **Practical implication for Phase 2 costing:** the
first replicate of any batch run after a gap should be expected to cost more than the steady-state rate; batch
replicates tightly, and treat a single cold-start price check as a slight overestimate of steady-state cost,
not an exact one.

### 5.3 Total Phase 2 cost table

Per-race cost = (replicates per arm, from §4) × 2 teams × (single-agent-equivalent cost per race, from §5.1,
at whichever budget is chosen) × (an unmeasured team-coordination multiplier — no team-topology-with-tool-access
race has been run, so this is a placeholder, not a measurement). Shown at 1x (optimistic: team coordination adds
no extra token cost beyond the evaluations themselves) and 2x (a round, deliberately conservative guess pending
a real measurement):

| metric / Δ | n/arm | budget cap | cost/race (measured basis) | total @1x (2 teams) | total @2x |
|---|---:|---:|---:|---:|---:|
| dev-validation, Δ=20 | 16 | 40 (~$0.10/race, see §5.1 caveat) | $0.10 | $3.20 | $6.40 |
| dev-validation, Δ=20 | 16 | 100 ($0.098/race measured) | $0.098 | $3.14 | $6.27 |
| dev-validation, Δ=10 | 63 | 40 | $0.10 | $12.60 | $25.20 |
| held-out, Δ=100 | 36 | 100 | $0.098 | $7.06 | $14.11 |
| held-out, Δ=50 | 142 | 100 | $0.098 | $27.83 | $55.67 |

**Reading:** if the dev-validation metric is adopted and the real gap is a moderate 20 points, Phase 2 fits
comfortably in single-digit dollars even at 2x the measured per-race rate. If ranking stays on held-out score
and the real gap is a plausible-but-not-huge 50 points, cost moves into the $30-55+ range before accounting for
any team-coordination overhead at all — a materially different scale of commitment, and another concrete reason
§3's metric choice matters, not just a statistical one.

---

## 6. Risks

1. **The Phase 1 pass is fragile at exactly the boundary, not comfortably clear of it.** `PHASE1_RESULTS.md`'s
   Gate 3 (n=5) was a unanimous 5/5 sweep; Gate 3b's full n=10 came in at exactly 8/10 — the pre-registered
   pass threshold — with one replicate a near-miss tie (+9.4 margin, just under the 10-point floor) and one an
   outright loss (−35.8). A single replicate's margin moving by under one point would have flipped the result
   from "pass" to "inconclusive" (`PHASE0_FREEZE.md` §4a-iv's own banding). Phase 2 is being proposed on top of
   a result that is real but thin — if a topology comparison also comes out close to its own significance
   threshold, there will be no clean way to tell real topology signal from this same order of run-to-run noise
   without more replicates than planned.
2. **A generous shared budget could push both teams to the ceiling, erasing the comparison.** At cap 100, the
   single agent closed ~96% of the available headroom (`PHASE1_RESULTS.md` Gate 3 part 2). If Phase 2's budget
   is large enough that both `randow-maps` and `opt-eval` converge to near-ceiling scores regardless of
   structure, the comparison would show no detectable difference *because the task is saturated*, not because
   the topologies are equally good — this is the direct motivation for §2's proposal to test a tighter budget
   (40) rather than defaulting to the already-known-to-pass 100.
3. **The dev-validation sd (19.8) is single-agent noise, not measured team noise.** Multi-agent coordination —
   especially `opt-eval`'s internal negotiate-until-approved loop — could add variance beyond anything a lone
   Haiku agent showed. §4's power calculation should be treated as a lower bound on required replicates, not a
   guarantee; the first few real team-topology replicates should be used to re-estimate σ before committing to
   a final replicate count, the same "price one, check, then scale" discipline used throughout this session.
4. **A shared budget creates a new way for a topology to fail that isn't about design quality.** If one role in
   a two-role negotiation (most obviously `opt-eval`'s Optimizer/Evaluator loop) can consume evaluations faster
   than the other, or the harness's accounting of a cross-iteration shared pool has a bug, a team could lose
   not because its final design is worse but because the budget was spent unevenly — this needs an explicit
   test of the budget-accounting mechanism itself (§1.2 point 2) before trusting any Phase 2 score difference.
5. **§3's metric reversal is itself a mid-experiment validity change** if approved — exactly the kind of thing
   this session's pre-registration discipline (`PHASE0_FREEZE.md`) exists to prevent being decided after seeing
   results. Writing it here, before any Phase 2 data exists, and asking for an explicit decision rather than
   quietly adopting it, is this document's attempt to apply that same discipline to its own proposal.
6. **Cost projections in §5 inherit §5.2's unexplained caching variance and §5.3's unmeasured team-coordination
   multiplier.** Both are flagged, not resolved — the actual total for a committed Phase 2 run could reasonably
   land anywhere in the ranges shown, and should be re-checked against real spend after the first few replicates
   of whichever design is approved, before scaling to the full replicate count.
