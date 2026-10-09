# LoopSense Robot Race Experiment Design

Status: map-driven harness implemented and used for pilot races; recorded run not yet ready

Date: 2026-10-09 (refreshed; first written 2026-10-03)

Owner: Dan Randow

Experiment: LoopSense producer–integrator pair versus conventional optimizer–evaluator pair

In the harness the LoopSense condition is the `randow-maps` entrant and the control is the `opt-eval` entrant. Where this document says "LoopSense" or "control", those are the packages meant.

## Purpose

Build a small, inspectable experiment that tests whether the LoopSense production topology helps a two-agent team adapt faster or better than a conventional optimizer/evaluator topology.

Both teams repeatedly design a line-following robot, test it in RobotTraceSim, receive objective measurements, and learn across iterations. The agents work between trials. They do not control the robot in real time.

The scope of the first experiment is deliberately small. Each team's starting state is its topology, role instructions and design constraints. A shared Working Agreement, a shared blackboard and private role expertise were part of the original design but are **deferred to a later experiment**; the current templates omit them so that the only structural difference under test is the topology itself.

The experiment must remain useful whether its result is positive, negative, or ambiguous. It therefore preserves a public, auditable record of what each actor received and produced, what happened on the track, which evidence and feedback each actor used, how its coordination changed, and how performance and cost changed over time.

## Research question

> Under the same model, total token budget, simulator, starting state, and evaluation conditions, does a serial producer–integrator topology exhibit a different adaptation trajectory from a conventional optimizer–evaluator pair?

The initial claim is deliberately narrow. This experiment does not test topology evolution, compare every major agent architecture, or establish that LoopSense solves arbitrary knowledge work. It tests whether one explicit LoopSense production and feedback topology changes learning relative to a strong, familiar baseline.

## Design principles

Decided by Dan, 2026-10-09. These govern the harness and the maps it runs.

- The map is the single source of truth for team topology. The orchestrator knows nothing about who does what until it reads the map.
- The map is part of the treatment. Both arms use it identically; only the topology differs.
- The harness must serve both topologies. The optimizer–evaluator multi-loop inner cycle is a per-map override in its configuration, and a possible step toward kanban-style continuous interaction.
- The harness is intended to be reusable beyond this experiment.
- Randow Maps serve as the spectator view and as the agents' work surface.

## Experimental conditions

### LoopSense condition

The LoopSense team has two AI roles joined by a single forward production spine:

```text
Geometry Builder
  → Geometry Proposal
  → Robot Integrator
  → Complete Robot Package
  → Race Simulator
  → Race Outcome
```

Its return flows are:

```text
Race Simulator → Geometry Race Data    → Geometry Builder
Race Simulator → Integration Race Data → Robot Integrator
Robot Integrator → Integration Feedback → Geometry Builder
```

The Geometry Builder produces a component. The Robot Integrator is its direct customer: it incorporates that geometry, adds a controller, and produces the self-contained robot package consumed by the simulator. The Integrator writes Integration Feedback for the Builder every iteration, including before the first race, from the geometry alone. Each role also receives its own addressed race-data entity. The two-agent boundary and single forward spine are fixed for this experiment.

### Evaluator–optimizer control

The conventional control also has two AI roles:

```text
Robot Optimizer
  → Robot Candidate
  → Evaluator
  → Approved Robot Build
  → Race Simulator
  → Race Outcome
```

Its return flows are:

```text
Evaluator → Evaluator Feedback → Robot Optimizer
Race Simulator → Optimizer Race Data → Robot Optimizer
Race Simulator → Evaluator Race Data → Evaluator
```

The Optimizer proposes a complete geometry-and-controller candidate. The Evaluator inspects the candidate and its rationale and always writes feedback; it also decides when to stop. Feedback without an Approved Robot Build sends the Optimizer round again; an approval ends the loop and the approved build races. The loop is bounded by the shared token and action-run budgets. Any feedback given with the approval is read by the Optimizer in the next iteration. This inner loop is a per-map workflow override, not harness logic.

Candidate, feedback and approved build are separate, contract-validated entities. There is no shared blackboard in the current experiment.

## Independent variable

The independent variable is the organisation of work between world-feedback cycles:

- **LoopSense:** a serial producer–customer relationship with explicit component and integrated-product entities, direct integration feedback, and separately addressed environmental return paths.
- **Control:** a conventional evaluator–optimizer relationship that iterates over complete solutions through critique and revision.

