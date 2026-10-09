# Robot Race Map-Driven Architecture Specification

Status: canonical (incorporates the former Map-Driven Race System Specification)

## Implemented cutover clarifications

The canonical package stores only `base.yaml` and contiguous
`scenario-iteration-N.yaml` files as root YAML. Control configuration is under
`config/workflow.yaml` and `config/race.yaml`; templates live under
`robotrace/package-templates/` and are cloned to top-level race-owned packages.
Preparation, per-entrant review acknowledgement, validation/freeze, and run are
separate UI phases. Immediately before execution, the pair service verifies
both reviews, package identities and common settings, frozen definition hashes,
controller/simulator versions, initial readiness, and resumable transaction
state. The normal UI and default CLI use `MapDrivenController`; the historical
condition-specific runner is exposed only by the explicitly named legacy CLI.

Iteration scenarios inside each race-owned package are authoritative. Actions
receive only topology-authorized entity payloads, and action transitions commit
entity versions, current pointers, scenario state, events, and checkpoints as
one recoverable transaction. Missing entities are absent rather than represented
by placeholder artifacts. Completed state is published directly from the
packages, including final held-out evaluation, leaderboard, report, and links.

Status: agreed design for implementation handoff  
Date: 2026-10-08  
Scope: restructuring the Robot Race so that each Randow Map is the authoritative work surface and structural source of truth for one team in one race

## 1. Purpose

The Robot Race currently uses a deterministic runner that contains condition-specific workflow knowledge and subsequently generates Randow Map scenarios representing completed work.

The target architecture reverses that relationship:

- each team's Randow Map is the authoritative work surface;
- the topology is the structural source of truth for actors, actions, entities, permitted reads, permitted writes, and routing;
- agents work on scenario state and scenario-related artifacts;
- a generic controller interprets and enforces the map rather than encoding team-specific workflows;
- a new or changed topology must not require a controller code change;
- every race receives new, race-specific map packages so that team definitions may evolve between races without rewriting the historical record.

This document specifies the agreed architecture. It does not authorize changes to the canonical Randow Maps schema unless separately agreed.

## 2. Core principles

### 2.1 The map is authoritative

`base.yaml` is not a visualization produced by the controller. It defines the team's structural operating model.

The topology owns:

- actor identity;
- the action associated one-to-one with each actor;
- entities in the system;
- which actions consume which entities through `used by` edges;
- which actions produce which entities through `generates` edges;
- return-flow routing;
- public, private, and internal structural placement;
- structural measures.

The controller must not maintain a second actor/entity routing table or hard-coded equivalent of the topology.

### 2.2 Scenario state is live work state

Agents operate on the current scenario. The scenario is not generated only after the work has finished.

Every work event must be recorded. Every affected map element must be updated when its state changes. Elements that were not affected must not be changed merely to show activity.

The map face remains human-readable:

- scenario labels contain compact state summaries;
- scenario notes contain fuller explanation and links;
- detailed artifacts live in scenario-related folders;
- measurements use the canonical topology-measure/scenario-measurement model;
- edge confidence is recorded in scenario overrides where applicable.

### 2.3 The controller is generic

The controller is deterministic orchestration software, not an autonomous agent. It:

- loads a map package;
- derives access and routing from its topology;
- determines eligible actions using generic readiness rules and the package workflow policy;
- invokes the configured runtime for an action;
- validates outputs;
- applies atomic scenario, artifact, and event-log updates;
- enforces budgets and frozen configuration;
- runs deterministic components such as the simulator;
- records manifests, hashes, measurements, results, and audit evidence.

The controller must not branch on team names such as `loopsense`, `control`, `randow-maps`, or `opt-eval`.

### 2.4 A race freezes its own team definitions

There is no separately maintained, permanently canonical team definition spanning every race.

Each race-specific map package contains the complete team definition used for that race. A later race may be cloned from an earlier map package and then edited, but the earlier package remains immutable historical evidence.

