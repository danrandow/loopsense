# LoopSense Robot Race Experiment — Implementation Plan

Status: implementation-ready draft  
Date: 2026-10-03  
Owner: Dan Randow  
Experiment: LoopSense pair versus conventional optimizer/evaluator pair

## 1. Purpose

Build a small, inspectable experiment that tests whether the LoopSense production
topology helps a two-agent team adapt faster or better than a conventional
optimizer/evaluator topology.

Both teams repeatedly design a line-following robot, test it in RobotTraceSim,
receive objective measurements, and learn across iterations. The agents work
between trials. They do not control the robot in real time.

The experiment should be useful regardless of outcome. A positive, negative, or
ambiguous result must leave a public, auditable record of:

- what each actor received;
- what each actor produced;
- what happened on the track;
- which evidence and feedback each actor used;
- how the working agreement changed;
- how performance and cost changed over time.

The initial claim is deliberately narrow:

> Under the same model, total token budget, simulator, starting state, and
> evaluation conditions, does a serial producer–integrator topology exhibit a
> different adaptation trajectory from a conventional optimizer–evaluator pair?

This experiment does not claim to prove that LoopSense solves arbitrary knowledge
work or that one short run generalizes to other tasks.

## 2. Fixed decisions

The following decisions are already made:

1. RobotTraceSim supplies the environment and objective evidence.
2. The simulator runs headlessly between agent turns.
3. Actor 2 is deterministic software, not an AI agent.
4. Two AI agents participate in each condition.
5. The LoopSense condition begins with Geometry Builder and Robot Integrator roles.
6. The roles may evolve their working agreement, but the two-agent boundary and
   single forward spine remain fixed during the initial experiment.
7. A retrospective occurs after an iteration ends. Its changes apply only to the
   next iteration.
8. One race batch produces one canonical measurement capture and two independently
   addressed return-flow entities.
9. Initially the two return entities contain the same standard measurements. Each
   recipient independently decides what to use.
10. Race Outcome, entity2, is not readable by either AI agent. Their evidence enters
    through return-flow entities.
11. The conventional condition is a two-agent optimizer/evaluator pair using a
    passive blackboard.
12. Orchestration is a narrow deterministic local program, not an autonomous agent.
13. Start with the cheapest model capable of reliably producing valid artifacts.
14. The same model and model settings apply to both conditions.
15. Trials run locally. Generated maps, JSON, Markdown, SVG, and leaderboard
    artifacts synchronize to the existing Randow Maps repository and public app.
16. There is no public simulation service or interactive simulator in version one.

## 3. Topologies

### 3.1 LoopSense condition

Canonical map: `experiments/robotrace/base.yaml`

Forward spine:

```text
Geometry Builder
  → Geometry Proposal
  → Robot Integrator
  → Complete Robot Package
  → Robot on Track
  → Race Outcome
```

Return flows:

```text
Robot on Track → Race Data for Geometry    → Geometry Builder
Robot on Track → Race Data for Integration → Robot Integrator
Robot Integrator → Integration Feedback     → Geometry Builder
```

The Geometry Builder produces a component. The Robot Integrator is its direct
customer and builds the complete product by incorporating that geometry and adding
a controller. The robot consumes only the complete package.

### 3.2 Conventional control condition

Canonical map: `experiments/robotrace/control-base.yaml`

Forward spine:

```text
Robot Optimizer
  → Candidate Robot
  → Evaluator
  → Test Submission
  → Robot on Track
  → Race Outcome
```

Return flows:

```text
Evaluator → Evaluator Feedback → Robot Optimizer
Robot on Track → Race Data for Optimizer → Robot Optimizer
Robot on Track → Race Data for Evaluator → Evaluator
```

The optimizer owns both geometry and controller. The evaluator never edits them.
It critiques complete candidates, decides when a valid candidate is ready to test,
and recommends changes after the race.

The shared blackboard is storage, not an actor. The orchestrator explicitly selects
which records enter each prompt.

### 3.3 Bounded pre-test control loop

The evaluator may return a candidate for revision before it reaches the track. To
avoid unlimited deliberation:

- default maximum: two evaluator reviews per iteration;
- the evaluator may approve the first proposal;
- the optimizer may revise after the first critique;
- after the second review, the latest valid candidate is tested;
- invalid candidates enter the mechanical repair policy rather than consuming an
  unbounded critique loop;