The experiment is not a comparison of different models, simulators, evidence, scoring systems, or total budgets. The map itself is part of the treatment: both teams are run by the same generic controller from their own map, so only the topology differs.

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
10. The same schema validation and bounded repair policy apply. A model that returns invalid or incomplete output is sent the validation errors and may retry up to the configured number of repair attempts.
11. Every model action is given, in the same format, its role, the objective (maximise the score, judged once after the last iteration on an unseen track of a different shape), its position in the race, its remaining budget, and the outputs it must write. Required outputs are derived from the team's own map and runtime files.
12. Neither condition can see held-out tracks in prompts or development returns.
13. There is no separate retrospective agent, call, or budget.
14. The same deterministic local orchestrator handles model calls, validation, simulation, budgets, state, artifacts, and rendering.
15. Every completed iteration is cloned into the next iteration's starting scenario.

Both teams also use the map identically: access, routing and eligibility are derived from each team's topology by the same controller, which never branches on team name. Fairness is based on equal total budget and equivalent evidence, not an identical number of calls. The control may spend more calls on internal critique and revision; the LoopSense team spends its budget through its prescribed production flow. Results therefore report improvement by race and by token or cost.

## Iteration procedure

The controller does not hard-code either team's sequence. Each iteration starts by cloning the previous iteration's carried-forward state (return entities and the scenario). The controller then runs any action whose required inputs are available, once per set of input versions unless the workflow permits re-entry, until the iteration's completion entities exist or a limit is reached. The sequences below are what that produces, not instructions to the controller.

### LoopSense iteration

1. The Geometry Builder writes a Geometry Proposal from the previous Geometry Race Data and Integration Feedback and the design constraints.
2. The Robot Integrator, now eligible, writes a self-contained Complete Robot Package and Integration Feedback.
3. The Race Simulator runs the package on the configured development track and seeds, and writes the Race Outcome and the two addressed race-data entities.
4. The new race-data entities and Integration Feedback are read when the next iteration begins.

### Control iteration

1. The Optimizer writes a Robot Candidate from its Evaluator Feedback and Optimizer Race Data and the design constraints.
2. The Evaluator inspects the candidate and writes feedback, and, if it approves, an Approved Robot Build.
3. Without an approval the Optimizer runs again on the new feedback; this repeats while budget remains. With an approval the loop ends.
4. The Race Simulator runs the approved build and writes the Race Outcome and the two addressed race-data entities, which are read in the next iteration.

### Iterations that cannot finish

An iteration that cannot finish (no action can run, or the token or action-run budget is spent) does not abort the race. It records `outcome.json` with the reason, the undelivered entities and the blocked actions, is not raced or scored, and seeds the next iteration, whose agents are told what went wrong. If the final iteration delivers no design, that entrant's held-out score is 0.0 and the race still completes.

## Robot and evidence boundaries

Agent output is constrained data, never executable code. Geometry and controller artifacts use canonical JSON schemas. A complete package contains its geometry rather than referencing a hidden dependency. The initial controller space is bounded to parameters such as base speed, PID gains, sensor weighting, line-loss response, bounded scheduling, and optionally a small finite-state policy.

Design outputs also carry a required `rationale`, written first, in which the agent reasons about its diagnosis; it is published in the map notes and is not part of the raced design. The controller receives only permitted sensor observations and timestep. It cannot see privileged global pose, hidden tracks, arbitrary files, the network, or a shell. The simulator adapter validates geometry, applies explicit seeds and timeouts, records controller errors, and returns stable result objects with explicit termination reasons.

## Tracks and evaluation

The track suite has three parts:

- an **anchor track**, fixed and visible every iteration for easy human comparison (defined under `tracks/anchor` but not used by the current templates);
- a **development set**, used during iterative learning and represented in returned evidence; and
- a **held-out set**, excluded from prompts and development returns and used only for the final evaluation after the last iteration.

The race configuration names the development and held-out tracks, seeds and noise; the current templates use one track of each, of different shapes.

Both conditions use identical track definitions, seeds, noise settings, and order. Conditions run sequentially or in a preregistered deterministic interleave; world conditions never change in response to current scores.

The primary score prioritises, in order: valid design, completion, progress when incomplete, robustness, and then speed and precision among reliable finishers. Robustness and precision are multiplied by progress, so a robot that does not move scores zero. A run also ends as `stalled` when progress rises by less than a set amount over a set number of steps. The weights live in each package's `race.yaml`, and the agents are shown the scoring formula generated from them. The formula must be frozen before the recorded run, and all raw components remain public.

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
- control critique–revision cycles and action runs; and
- requested measurements and evidence of their later use.