Race-to-race comparisons must record definition changes because improved results may arise from changed topology, instructions, policy, contracts, models, or race configuration as well as learning.

## 3. Repository structure

Race map packages live at the same level as other Loopsense maps, not inside the neutral experiment machinery.

Target shape:

```text
loopsense/
  loopsense/                         # existing original Loopsense map

  robot-race/                        # neutral experiment machinery
    controller/
    simulator/
    schemas/
    evaluation/

  robot-race-5-randow-maps/          # Race 5 Randow Maps team package
    base.yaml
    race.yaml
    workflow.yaml
    actions/
    entities/
    scenario-iteration-0.yaml
    iteration-0/

  robot-race-5-opt-eval/             # Race 5 Opt-Eval team package
    base.yaml
    race.yaml
    workflow.yaml
    actions/
    entities/
    scenario-iteration-0.yaml
    iteration-0/
```

The exact internal names of generic Python modules may change during implementation. The ownership boundaries above must not.

### 3.1 Map proliferation is accepted

There will be one map package per team per race. This is intentional. Real teams using maps as work surfaces will also create many maps. Navigation and archival can be improved later without collapsing race-specific maps back into shared mutable definitions.

## 4. Map package contract

A race-specific map package contains the topology, executable action definitions, entity contracts, workflow override, race configuration, live scenarios, artifacts, and history for one team in one race.

Recommended layout:

```text
robot-race-5-randow-maps/
  base.yaml
  race.yaml
  workflow.yaml

  actions/
    action0/
      instructions.md
      runtime.yaml
    action1/
      instructions.md
      runtime.yaml
    action2/
      runtime.yaml

  entities/
    entity0/
      contract.schema.json
    entity1/
      contract.schema.json

  scenario-iteration-0.yaml
  scenario-iteration-1.yaml

  iteration-0/
    events.jsonl
    entity0/
    entity1/
    entity2/
    entityR1/
    entityR2A/
    entityR2B/

  iteration-1/
    events.jsonl
    ...
```

Scenario YAML files should initially remain in the map root unless the Randow Maps application is explicitly updated and tested to discover scenarios in nested folders. Detailed artifacts belong in the corresponding iteration folder.

## 5. Source-of-truth boundaries

Each file type has one non-overlapping responsibility.

### 5.1 `base.yaml`

Authoritative for structural identity, topology, permissions, routing, measures, and dimension axes.

It must conform to canonical Randow Maps schema v0.2 and the canonical authoring method. Scenarios may not add nodes or edges or alter structural routing.

### 5.2 `actions/<action-id>/instructions.md`

Authoritative instructions for performing that action when its runtime is model-backed.

An actor operates only through its one associated action. In this operational sense, the action is the instruction-bearing unit.

The association is resolved by convention:

```text
action0 -> actions/action0/instructions.md
```

Human-facing action notes in `base.yaml` should summarize the action and may link to the instruction file. The controller must not scrape notes to locate instructions.

### 5.3 `actions/<action-id>/runtime.yaml`

Minimal binding for information that cannot currently be expressed in the Randow Maps topology schema, chiefly how the action is executed.

Examples:

```yaml
kind: model
```

```yaml
kind: component
component: robotrace.simulator
```

The permitted runtime vocabulary must be small, validated, and owned by the generic controller. Arbitrary shell commands are prohibited.

### 5.4 `entities/<entity-id>/contract.schema.json`

Optional machine-readable artifact contract for an entity. The association is resolved by directory convention and must not be repeated in a registry.

Contracts define payload structure. They do not redefine who may read or write the entity; topology edges remain authoritative for that.

### 5.5 `workflow.yaml`

Authoritative only for scheduling, repetition, and completion semantics that cannot be derived from the current edge vocabulary.

It must not repeat entity routing or lists of what each actor generates and consumes.

