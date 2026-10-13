# Gate 4: information agents are told, log-mined team behaviour, offline re-scoring

Written 2026-10-13. Tool-access build cancelled per instruction — no code changes, no spend, nothing run
through an LLM. Everything below is either (a) quoted directly from already-committed instruction/prompt text,
(b) mined from already-existing race logs (races 100-104, race-40 a/b/c), or (c) computed by re-running the
existing offline simulator (`simulator/adapter/headless.py`) on already-existing design payloads — the
re-scoring methodology was validated by reproducing a real race's recorded score exactly (see §3).

---

## 1. What the Evaluator (opt-eval) and the Reviewer (randow-maps) are actually told

First, a naming correction: `randow-maps`'s action1 role is not called "Reviewer" in its own instructions — its
label is **Robot Integrator**, paired with a **Geometry Builder** (action0). It has no approve/revise decision
at all (see "What approval does" below) — it unconditionally writes a new complete design every iteration. The
rest of this section uses the template's own names.

### Token budget

Every model call gets a `remaining_budget` object (`orchestrator/controller.py`'s `context["budget"]`), with the
same fields for every role in both templates:

```
action_runs_used_this_iteration, action_runs_allowed_this_iteration, action_runs_remaining_this_iteration,
iteration_tokens_used, iteration_tokens_remaining, total_tokens_used, total_tokens_remaining,
iterations_remaining_after_this, your_previous_calls, teammate_calls_not_yet_run_this_iteration
```

plus, added per-call in `executors.py`: `this_call_input_tokens_estimate` and `output_limit_tokens_this_call`.
The fixed system message explains what these mean (identical text, every role, both teams):

> "You have a token allowance for this. remaining_budget shows the action runs this iteration has used, is
> allowed and has left (an action run is one call to one role, or the race itself), how many iterations follow
> this one, the tokens left in this iteration and in total, the size of this call's own prompt (already spent),
> output_limit_tokens_this_call (everything you generate in this call counts toward it, and an answer that
> reaches it is cut off and cannot be used) and your_previous_calls (what your last calls in this role spent,
> how many attempts they took, and how many were cut off by the limit); a careful rationale is worth spending
> it on."

### Scarcity (only one design races per iteration)

Not stated as a generic harness fact — stated inside each topology's own role notes, because the mechanic
itself differs by topology (see "What approval does"). The one scarcity statement common to every role, both
teams (`orchestrator/executors.py`'s `iteration_guidance`):

> "An iteration that ends without every required output is not scored; its development race is not run. Later
> iterations still run." — and, only on the last iteration: "This is the final iteration. If it ends without a
> delivered design, the final unseen-track race is scored 0, and you will not see that score. Watch
> remaining_budget."

### What approval does

**opt-eval's Evaluator is told, verbatim:** "A candidate races only when the Evaluator approves it, and the
approved build races unchanged. An iteration that ends with no approved build is not scored. Each review and
each revision uses one of the iteration's limited action runs, and the race itself needs one." And on the
decision itself: "Decision, every time you run: set decision in your Evaluator Feedback to approve or revise.
approve passes the candidate you reviewed on, unchanged, and it races (the orchestrator releases it; you do not
re-write it). revise sends it back to the Optimizer with your feedback... Saying in the feedback text that a
candidate is good enough is not a decision: only decision counts, and an iteration with no approval is not
scored."

**randow-maps has no analogous mechanic.** The Integrator's instructions never mention approving or gating
anything — it is told to "turn the supplied Geometry Proposal into a complete runnable robot by adding a
controller for that exact geometry" every iteration, unconditionally, and separately give "Integration
Feedback" (a distinct output, `entityR1`) back to the Builder. There is no scarcity of *races* in randow-maps
the way there is in opt-eval — every iteration produces exactly one complete design and races it, by
construction, not by a decision either role makes. Asking "what does approval do" in randow-maps has no answer
because there is no approval step.

### What happens to unspent tokens

**Never stated, in either template, for the normal case.** No instruction text anywhere says tokens carry
over, are forfeited, or otherwise addresses what happens to budget left unspent at the end of an iteration or
the race. The only place the word "unspent" appears anywhere in the harness is a failure-diagnosis string
(`orchestrator/controller.py`, inside `_close_incomplete`'s reason), used only when an iteration closes
*incomplete* specifically because the **per-iteration** token cap bound before the **total** cap did:

> "iteration token cap reached: {X} of {Y} tokens used this iteration ({Z} of {W} total tokens still unspent)"

This reaches an agent only indirectly, as `previous_iteration.reason` in the *next* iteration's prompt
(`controller.py`'s `_previous_incomplete`), and only after a failure — it is a clarification of which limit
caused that specific failure, not a general policy statement. For the common case (an iteration completes with
budget to spare), nothing is ever said about what becomes of what's left.

---

## 2. Log-mined behaviour: races 100-104, race-40 a/b/c

Usable iterations: races 100/101 have 0-1 iterations each (died almost immediately) and are excluded from the
rate tables below; 102/103/104 (opt-eval 28, randow-maps 30 iterations) and race-40 a/b/c (18 iterations each
team) are the basis for everything that follows. "Rounds" and decisions are counted from genuine action calls
only (`events.jsonl`), excluding carried-forward entity copies (versions named `carried-...`, tagged
`source_iteration` rather than a real `transaction` id in `version.json`) — an early version of this analysis
over-counted these as extra rounds; the numbers below are the corrected count.

### opt-eval: revise/approve rate and rounds per iteration

| race | iterations | revise decisions | approve decisions | mean rounds/iteration | iterations with NO race at all |
|---|---:|---:|---:|---:|---:|
| race-102 | 6 | 0 | 6 | 1.00 | 0 |
| race-103 | 12 | 0 | 12 | 1.00 | 0 |
| race-104 | 10 | 0 | 9 | 0.90 | 0 (1 iteration's data unreadable, consistent with the known read-timeout death) |
| race-40-a | 6 | 13 | 2 | 2.50 | **4 of 6** |
| race-40-b | 6 | 9 | 3 | 2.00 | **3 of 6** |
| race-40-c | 6 | 7 | 5 | 2.00 | 1 of 6 |

**This is a clean regime change, not noise.** In the three current-template races (102-104, 28 iterations), the
Evaluator revised **zero** times — every single candidate was approved on the first review. In the older
template (race-40, 18 iterations), it revised 29 times against 10 approvals, and in 8 of 18 iterations the
revise-and-re-review negotiation burned through the entire `max_action_runs: 6` budget *without ever reaching
an approval* — confirmed directly from those iterations' own `outcome.json`: `"reason": "action-run budget
exhausted: 6 of 6 runs used before completion"`, `"undelivered": ["entity1"]`. Those iterations scored zero
(no race ran at all) by the Evaluator's own instructed rule. Both regimes are real behaviour under the same
topology; something about the template/budget-field changes between race-40 and race-102+ (`CLAUDE.md`'s
"clarify per-call budget fields, cut-off feedback, raise iteration/token caps" commit sits in between
chronologically) flipped the Evaluator from revising too often (sometimes to the point of self-destruction) to
never revising at all.

**Why it never revises now, in its own words — and this looks like a factual error, not a judgment call.**
Nearly every approval in races 102-104 cites budget scarcity as the reason, e.g. (race-102, iteration 1 and 2):

> "Approved, because only one run remains this iteration. A revise decision would need a review and a
> revision, two runs, so it would leave the iteration unscored."

and (race-103, iteration 0, the very first review of the race):

> "The only remaining budget is one action run, so a revise round cannot be completed within this iteration."

**These statements do not match the actual budget.** `max_action_runs` is 6 in every one of these races'
own stored config (confirmed directly: `race-102-opt-eval/iteration-1/budget-ledger.json` shows
`"action_runs": 3, "maximum_action_runs": 6"` for an iteration that had *already completed* — i.e. a full
propose→review→race cycle costs 3 runs, not 6, and when the Evaluator is actually called it has only spent 1 of
6 (the Optimizer's call), leaving 5, not "one," for every non-final iteration quoted above (iterations 0-2 of
races 102/103, nowhere near the final iteration). The model's own instructions say "another review-and-revision
round costs two, the race one" — it appears to be pattern-matching that sentence into a reflexive "not enough
budget" conclusion rather than reading the live `action_runs_remaining_this_iteration` number it is actually
given, which this session did not expect going in and did not look for until the approve-rate pattern made it
worth checking. This is reported as an observation about model behaviour under this exact prompt, not a
simulator or scoring bug.

The feedback *text* in these always-approve iterations is often still substantive and forward-looking (e.g.,
race-103 iteration 5: "if completion_time is above 3 s with progress below 0.995... raise base_speed toward 1.8
to 2.0... if rms_error or max_error rises on tight bends, raise kp toward 3.0 to 3.5") — the Evaluator is not
failing to think about the design, it is failing to ever act on that thinking via the one lever (`decision`)
that matters, every single time, for a reason that does not hold up against its own supplied numbers.

A genuine revise, by contrast, when it does happen (race-40-a, iteration 0): "the integral gain ki has been
reduced from 0.5 to 0.2, which is expected to reduce overshoot and oscillations based on iteration 0 evidence.
The line_loss strategy has been changed from 'last_direction' to 'search_left' to test if this improves
recovery from line loss events."

### randow-maps: rounds, tokens, and whether the Integrator ever changes the geometry

| race | iterations | geometry changed by Integrator | geometry unchanged |
|---|---:|---:|---:|
| race-102 | 6 | 0 | 6 |
| race-103 | 12 | 0 | 10 (2 unreadable) |
| race-104 | 12 | 0 | 12 |
| race-40-a | 6 | 0 | 6 |
| race-40-b | 6 | 1 | 4 (1 unreadable) |
| race-40-c | 6 | 0 | 6 |

The Integrator changes the Builder's geometry in **1 of 48 readable iterations** across every race checked —
consistent with its own instructions ("adding a controller for that exact geometry"), not a surprise, but
confirms there is effectively no geometry-revision dynamic to analyse in this topology; its only real lever is
the controller. Sample Integration Feedback (`entityR1`, race-103 iteration 0, the Builder-facing output):

> "No race telemetry exists yet, so this feedback rests on the contract and the iteration 0 design... (1) H1
> depends on the 12 mm footprint giving a clean reading gradient across the 25 mm tape. Use the first race's
> line_loss_events and steering_oscillation to check this... (2) H2 depends on max_error staying below 0.06 m
> on tight bends. The controller will be tuned to keep max_error low, so if max_error still approaches 0.06 m,
> the limit is geometric and body_width or wheel_track need to change, not the gains."

### Tokens per iteration, per action (mean input/output tokens, current-template races)

| race | team | action0 in/out | action1 in/out |
|---|---|---:|---:|
| race-103 | opt-eval (Optimizer / Evaluator) | 23,868 / 2,609 | 27,357 / 1,700 |
| race-103 | randow-maps (Builder / Integrator) | 34,650 / 5,130 | 47,392 / 5,464 |

randow-maps spends roughly 1.5-2x the tokens per role that opt-eval does, despite opt-eval's topology having
the extra review step — most of randow-maps's extra output tokens are in the Integrator's dual job (complete
robot *and* Integration Feedback, written every iteration unconditionally, vs. opt-eval's Evaluator writing
feedback only on review).

---

## 3. Offline re-scoring: first draft vs. the design that actually raced (zero token cost)

Methodology check: re-scoring race-103's actual raced design (dev tracks, seeds 1-20, current `baseline_search`
config/tracks) reproduced its recorded score exactly (oval 83.96 / s-bend 70.94 / slalom 48.04, matching the
race's own `summary.json` to the reported decimal) — confirming the offline grid used below matches what each
race actually ran, for the three current-template races (102-104, adapter `v2`, same as today's code). Race-40
ran on adapter `v1`; re-scoring those designs under today's `v2` adapter is **not** a reproduction of race-40's
original scores — the physics changed since (noted in `PHASE0_FREEZE.md`'s commit history) — so race-40's
numbers below answer "how would this same first-vs-final pair compare under today's frozen rules," not "what
race-40 actually scored at the time."

### opt-eval: Optimizer's first draft vs. the design the Evaluator approved

| race | iterations with both designs | identical (no revise occurred) | among revised: improved | hurt | mean delta when revised |
|---|---:|---:|---:|---:|---:|
| race-102 | 6 | 6 | 0 | 0 | — |
| race-103 | 12 | 12 | 0 | 0 | — |
| race-104 | 9 | 9 | 0 | 0 | — |
| race-40-a | 2 | 1 | 1 | 0 | +81.0 |
| race-40-c | 5 | 2 | 2 | 1 | +194.9 |

Given §2's finding (zero revisions in 102-104), the first-vs-approved comparison is trivially "no change" in
every one of those 28 iterations — there is no second draft to compare against; "the Evaluator's intervention"
literally never alters the raced design in the current regime. Where a revision *did* happen (race-40, under
the old adapter), it helped more often than it hurt in this small sample (3 improved, 1 hurt, 1 tie across the
iterations with usable data) and the improvements were large when they happened (+81 to +195 points) — some
evidence that the review step, when actually exercised, was not merely theatre.

### randow-maps: Builder's draft (paired with this session's frozen reference controller, since a geometry
alone cannot be scored) vs. the Integrator's complete final design

| race | n | improved | hurt | mean delta |
|---|---:|---:|---:|---:|
| race-102 | 6 | 0 | 6 | −529.1 |
| race-103 | 10 | 0 | 10 | −472.7 |
| race-104 | 12 | 0 | 12 | −674.1 |
| race-40-a | 6 | 3 | 3 | +75.7 |
| race-40-b | 5 | 2 | 3 | −20.8 |
| race-40-c | 6 | 5 | 1 | +32.0 |

**Caveat this needs, stated plainly:** this is not "the Integrator hurt the design" — it is "the Builder's raw
geometry, paired with a neutral reference controller it was never designed against, scores far worse than the
same geometry paired with the Integrator's purpose-built controller." The large, consistent negative deltas in
102-104 mostly reflect that the reference controller (fixed gains, fixed `sensor_weights` shape) is a poor match
for whatever sensor count/spacing a given iteration's Builder proposed — this comparison measures the value of
*having a controller at all*, not the value of the Integrator's specific judgement, since geometry itself is
almost never touched (§2). Read this column as "a complete design beats an incomplete one," which is expected,
not as evidence about integration quality one way or the other.

---

## 4. Proposed minimal information changes (not implemented)

Charter constraints followed: say what to achieve, never how; identical information to both teams; smallest
change that lets a team judge its own token use, not a prescription for what to do about it.

1. **Give the Evaluator the number it needs, computed, instead of asking it to compute it.** §2's evidence is
   that the Evaluator's stated "only one run remains" claims do not match
   `action_runs_remaining_this_iteration`. Rather than restating that field more loudly (it is already there),
   add one derived, factual boolean next to it: whether a full review-and-revision-and-race round fits in the
   runs and tokens actually remaining this iteration (e.g. `another_revise_round_fits_in_budget: true/false`,
   computed by the harness from the same numbers it already tracks). This answers the exact question the
   Evaluator's own instructions pose ("another review-and-revision round costs two, the race one") without
   telling it whether to use that answer — purely arithmetic the harness can do more reliably than a model
   appears to be doing it today, and identical in both templates (any role reasoning about round-trip cost
   could use it).
2. **Say, once, what happens to tokens that are never spent.** Currently nothing does, for either team, in the
   normal case (§1). Adding one neutral factual sentence to the shared system prompt — e.g. "Tokens and action
   runs not used by the end of a race are not banked or carried to another race" (or whatever is actually true
   of the harness — this should be confirmed against the harness's real behaviour before wording it, not
   assumed) — removes a gap in what both teams are told, without telling either team what to conclude from it.
3. **Make the scarcity statement a budget fact, not a topology-specific aside.** Today, "only one design races
   per iteration" is implied by each topology's own notes (opt-eval's gate, randow-maps's unconditional
   once-per-iteration output) rather than stated as a general harness property. A one-line, team-neutral
   addition to the shared `iteration_guidance` block — "exactly one design races each iteration, the one
   written to the race's output entity by the time this iteration's actions finish" — would be true for both
   topologies as written today and would not need updating if a topology's internal mechanics changed, since
   it describes the harness's behaviour, not either team's process.

None of these were implemented or tested. All three are additions to information already computed or already
true today — none change what either team is told to *do*, and all three are identical text for both templates.