The core comparison is the shape and efficiency of each adaptation trajectory, not merely the final winner.

## Auditability and context isolation

Prompts are assembled from each action's topology-authorised neighbourhood: it reads only entities connected to it by `used by` edges and writes only entities it generates, and an undeclared read or write is rejected. Held-out tracks and the aggregate Race Outcome are never supplied. The race manifest records definition hashes, controller and simulator versions and common settings, and the per-iteration events record what each action received and produced. This must demonstrate that evidence and topology-specific context were handled as designed.

Every state transition appends to an immutable per-iteration `events.jsonl` containing the action, input versions, artifact hashes, token use, validation result, and any failure or repair reason. Atomic checkpoints permit a stopped run to resume without duplicating completed calls or trials.

Each race also produces a shared leaderboard and report, per-entrant scenario maps, entity versions, telemetry, and SVG trajectories and track views. Race Outcome links directly to a human-viewable iteration summary. Randow Maps is the public spectator interface; no public simulation service is required.

## Failure policy

- An invalid or incomplete model output receives validation errors and up to the configured number of repair attempts (two in the current templates); after that the action fails.
- A missing required output is a validation error and goes through the same repair loop.
- Budget exhaustion or a stalled workflow closes the iteration as incomplete (see above). It grants no discretionary extra calls.
- A model call that exceeds the configured token budget stops the run, because it is detected before the transaction commits. The race is recorded as `failed` with the error, cannot be resumed or edited, and must be retired and re-prepared under a fresh race id.
- A harness defect stops the race. The defect is fixed and versioned (`controller_version`), and a new race begins; scores are not comparable across harness versions.
- A machine interruption resumes from the last atomic checkpoint.
- A pre-run check blocks configurations that cannot work, such as OpenRouter with no key, and warns on a model id that looks like the offline mock.

## Current status and recorded-run gate

The map-driven harness runs complete pilot races with either the deterministic mock provider or a real model through OpenRouter, using the pinned RobotTraceSim native sensor and drivetrain functions behind the headless adapter. Prepare, review, freeze and run are enforced; a frozen race is verified against its definition hashes before it runs. Current races are pilots: they validate the harness and are not the preregistered experiment, and scores are not comparable across harness versions.

Before a recorded run:

1. verify the simulator adapter against the pinned MIT-licensed RobotTraceSim source and rebuild the native library with identical deterministic results;
2. validate the chosen model and frozen settings through the provider adapter;
3. freeze the model settings, role instructions and contracts (by definition hash), total and per-iteration budgets, score weights, geometry bounds, tracks, seeds, run length, repair policy and ordering;
4. complete disposable pilot races, including at least one in which both teams deliver designs on every iteration;
5. start the recorded race from fresh race-owned packages; and
6. tag the exact experiment configuration.

The first recorded run is expected to use five or six iterations per team and one final held-out evaluation (the templates currently default to six), unless a different run length or non-score-based extension rule is preregistered before comparative results are inspected.

## Reporting rules

Carried over from the retired race-4 preregistration.

- Report all raw metrics and the composite score. State development and held-out results separately.
- Do not declare a topology superior on one final composite score. The comparison must cover adaptation trajectory (current score, best-so-far, improvement per iteration, improvement per 10,000 tokens), worst case, invalid artifacts, repair calls and token use.
- Equal or conflicting results are reported as ambiguous.
- Do not interpret pilot, dry-run or smoke scores as evidence.
- A run's length and stopping rule are fixed before results are inspected; any later run needs its own preregistration.

## Interpretation

A positive result would show that this explicit producer–integrator topology learns faster or better under the controlled conditions. A negative result would show that the conventional evaluator–optimizer loop is as effective or better for this task. An ambiguous result would still expose where costs, failures, feedback use, or coordination differed.

Any result applies first to this bounded experiment. Generalisation to other tasks, larger teams, changing environments, topology evolution, or reduced human oversight requires later experiments.

## Source of truth

This design summarises the decisions governing the comparison. The map-driven architecture is specified in [MAP_DRIVEN_ARCHITECTURE_SPEC.md](MAP_DRIVEN_ARCHITECTURE_SPEC.md) (canonical), the work to finish it is in [COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md](COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md), and operation is in the [README](README.md). Harness revisions are recorded in the `RACE_*_CHANGES.md` files. If these documents differ, the spec is authoritative on architecture until this design is updated.