### 5.6 `race.yaml`

Authoritative for race-specific experimental parameters, including model selection, budgets, tracks, seeds, scoring configuration, publication settings, and other fixed run inputs.

Budgets belong here rather than in team workflow definitions unless a workflow needs to name a generic kind of limit.

Budget scope. "Race budget" means the limit is declared once, in `race.yaml`, and applies equally to every entrant. It does not mean one shared pool. Enforcement scope differs by field:

| Field | Counted | Resets |
|---|---|---|
| `budget.max_action_runs` | per entrant, per iteration | each iteration |
| `budget.max_tokens_per_iteration` | per entrant, per iteration | each iteration |
| `budget.total_tokens_per_condition` | per entrant, across all iterations | never |

User-facing descriptions of these fields live in `orchestrator/field_docs.py` and must agree with this table.

### 5.7 Scenario YAML

Authoritative for the current human-readable state of the topology in that iteration:

- dimensions;
- label and note overrides;
- edge confidence;
- measurements;
- links to detailed artifacts.

Note links are sufficient for artifact references in the initial implementation. No Randow Maps schema extension is required.

### 5.8 Scenario artifact folders

Authoritative for detailed work products too large or structured to live in scenario YAML, such as geometry, controller, candidate, evaluation, telemetry, Markdown reports, and SVGs.

### 5.9 `events.jsonl`

Authoritative append-only chronology of work events and state transitions within the scenario.

### 5.10 Race manifest

Authoritative frozen record of the package and execution inputs. It must include hashes of at least:

- `base.yaml`;
- `workflow.yaml`;
- `race.yaml`;
- every action instruction file;
- every action runtime binding;
- every entity contract;
- controller and simulator versions.

## 6. Topology-derived authorization

The controller derives permissions from `base.yaml`.

For an action:

- it may read an entity only when an applicable `used by` edge connects that entity to the action;
- it may create or update an entity only when a `generates` edge connects the action to that entity;
- it may not gain access merely because a file is present in the same package or scenario directory;
- return-flow entities obey the same access rules as other entities;
- `direction: return` describes structural direction and presentation, not a separate permission mechanism;
- public, private, and internal placement does not independently grant filesystem access;
- all reads supplied to a model call must be assembled from the permitted topology neighbourhood;
- all writes must be validated against both topology authorization and the entity contract, where present.

The controller must reject undeclared reads, undeclared writes, structural changes attempted through a scenario, and output for an entity not generated by the active action.

## 7. Generic execution semantics

The controller should infer as much execution as possible from topology rather than restating the map in another workflow language.

### 7.1 Generic readiness rules

Initial implementation:

1. An action is eligible when all required entities connected to it by `used by` edges have available current versions, or when it is declared an entry action.
2. The controller supplies only the action's permitted readable entity state, instructions, applicable constraints, budget state, and race configuration.
3. A successful action invocation may update only entities it generates.
4. A generated new entity version may make another action eligible.
5. An action runs once for a particular set of input versions unless re-entry policy permits another invocation.
6. A deterministic component action follows the same topology authorization and event-recording rules as a model action.
7. The controller continues until the completion predicate is satisfied, a declared limit is reached, or execution fails validation.

### 7.2 Generic defaults and per-map override

Generic defaults belong to the harness, not to any map. Initial values: `reentry_default: on_new_inputs`, `failure_policy: stop`, `transaction_recovery: reject_incomplete`.

Each map package contains a small `workflow.yaml` override. It declares only semantics that cannot be inferred safely, such as:

- entry actions;
- re-entry behavior;
- completion predicate;
- action invocation limits or references to limits supplied by `race.yaml`;
- exceptional gating rules, if required.

Illustrative shape only—the implementation may refine field names before freezing the policy schema:

```yaml
version: 1

entry_actions:
  - action0

reentry:
  action0: on_new_inputs
  action1: on_new_inputs
  action2: once_per_iteration

iteration_complete_when:
  entities_present:
    - entity2
    - entityR1
    - entityR2A
    - entityR2B

limits:
  max_action_runs_from: race.yaml#budget.max_action_runs
```

This policy must be validated against the topology: every referenced action and entity must exist.

### 7.3 LoopSense behavior

The LoopSense sequence should emerge from readiness and topology:

- geometry action produces the geometry entity;
- geometry enables integration;
- integration produces the runnable package;
- the package enables the simulator;
- race returns enable their addressed recipients;
- integration feedback becomes available to the geometry action for the next outer iteration;
- the workflow completion predicate closes the current iteration at the agreed state.

The generic controller must not contain a LoopSense-specific build function.

### 7.4 Opt-Eval behavior

The Opt-Eval inner loop should also emerge from readiness and topology:

- optimizer produces a candidate;
- candidate enables evaluator;
- evaluator either produces feedback, which re-enables optimizer, or an approved build, which enables the simulator;
- budget and workflow policy bound the loop;
- the selected build races once per outer iteration.

The generic controller must not contain an Opt-Eval-specific build function.

## 8. Iterations, scenarios, and dimensions

Each team/race map has one scenario per outer race iteration.

The topology should not use `condition` as a scenario dimension because each experimental entrant is already a separate map package.

The recommended axes are:

```yaml
dimension_axes:
  - time_horizon
  - iteration
```

Example scenario dimensions:

```yaml
dimensions:
  time_horizon: race-5
  iteration: 2
```

`time_horizon` is retained because it is mandatory under the canonical Randow Maps authoring method. `iteration` expresses the position within the race.

Each scenario must inherit from its package's `base.yaml` and must use only valid v0.2 overrides.

## 9. Opt-Eval inner-cycle history

Opt-Eval revisions within an outer iteration must not silently overwrite one another and do not each require a separate Randow Map scenario.

Use immutable cycle artifacts plus a live scenario projection:

```text
iteration-2/
  events.jsonl
  opt-eval/
    cycle-0/
      candidate.json
      evaluation.json
    cycle-1/
      candidate.json
      evaluation.json
    selected/
      manifest.json
```

During execution:

- the scenario's candidate and feedback elements show the current state;
- each candidate/evaluation cycle is preserved immutably;
- the event log records the chronology;
- the final selected build is linked from the scenario;
- Git may record completed checkpoints but is not the primary runtime history mechanism.

This design should later generalize to continuous or Kanban-style work in which the map presents current state while append-only events and artifacts preserve history.

## 10. Atomic state transitions

Agents own the semantic changes, but they do not perform uncontrolled raw edits to scenario YAML.

The controller must expose constrained operations such as:

- read permitted entity;
- write a new entity artifact version;
- update an entity's scenario label and notes;
- update an action's scenario label and notes;
- append a measurement;
- update edge confidence and evidence notes;
- append a work event.

For each accepted action result, the controller applies one validated transaction covering:

1. artifact writes;
2. scenario overrides and measurements;
3. immutable version metadata;
4. the appended event record;
5. checkpoint/manifest state.

On validation or write failure, none of the transition should become the visible committed scenario state. Resume behavior must detect and recover or reject incomplete transactions deterministically.

## 11. Race configuration UI

The race UI has two explicit phases, which may be presented in one continuous interface.

### Phase 1: Prepare the race

The UI:

- creates or clones one new race-specific map package per entrant;
- creates the initial scenario for each package;
- permits deliberate edits to topology, action instructions, workflow policy, contracts, runtime bindings, and race settings;
- shows provenance from any earlier package used as a starting point;
- validates each complete package;
- reports definition differences from the prior race where applicable.

The state is `draft` until validation succeeds and the operator chooses to freeze.

### Phase 2: Freeze and run

The UI/controller:

- freezes and hashes both map packages;
- writes the race manifests;
- prevents definition changes during the recorded race;
- runs both entrants under the frozen configuration;
- allows only controller-mediated scenario and artifact state transitions;
- exposes live scenario state, artifacts, events, results, and failures;
- marks packages complete only when their declared completion rules are satisfied.

Suggested lifecycle:

```text
Draft -> Validated/ready -> Frozen/running -> Complete
                             |                |
                             +----> Failed <--+
```

The UI must not silently author a bespoke workflow during the run. It may scaffold a policy from generic defaults during preparation, but the resulting `workflow.yaml` must be visible, editable, validated, and frozen before execution.

## 12. Experimental terminology

The runtime architecture removes `condition` as a hard-coded controller concept.

The experiment may still describe its entrants analytically:

```yaml
entrants:
  - map_package: robot-race-5-randow-maps
    experimental_role: treatment
    method: randow-maps
  - map_package: robot-race-5-opt-eval
    experimental_role: comparison
    method: opt-eval
```

These fields belong in experiment/race metadata. They do not control workflow routing and need not be duplicated in every scenario.

## 13. Removal of duplicated registries

The existing team registries must not remain sources of truth for:

- actor/action identity;
- entity ownership;
- generates/consumes relationships;
- routing;
- workflow sequence;
- entity descriptions.

Those facts belong to the topology.

Any remaining facts must move to conventionally located action runtime files, instruction files, entity contracts, workflow policy, or race configuration. Once migrated, the prose registries should be deleted or reduced to generated human documentation with an explicit non-authoritative status.

The controller's `ROLE_INSTRUCTION_PATHS`, `ACTOR_CONTRACTS`, condition branches, and other equivalent duplicated registries must be removed in favor of package discovery and validation.

## 14. Human readability and spectator experience

The same authoritative map supports both workers and spectators at different depths:

- the map face shows topology and current scenario state;
- labels remain within Randow Maps display constraints;
- notes provide concise context and clickable links to Markdown and SVG artifacts;
- artifact folders preserve detailed work;
- events expose chronology;
- measurements and confidence expose evidence;
- race summaries and leaderboards remain experiment-level evidence and may be linked from scenarios without becoming topology actors.

No separate generated spectator topology should replace the authoritative work map. Derived read-only views are permitted so long as they are projections of the same authoritative package.

## 15. Freeze and mutability rules

Before freeze, the operator may edit:

- topology;
- instructions;
- runtime bindings;
- entity contracts;
- workflow policy;
- race configuration;
- initial scenario.

After freeze and before completion, the following are immutable:

- topology;
- action instructions;
- action runtime bindings;
- entity contracts;
- workflow policy;
- race configuration;
- generic controller/simulator versions selected for the run.

During the run, only validated operational state may change:

- scenario overrides;
- measurements;
- linked artifacts;
- event logs;
- checkpoints, audit records, and results.

## 16. Validation requirements

Before a package may freeze:

1. `base.yaml` passes the canonical Randow Maps validator.
2. Every actor is associated with exactly one action and every action with exactly one actor.
3. Every model action has an instructions file.
4. Every action has a valid runtime binding.
5. Every workflow reference resolves to an existing topology ID.
6. Entity contracts are valid schemas and resolve by convention.
7. Every initial scenario inherits from the correct `base.yaml`.
8. Scenario dimensions match topology axes.
9. No scenario attempts structural changes.
10. The topology has complete return flows and no invalid duplicate return path.
11. The workflow has at least one possible entry and a reachable completion predicate.
12. Race budgets and fixed inputs are present and valid.
13. All paths remain inside the map package or explicitly permitted shared read-only experiment resources.
14. A dry-run readiness analysis reports which action is initially eligible and why.

## 17. Migration from the current implementation

Implementation should proceed in bounded stages while preserving existing race records.

### Stage A: Define package formats