- the total token budget, rather than equal call count, determines cost fairness.

The review cap is configuration, fixed before the recorded run. It is not editable
through the agents' working agreement.

## 4. Iteration lifecycles

### 4.1 LoopSense iteration

1. The orchestrator opens iteration `N` and loads its immutable configuration.
2. Agent 0 receives:
   - its private expertise state;
   - current working agreement;
   - `Race Data for Geometry` from iteration `N-1`;
   - `Integration Feedback` from iteration `N-1`;
   - permitted experiment constraints.
3. Agent 0 generates Entity 0: Geometry Proposal.
4. Mechanical validation checks Entity 0. One bounded repair call is allowed for
   schema or constraint errors.
5. Agent 1 receives:
   - Entity 0;
   - its private expertise state;
   - current working agreement;
   - `Race Data for Integration` from iteration `N-1`;
   - permitted experiment constraints.
6. Agent 1 generates Entity 1: Complete Robot Package.
7. Mechanical validation checks Entity 1. One bounded repair call is allowed.
8. The evaluator runs the configured development-track and seed batch.
9. The evaluator writes:
   - Entity 2: Race Outcome;
   - Race Data for Geometry;
   - Race Data for Integration;
   - per-trial telemetry and SVGs;
   - aggregate result JSON.
10. Agent 1 receives its addressed race return and generates post-race Integration
    Feedback for Agent 0.
11. The iteration closes. Agent 0 does not act again inside it.
12. Both agents independently write retrospective observations.
13. A deterministic retro step asks them to agree any working-agreement revision.
14. The revision is versioned and applies from iteration `N+1`.

### 4.2 Control iteration

1. The optimizer receives its private state, working agreement, direct prior race
   data, prior evaluator feedback, and fixed constraints.
2. It generates a complete Candidate Robot.
3. The evaluator reviews the candidate and either approves it or returns critique.
4. Proposal and critique may repeat within the configured review cap.
5. The evaluator produces an unchanged Test Submission identifying the exact
   candidate version selected.
6. The same simulator batch used by the LoopSense condition runs.
7. The harness generates the outcome and independently addressed race returns for
   both agents.
8. The evaluator consumes its race return and produces post-race feedback.
9. The iteration closes.
10. Both agents retrospect; any working-agreement revision applies next iteration.

## 5. Repository layout

Proposed layout inside the LoopSense repository:

```text
experiments/robotrace/
  IMPLEMENTATION_PLAN.md
  base.yaml
  control-base.yaml
  README.md
  config/
    experiment.yaml
    design-space.schema.json
    controller.schema.json
    observation-request.schema.json
    result.schema.json
  simulator/
    upstream/                 # pinned RobotTraceSim source or documented submodule
    native/                   # portable build wrapper
    adapter/                  # headless interface and scoring
  orchestrator/
    runner.py
    state_machine.py
    model_client.py
    prompts/
    validators/
  tracks/
    development/
    held-out/
    anchor/
  conditions/
    loopsense/
      working-agreement-v0.md
      private/
    control/
      working-agreement-v0.md
      private/
  runs/
    <experiment-id>/
      manifest.json
      leaderboard.json
      leaderboard.md
      leaderboard.svg
      loopsense/
        iteration-0/
        iteration-1/
      control/
        iteration-0/
        iteration-1/
```

Generated run artifacts should not overwrite canonical maps or configuration.
Whether full telemetry is committed or stored separately should be decided after
measuring file size during the smoke test. Summaries, maps, and representative SVGs
should always be committed.

## 6. Artifact contracts

### 6.1 Geometry Proposal

```text
entity0/
  geometry.json
  intent.md
  feedback-request.json
  manifest.json
```

`geometry.json` uses one canonical schema. It must not contain duplicated fields
whose values can disagree. The adapter translates it into RobotTraceSim's current
robot JSON.

`feedback-request.json` contains machine-readable requested measurements selected
from a supported catalogue. Free-text questions may accompany requests but cannot
cause arbitrary code execution.

### 6.2 Complete Robot Package

```text
entity1/
  geometry.json
  controller.json
  integration-notes.md
  observation-request.json
  manifest.json
```

The geometry is copied into Entity 1, not referenced through a hidden dependency.
Actor 2 therefore consumes one self-contained package.

The initial controller representation should be constrained JSON describing a PID
or small state machine. Arbitrary Python generation is deferred. This prevents
filesystem access, hidden track inspection, network calls, and accidental process
damage while keeping controller design meaningful.

