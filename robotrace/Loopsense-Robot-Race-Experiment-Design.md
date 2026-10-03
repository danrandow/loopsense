# LoopSense Robot Race Experiment Design

Status: aligned with the implementation plan; pilot harness implemented, recorded run not yet ready

Date: 2026-10-03

Owner: Dan Randow

Experiment: LoopSense producer–integrator pair versus conventional optimizer–evaluator pair

## Purpose

Build a small, inspectable experiment that tests whether the LoopSense production topology helps a two-agent team adapt faster or better than a conventional optimizer/evaluator topology.

Both teams repeatedly design a line-following robot, test it in RobotTraceSim, receive objective measurements, and learn across iterations. The agents work between trials. They do not control the robot in real time.

The experiment must remain useful whether its result is positive, negative, or ambiguous. It therefore preserves a public, auditable record of what each actor received and produced, what happened on the track, which evidence and feedback each actor used, how its coordination changed, and how performance and cost changed over time.

## Research question

> Under the same model, total token budget, simulator, starting state, and evaluation conditions, does a serial producer–integrator topology exhibit a different adaptation trajectory from a conventional optimizer–evaluator pair?

The initial claim is deliberately narrow. This experiment does not test topology evolution, compare every major agent architecture, or establish that LoopSense solves arbitrary knowledge work. It tests whether one explicit LoopSense production and feedback topology changes learning relative to a strong, familiar baseline.

## Experimental conditions

### LoopSense condition

The LoopSense team has two AI roles joined by a single forward production spine:

```text
Geometry Builder
  → Geometry Proposal
  → Robot Integrator
  → Complete Robot Package
  → Robot on Track
  → Race Outcome
```

Its return flows are:

```text
Robot on Track → Race Data for Geometry    → Geometry Builder
Robot on Track → Race Data for Integration → Robot Integrator
Robot Integrator → Integration Feedback     → Geometry Builder
```

The Geometry Builder produces a component. The Robot Integrator is its direct customer: it incorporates that geometry, adds a controller, and produces the self-contained robot package consumed by the simulator. The Integrator sends post-race integration feedback upstream. Each role also receives its own addressed race-data entity.

The team begins with a shared Working Agreement pointing it toward these explicit products and return records. Either agent may update the agreement during its ordinary turn. The agents can improve their methods and coordination, but the two-agent boundary and single forward spine remain fixed for this initial experiment.

### Evaluator–optimizer control

The conventional control also has two AI roles:

```text
Robot Optimizer
  → Complete Robot Candidate
  → Evaluator
  → Approved Robot Build
  → Robot on Track
  → Race Outcome
```

Its return flows are:

```text
Evaluator → Evaluator Feedback → Robot Optimizer
Robot on Track → Race Data for Optimizer → Robot Optimizer
Robot on Track → Race Data for Evaluator → Evaluator
```

The Optimizer proposes a complete geometry-and-controller candidate. The Evaluator sees the real candidate and rationale and either requests another revision or selects a recorded candidate to ship unchanged. The pair may alternate through multiple candidate and feedback versions before racing, provided it stays within the shared budget.

Both agents can read and write an unstructured shared blackboard. The blackboard is storage, not an actor, and its files are not permission boundaries. The control receives minimal initial criteria but no LoopSense topology advice.

## Independent variable

The independent variable is the organisation of work between world-feedback cycles:

- **LoopSense:** a serial producer–customer relationship with explicit component and integrated-product entities, direct integration feedback, and separately addressed environmental return paths.
- **Control:** a conventional evaluator–optimizer relationship that iterates over complete solutions through critique and revision in a shared blackboard.

The experiment is not a comparison of different models, simulators, evidence, scoring systems, or total budgets.

## Common controls

The following are held common across both conditions:

1. Two AI agents participate in each condition.
2. Both conditions use the same exact model and model settings.
3. Both receive the same total token budget and expose actual use and remaining budget after every call.
4. Both start from equivalent initial robot state and fixed experiment constraints.
5. Both use the same simulator version, tracks, seeds, noise, trial order, termination rules, metrics, and score.
6. Exactly one selected robot package per condition enters one canonical race batch per iteration.
7. The simulator creates one canonical measurement capture and two independently addressed race-return entities per condition and iteration.
8. Initially, both addressed returns contain the same standard measurements; each recipient independently decides what to use.
9. Race Outcome is preserved for topology, audit, and human inspection but is not an operational input to an AI agent.
10. The same schema validation and one bounded, non-substantive format-repair policy apply.
11. Private expertise remains actor-specific in both conditions.
12. Neither condition can see held-out tracks in prompts or development returns.
13. There is no separate retrospective agent, call, or budget.
14. The same deterministic local orchestrator handles model calls, validation, simulation, budgets, state, artifacts, and rendering.
15. Every completed iteration is cloned into the next iteration's starting scenario.

Fairness is based on equal total budget and equivalent evidence, not an identical number of calls. The control may spend more calls on internal critique and revision; the LoopSense team spends its budget through its prescribed production flow. Results therefore report improvement by race and by token or cost.

## Iteration procedure

### LoopSense iteration

1. Clone the previous completed scenario and update the shared budget ledger.
2. Give the Geometry Builder its private expertise, Working Agreement, previous addressed race data, previous Integration Feedback, and permitted constraints.
3. Generate and mechanically validate a Geometry Proposal, allowing one format-repair call if needed.
4. Give the Robot Integrator that proposal, its private expertise, Working Agreement, previous addressed race data, and permitted constraints.
5. Generate and validate a self-contained Complete Robot Package, again allowing only the common bounded repair policy.
6. Run the configured development tracks and seeds.
7. Write the Race Outcome, the two addressed race returns, trial telemetry, trajectory SVGs, summary SVG, and aggregate result.
8. Give the Integrator its addressed race return and generate Integration Feedback for the Builder.
9. Close the iteration. The new return entities become inputs only when the next scenario is cloned.