- Specify and validate `runtime.yaml`, `workflow.yaml`, and `race.yaml`.
- Establish action/entity path conventions.
- Keep these outside the Randow Maps YAML schema.

### Stage B: Build topology authorization

- Parse topology actors, actions, entities, and edges.
- Build derived read/write permissions.
- Add tests proving undeclared access is rejected.

### Stage C: Build transactional scenario operations

- Add constrained scenario update operations.
- Add immutable artifact versioning and event logging.
- Add atomic commit/recovery behavior.

### Stage D: Generalize execution

- Replace condition-specific build functions with generic readiness scheduling.
- Load action instructions, runtimes, and entity contracts by convention.
- Implement workflow defaults and validated per-map overrides.

### Stage E: Create race-specific packages

- Create Race 5 Randow Maps and Opt-Eval packages from the existing maps and definitions.
- Preserve existing race outputs as historical evidence rather than destructively relocating them without a migration record.
- Remove duplicated registries only after all required information has authoritative new homes.

### Stage F: Update race UI

- Add draft preparation and frozen execution phases.
- Add package cloning, validation, diffing, freezing, and status display.

### Stage G: Remove obsolete paths

- Remove hard-coded condition branches and registries.
- Stop generating maps as post-run representations.
- Retain only derived publication/rendering steps that project the authoritative map state.

## 18. Acceptance criteria

The architecture is complete only when all of the following are true.

### Map authority

- Changing an edge in a draft topology changes runtime access/routing after validation, without a controller code change.
- Adding a valid new actor/action/entity chain can be executed without adding a team-specific controller branch.
- The controller contains no duplicate table of topology reads and writes.

### Isolation

- A model action cannot receive an entity without a matching `used by` edge.
- A model action cannot update an entity without a matching `generates` edge.
- Directory proximity does not grant access.

### Instructions and contracts

- Each model action's instructions are loaded through the action-ID directory convention.
- Each entity contract is loaded through the entity-ID directory convention.
- Missing or invalid required files prevent freeze.

### Execution

- Both Randow Maps and Opt-Eval teams run through the same generic controller.
- Opt-Eval can repeat candidate/evaluation cycles without controller condition branches.
- LoopSense and Opt-Eval terminate using their package policies.
- A third materially different valid topology can be smoke-tested without editing controller code.

### State integrity

- Every successful action produces one coherent scenario/artifact/event transition.
- A forced failure during a transition does not leave a visibly half-updated scenario.
- Resume either completes or rejects an interrupted transaction deterministically.

### Historical record

- Every outer iteration is a visible scenario.
- Every Opt-Eval inner cycle remains inspectable as immutable artifacts/events.
- Race packages remain frozen after completion.
- Definition differences between races are inspectable.

### UI

- The operator can prepare, edit, validate, freeze, and run a race.
- The UI clearly distinguishes draft, ready, frozen/running, complete, and failed states.
- No recorded race starts before the operator freezes its packages.

### Randow Maps fidelity

- The topology remains the Moving Parts structural SSOT.
- Scenarios contain only valid overrides, dimensions, confidence, and measurements.
- Labels, notes, IDs, return flows, boundaries, and measurement records follow the canonical authoring method and schema.

## 19. Non-goals for the first implementation

- Do not change the canonical Randow Maps schema solely to support artifact links.
- Do not make every inner Opt-Eval cycle a separate scenario.
- Do not use Git commits as the primary runtime event store.
- Do not implement continuous/Kanban operation yet; preserve a path toward it.
- Do not solve map proliferation yet.
- Do not create arbitrary executable hooks or general shell access in map packages.
- Do not carry mutable learning implicitly between race packages.
- Do not optimize away the explicit prepare-and-freeze transition.

## 20. Principal architectural test

The implementation should be judged by one overriding test:

> A new race can introduce a changed or entirely different valid team topology by creating a new map package, without changing the generic controller.

If that is not true, team definition remains embedded in the experiment machinery and the migration is incomplete.