### 6.3 Race Outcome

```text
entity2/
  result.json
  summary.md
  iteration-summary.svg
  trials/
    <trial-id>/
      result.json
      trajectory.svg
      telemetry.json          # may be excluded from Git if large
```

Entity 2 is retained for topology, audit, and human inspection. It is not supplied
to either AI agent.

### 6.4 Addressed race returns

Each return contains:

```text
return/
  measurements.json
  measurement-catalogue-version
  source-run-id
  source-trial-ids
  request-coverage.json
```

Initially the measurement payloads for both recipients are identical. They are
separate immutable entities so later changes in requested data are observable.

The robot does not interpret the measurements. The harness mechanically calculates
and packages them.

### 6.5 Working agreement

The canonical topology and entity definitions do not live in the working agreement.
The agreement may cover:

- responsibilities within the fixed topology;
- readiness and handoff expectations;
- design-rationale conventions;
- feedback style;
- measurement requests;
- diagnostic practices;
- how disagreements are recorded;
- what each agent promises to preserve from upstream work.

Every revision records a diff and the retrospective evidence motivating it.

## 7. RobotTraceSim adaptation

Create a pinned fork or vendored copy of the MIT-licensed repository and record its
upstream commit.

Required changes:

1. Compile `linesim.c` for the current platform rather than loading a Windows DLL
   unconditionally.
2. Extract or wrap the simulation worker behind a headless function.
3. Give every trial an explicit private random generator and seed.
4. Return a termination reason: `finished`, `off_track`, `timeout`,
   `controller_error`, or `invalid_design`.
5. Remove exact global position and heading from the controller's observation.
6. Supply only observations permitted by the canonical robot design.
7. Count and surface controller errors instead of silently hiding them.
8. Collect telemetry in memory with collision-free run identifiers.
9. Correct or replace the existing CSV sensor logging.
10. Validate geometry before starting physics.
11. Add a maximum step count and process timeout.
12. Produce a stable result object independent of the desktop UI.

The version-one adapter may continue importing PySide6 if that saves time. Removing
the GUI dependency is optimization, not a prerequisite for the experiment.

## 8. Design and controller spaces

The design space must permit meaningful co-adaptation without permitting trivial
score exploits.

Initial geometry variables:

- sensor count within a small fixed range;
- sensor positions within a bounded body envelope;
- sensor size from an allowed list;
- wheel track within bounds;
- wheel radius within bounds;
- body dimensions or fixed body-area budget;
- mass within bounds if it remains a meaningful simulator variable.

Initially fix or tightly bound friction and motor constants. Do not let geometry
increase its collision envelope simply to remain counted as on-track.

Initial controller space:

- base speed;
- proportional, integral, and derivative gains;
- sensor weighting;
- line-loss response;
- bounded speed scheduling;
- optionally a small finite-state policy.

The controller receives sensor readings and timestep only. Encoder data may be
added later only if represented in the geometry and supplied symmetrically.

## 9. Tracks and evaluation

Use three sets:

1. **Anchor track:** fixed and visible every iteration. Its SVG makes progress easy
   for humans to compare.
2. **Development set:** visible to agents through returned results and used during
   iterative learning.
3. **Held-out set:** never included in prompts or development returns. Used at
   preregistered checkpoints and final evaluation.

Use validated parameterized track families rather than unconstrained random
segments. Families may include oval, S-bend, slalom, hairpin, and mixed-radius
circuits.

Every condition uses identical track definitions, seeds, noise settings, and order.
Run conditions sequentially or interleave them deterministically; do not change
world conditions based on current scores.

## 10. Metrics and score

Record raw components before choosing or calculating a composite:

- completion;
- normalized progress;
- completion time;
- RMS centre-line error;
- maximum centre-line error;
- loss-of-line events;
- steering oscillation;
- control effort;
- controller errors;
- performance under sensor noise;
- performance under motor variation;
- development versus held-out gap.

The primary score should prioritize in this order:

1. valid design;
2. completion;
3. progress when incomplete;
4. robustness;
5. speed and precision among reliable finishers.

Freeze the exact formula before the recorded run. Publish both the composite and
all components so the formula cannot conceal trade-offs.

Also record learning-system measures:

- improvement by iteration;
- best-so-far and current score;
- worst-case score;
- tokens and estimated cost;
- improvement per 10,000 tokens;
- invalid artifacts and repair calls;
- number and content of working-agreement revisions;
- requested measurements and which were actually used in reasoning.

## 11. SVG generation

Generate SVG directly from track JSON and trajectory telemetry.

Every trial SVG should show:

- track centre line and tape width;
- start and finish;
- robot trajectory;
- path colour by centre-line error or speed;
- finish or failure marker;
- score, elapsed time, and termination reason;
- condition, iteration, track, and seed identifiers.

For each condition and iteration, generate:

- anchor-track trajectory;
- representative trajectory;
- worst failure;
- summary montage comparing current, previous, and best-so-far.

SVG is the canonical visual artifact. PNG thumbnails are optional if the Maps app
needs them.

## 12. Maps and public spectator record

Each condition has its own base map and iteration maps. The iteration map notes link
to the iteration summary, representative SVGs, relevant entities, feedback, and the
single shared leaderboard.

The leaderboard is experiment-level evidence, not another topology actor:

```text
runs/<experiment-id>/leaderboard.json
runs/<experiment-id>/leaderboard.md
runs/<experiment-id>/leaderboard.svg
```

Both conditions' iteration notes link to the same leaderboard artifact. The Maps
app remains the public spectator interface. No simulator server is required.

The control map must show proposal versions, evaluator critiques, test submission,
race returns, post-race advice, and retrospective changes. This makes its internal
work as inspectable as the LoopSense pair rather than representing it only as a
score.

## 13. Deterministic local orchestrator

The orchestrator is a finite state machine, not an autonomous agent. It receives no
open-ended shell objective.

Permitted capabilities:

- read experiment configuration and approved prior artifacts;
- call one configured model API;
- write under the current experiment run directory;
- validate JSON and YAML against local schemas;
- invoke a fixed simulator command with fixed arguments;
- invoke a fixed SVG-generation command;
- calculate hashes, metrics, budgets, and leaderboard files;
- stop, resume, and report status.

It should not have:

- general shell access chosen by the model;
- arbitrary tool execution;
- browser or email access;
- credentials other than the model API key and optional repository sync credential;
- write access outside the experiment output directory;
- permission to change prompts, budgets, schemas, scoring, or held-out tracks during
  a recorded run.

Agent output is data. It never becomes a command line. Paths are generated by the
orchestrator, not accepted from model output.

Each state transition appends an event to an immutable JSONL audit log with:

- timestamp;
- condition and iteration;
- state entered and exited;
- artifact hashes;
- model request identifier;
- token usage;
- validation result;
- simulator version;
- failure or retry reason.

Use an atomic checkpoint after every successful state. A resumed run continues from
the first incomplete state without repeating completed model calls or trials.

## 14. Model calls and budgets

Begin with the cheapest model being considered, but run a small artifact-validity
test before the experiment.

Freeze and record:

- exact model identifier;
- reasoning setting;
- temperature or sampling controls;
- maximum output size;
- prompt templates and hashes;
- total token budget per condition;
- maximum token budget per iteration;
- repair-call allowance;
- timeout and retry policy.

Fairness is based on total budget and access to evidence, not identical call count.
The runner must never silently upgrade one condition to another model.

Suggested first configuration:

- two unscored smoke-test iterations per condition;
- five recorded iterations per condition;
- one mechanical repair call per malformed agent artifact;
- two pre-test evaluator reviews in the control condition;
- fixed total token budget per condition;
- final held-out evaluation after iteration five.

Decide whether to extend to ten recorded iterations before examining comparative
scores, or preregister a non-score-based continuation rule.

## 15. Prompt and context isolation

Prompts should be assembled from an allowlist for each actor and state. Do not point
agents at the entire run directory.

The runner records a manifest of every input supplied to every call. This proves
that:

- neither agent read Entity 2;
- each received only its addressed return entity;
- held-out tracks were not exposed;
- the LoopSense Geometry Builder received Integrator Feedback;
- the control Optimizer received evaluator advice;
- private expertise remained actor-specific;
- both conditions received equivalent world measurements and constraints.

## 16. Retrospectives

After each iteration:

1. Ask each agent separately what helped, hindered, or surprised it.
2. Ask what it proposes changing in the working agreement and why.
3. Exchange the proposals.
4. Permit one bounded reconciliation call if proposals conflict.
5. Record accepted, rejected, and deferred changes.
6. Validate that accepted changes do not alter fixed experimental rules.
7. Save the next version of the working agreement.