### Control iteration

1. Clone the previous completed scenario and update the shared blackboard budget ledger.
2. Have the Optimizer read its allowed context and generate a complete candidate.
3. Mechanically validate the candidate under the common repair policy.
4. Have the Evaluator inspect the actual candidate, rationale, blackboard, private expertise, constraints, and remaining budget.
5. The Evaluator either writes feedback for another cycle or selects a recorded candidate unchanged as the Approved Robot Build.
6. Repeat candidate and feedback cycles while the Evaluator requests revision and budget remains. If budget policy forces selection, use the latest valid candidate under the preregistered rule.
7. Run that selected build through the same configured development tracks and seeds.
8. Write the Race Outcome, two addressed race returns, telemetry, SVGs, and aggregate result, then close the iteration.

## Robot and evidence boundaries

Agent output is constrained data, never executable code. Geometry and controller artifacts use canonical JSON schemas. A complete package contains its geometry rather than referencing a hidden dependency. The initial controller space is bounded to parameters such as base speed, PID gains, sensor weighting, line-loss response, bounded scheduling, and optionally a small finite-state policy.

The controller receives only permitted sensor observations and timestep. It cannot see privileged global pose, hidden tracks, arbitrary files, the network, or a shell. The simulator adapter validates geometry, applies explicit seeds and timeouts, records controller errors, and returns stable result objects with explicit termination reasons.

## Tracks and evaluation

The track suite has three parts:

- an **anchor track**, fixed and visible every iteration for easy human comparison;
- a **development set**, used during iterative learning and represented in returned evidence; and
- a **held-out set**, excluded from prompts and development returns and used only at preregistered checkpoints and final evaluation.

Both conditions use identical track definitions, seeds, noise settings, and order. Conditions run sequentially or in a preregistered deterministic interleave; world conditions never change in response to current scores.

The primary score prioritises, in order: valid design, completion, progress when incomplete, robustness, and then speed and precision among reliable finishers. Its exact formula must be frozen before the recorded run, and all raw components remain public.

Recorded outcome measures include:

- completion and normalised progress;
- completion time;
- RMS and maximum centre-line error;
- loss-of-line events;
- steering oscillation and control effort;
- controller errors;
- performance under sensor noise and motor variation; and
- the development-to-held-out performance gap.

Learning-system measures include:

- improvement by iteration;
- current, best-so-far, and worst-case scores;
- tokens, estimated cost, and improvement per 10,000 tokens;
- invalid artifacts and repair calls;
- Working Agreement revisions and control critique–revision cycles; and
- requested measurements and evidence of their later use.

The core comparison is the shape and efficiency of each adaptation trajectory, not merely the final winner.

## Auditability and context isolation

Prompts are assembled from an allowlist for each role and state. A manifest records every input supplied to every model call. This must demonstrate that evidence, private expertise, held-out tracks, and topology-specific context were handled as designed.

Every state transition appends to an immutable JSONL audit log containing the condition, iteration, state, artifact hashes, model request identifier, token use, validation result, simulator version, and any failure or retry reason. Atomic checkpoints permit a stopped run to resume without duplicating completed calls or trials.

Each run also produces a shared leaderboard, per-condition scenario maps, entity and feedback records, telemetry, and SVG trajectories. Race Outcome links directly to a human-viewable iteration summary. Randow Maps is the public spectator interface; no public simulation service is required.

## Failure policy

- An invalid model artifact receives one repair call containing validation errors only; a second failure receives the preregistered invalid-result consequence.
- A transient model API failure receives bounded, recorded retries without prompt changes.
- A simulator crash is retried once with the identical package and seed; a repeated failure stops the experiment.
- Budget exhaustion stops the condition at its declared boundary and grants no discretionary extra calls.
- A harness defect stops both conditions. The defect is fixed and versioned, state is reset, and a new run begins.
- A machine interruption resumes from the last atomic checkpoint.

## Current status and recorded-run gate

The checked-in system can run with either its deterministic mock provider or a real model through OpenRouter. RobotTraceSim is pinned with its upstream provenance and license, but races still use the safe headless contract simulator while the upstream desktop physics loop is extracted behind that contract. Current runs are therefore pilots: they validate the harness but do not constitute the preregistered RobotTraceSim experiment.

Before a recorded run:

1. finish and verify the adapter from the pinned MIT-licensed RobotTraceSim source to the headless simulation contract;
2. validate the chosen model and frozen settings through the implemented provider adapter;
3. freeze the model settings, prompt hashes, total and per-iteration budgets, score weights, geometry bounds, tracks, seeds, run length, retry rules, and ordering;
4. complete disposable pilot iterations per condition;
5. reset private state, artifacts, and starting designs; and
6. tag the exact experiment configuration.

The first recorded run is expected to use five iterations per condition and one final held-out evaluation, unless a different run length or non-score-based extension rule is preregistered before comparative results are inspected.

## Interpretation

A positive result would show that this explicit producer–integrator topology learns faster or better under the controlled conditions. A negative result would show that the conventional evaluator–optimizer loop is as effective or better for this task. An ambiguous result would still expose where costs, failures, feedback use, or coordination differed.

Any result applies first to this bounded experiment. Generalisation to other tasks, larger teams, changing environments, topology evolution, or reduced human oversight requires later experiments.

## Source of truth

This design summarises the decisions governing the comparison. The detailed technical contracts, repository layout, implementation phases, tests, and remaining pre-registration choices are maintained in the [Implementation Plan](IMPLEMENTATION_PLAN.md). If these documents differ, the Implementation Plan is authoritative until the design is updated.
