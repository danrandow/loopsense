# Harness changes (next race after 18)

Aim: make each model agent clear about, and committed to, its role, and make the actor1 -> actor0 feedback loop (`entityR1`) actually run.
Scores are not comparable with earlier races. Both entrants get identical behaviour: the changes are in the generic executor and in both templates.
The previous templates are kept unchanged in `package-templates-archive/race-18-v1/`.

Why (race 18): randow-maps' Geometry Builder wrote only a no-op Working Agreement in iterations 1-5 and never wrote `entity0`; no run in either entrant ever wrote `entityR1`.
Causes found: the system prompt said outputs "may be omitted"; agents were never told who they were or what their outputs were for; instructions only asked for feedback "when race data is supplied" (never before the first race) and opt-eval's was "either critique or approve"; opt-eval did not carry `entityR1` forward; the Working Agreement carried a "proposal accepted" claim that read as the work being done.

| Change | Where |
|---|---|
| Each model action gets `your_role` (actor and action label/notes, label and purpose of each output it may write) and `required_outputs`. | `orchestrator/executors.py` (`role_brief`, `_openrouter`) |
| System message rewritten: shared team score, every `required_outputs` entity must be present, feedback outputs must be specific and evidence-based, no licence to omit. | `orchestrator/executors.py` |
| A missing required output is a validation error and is fed back to the model through the existing repair loop (`repair_attempts: 2`). | `orchestrator/executors.py` |
| `downstream_dependents` also says what each consumer does and what the output is for. | `orchestrator/executors.py` |
| New runtime field `required_outputs` (validated as a subset of topology-authorised writes). | `orchestrator/map_package.py` |
| Templates: `entity3` (Working Agreement / Shared Blackboard), `entityPrv0`, `entityPrv1` taken out of scope (topology, edges, contracts, `carry_forward`, `output_contracts`). To be reintroduced as a later experiment. | `package-templates/*` |
| Templates: action0 requires `entity0`; action1 requires `entity1` and `entityR1` every iteration (feedback allowed from the geometry/candidate alone, before any race). `entityR1` is carried forward in both (opt-eval previously dropped it). Instructions rewritten as role briefs with matching wording for both entrants. | `package-templates/*` |

Tests: `tests/test_map_driven.py`, `tests/test_incomplete_iteration.py` updated. In the cloud sandbox the canonical Randow Maps validator is unreachable, so tests were run with it stubbed (two unrelated failures remain: the stubbed title check, and a legacy `runner.py` the test expects to be deleted). Re-run with the real validator on your machine.

## In-iteration loop (opt-eval): the Evaluator decides when to race

Because `entityR1` is now always written, opt-eval's Optimizer and Evaluator would otherwise answer each other until the action-run budget was spent and the simulator never ran.
New workflow field `stop_reentry_when_present` (action -> entities): once those entities exist, an action that has already run is not re-entered. opt-eval uses `action0: [entity1]`, `action1: [entity1]`.
So the Evaluator controls the loop: feedback without an Approved Robot Build (`entity1`) sends the Optimizer round again; an approval ends the loop and the build races. The Evaluator must always write `entityR1`; `entity1` is its decision. It is told the run budget and that an iteration with no approved build is not scored.
randow-maps needs nothing: its action0 runs once per iteration and its action1 does not read `entityR1`.

Also fixed: the controller counted "runs" as distinct actions when resuming a half-finished iteration; it now counts every run.

## Feedback timing

- randow-maps: actor1 -> actor0 (`entityR1`) and actor2 -> actor0/actor1 (`entityR2A`/`entityR2B`) are read in the next iteration.
- opt-eval: `entityR1` can be read within the iteration (until the Evaluator approves); race data (`entityR2A`/`entityR2B`) is read in the next iteration.

## Reasoning goes in the entity (rationale), and the budget is usable

Agents had nowhere to think: output was JSON-only, capped at 2,000 tokens per call, and opt-eval's Optimizer had no rationale field at all (its instructions asked for one, but its contract forbade extra keys).
- Required `rationale` (string, first in the contract) on the design outputs: `entity0` and `entity1` in randow-maps, `entity0` in opt-eval. The system message tells agents to write it first, to think the diagnosis through in it, and to derive the `_presentation` label and notes from it (e.g. "Wider sensor array"). It is not part of the design that is raced (`project_design` drops it).
- The system message tells agents they have a token allowance (`remaining_budget`) and that a careful rationale is worth spending it on.
- `max_output_tokens` raised from 2000 to 4000 in both templates, so one thorough call is possible.
- Fairness: both entrants get the same budgets, model, temperature, output limit and evidence; the structural difference under test is opt-eval's in-iteration revision loop vs randow-maps' between-iteration feedback. Compare tokens used, agent runs and score per token alongside the score.

## Map notes carry the full reasoning

The Markdown note on each output entity now ends with the agent's `rationale` (design outputs) or its `feedback` and `requested_changes` (`entityR1`), appended verbatim by the harness (`full_notes`). The agent writes only a short summary as its note and is told not to repeat the reasoning, so it costs no extra tokens. A person can browse a map and read what each actor concluded and asked for.