The retro cannot change:

- number of agents;
- forward or return edges;
- model;
- total budgets;
- score;
- track split;
- held-out access;
- control review cap;
- simulator version during a recorded batch.

## 17. Build phases

### Phase 1 — Freeze specifications

- validate both base maps in the Maps renderer;
- write the two initial working agreements;
- freeze schemas and measurement catalogue;
- freeze design bounds;
- freeze score and track split;
- pin RobotTraceSim source revision and license notice.

Exit criterion: a human can trace every permitted input and output for both
conditions without implementation ambiguity.

### Phase 2 — Build evaluator

- portable native build;
- headless adapter;
- restricted controller observations;
- canonical geometry translation;
- deterministic seeding;
- explicit termination reasons;
- metrics and trajectory capture;
- SVG output.

Exit criterion: the same package and seed produce byte-equivalent result JSON and
equivalent trajectories across repeated local runs.

### Phase 3 — Build orchestrator

- state machine and checkpoints;
- model client;
- prompt allowlists;
- schema validation and repair policy;
- budgets and audit log;
- separate condition workflows;
- retro workflow.

Exit criterion: mock agents can complete five iterations without manual file
movement, hidden-context leakage, or writes outside the run directory.

### Phase 4 — Integrate Maps artifacts

- generate iteration YAML overrides;
- link entities and SVGs;
- generate the shared leaderboard;
- verify both maps render;
- verify relative/public artifact URLs.

Exit criterion: a spectator can navigate both conditions and understand one full
iteration without reading source code.

### Phase 5 — Smoke test

- run two disposable iterations per condition;
- fix only mechanical or specification defects;
- do not use smoke-test scores as experimental evidence;
- reset private state, artifacts, and starting designs;
- tag the exact experiment configuration.

Exit criterion: both conditions finish unattended under their budgets and produce
complete comparable records.

### Phase 6 — Recorded run

- run the preregistered number of iterations;
- do not change code or configuration mid-run;
- stop and version a new run if an integrity defect requires a change;
- perform final held-out evaluation;
- publish all outcomes, including failures and ambiguous results.

## 18. Testing

Minimum automated tests:

- YAML and JSON schema validation;
- geometry bound enforcement;
- controller observation contains no privileged pose fields;
- identical seed determinism;
- distinct seed noise variation;
- finish, off-track, timeout, invalid design, and controller-error classification;
- score component calculations;
- measurement request allowlisting;
- context manifest enforcement;
- token budget hard stop;
- control review-cap enforcement;
- retrospective cannot mutate fixed rules;
- checkpoint resume does not duplicate model calls;
- SVG generation for finish and failure cases;
- leaderboard derived only from signed/hashed result JSON;
- no agent-provided path escapes the run directory.

## 19. Failure and recovery policy

- **Invalid model artifact:** one repair call with validation errors only; then mark
  invalid and apply the preregistered score consequence.
- **Model API transient failure:** bounded retries with recorded backoff; no prompt
  changes.
- **Simulator crash:** retry once with the identical package and seed; repeated
  failure stops the experiment for integrity review.
- **Budget exhausted:** stop that condition at the same budget boundary specified
  before the run; do not grant discretionary extra calls.
- **Harness defect:** stop both conditions. Fix, version, reset, and begin a new run.
- **Machine interruption:** resume from the last atomic checkpoint.

## 20. Remaining choices that do not block implementation

These values must be frozen before the recorded run but do not block building:

- exact cheapest model identifier and reasoning setting;
- five or ten recorded iterations;
- total token budget;
- detailed score weights;
- precise geometry bounds;
- exact development and held-out track counts;
- whether full telemetry is committed or stored outside Git;
- whether conditions run sequentially or deterministically interleaved.

Defaults in this plan are sufficient for implementation and smoke testing.

## 21. Definition of done

The experiment system is ready when one command can:

1. validate the frozen configuration;
2. run both conditions under equal declared budgets;
3. complete the configured iterations without human routing;
4. evaluate identical track and seed batches;
5. generate maps, entities, feedback, SVGs, audit logs, and leaderboard;
6. resume safely after interruption;
7. prove which context each agent received;
8. synchronize a complete spectator record to Randow Maps;
9. expose no arbitrary model-directed shell or filesystem capability;
10. preserve enough evidence for another person to reproduce or challenge the
    result.

