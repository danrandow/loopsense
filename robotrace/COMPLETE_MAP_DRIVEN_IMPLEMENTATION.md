# Complete the Map-Driven Robot Race Implementation

## Task authority

Implement the remaining map-driven Robot Race system end to end.

Do **not** stop after adding package formats, validators, controller classes,
unit tests, UI scaffolding, or manifests. This task is complete only when the
deterministic end-to-end acceptance run described below succeeds through the
real preparation UI and the map-driven controller.

Race 5 and Race 6 are historical evidence. Do not edit, relocate, regenerate,
or "repair" either race or their artifacts.

Before changing Randow Map YAML, read completely and follow:

1. `/Users/danrandow/github/randow-maps-authoring/skills/randow-maps-authoring/SKILL.md`
2. `/Users/danrandow/github/randow-maps/docs/schema.yaml`
3. `/Users/danrandow/github/loopsense/AGENTS.md`

Preserve unrelated changes in the existing dirty worktree. Inspect the current
diff before editing and do not overwrite work merely because it is uncommitted.

## Definition of done

All of the following must be true:

1. The Robot Race UI prepares two new race-owned entrant packages from clean
   templates.
2. Non-map YAML is stored below `config/` and never appears in the Randow Maps
   scenario selector.
3. The operator can inspect and edit topology, action instructions, runtime
   bindings, contracts, workflow, and race settings before execution.
4. The operator must explicitly review both packages and select **Validate and
   freeze**.
5. No model or simulator call can occur before both packages validate and
   freeze.
6. **Run frozen race** invokes only the map-driven execution path. The normal UI
   must not call `ExperimentRunner`.
7. Real model-backed actions and the real simulator adapter execute through
   topology-derived read/write authorization.
8. Every action transition commits artifacts, scenario state, event history,
   and checkpoint state transactionally.
9. Every completed iteration has one valid
   `scenario-iteration-<N>.yaml` inside its race-owned package.
10. Interruption and resume do not repeat committed work.
11. Final evaluation, leaderboard, report, manifest, and map links are produced
    from the authoritative package state.
12. Every generated topology and scenario passes the canonical Randow Maps
    parser/validator and renders through the real layout API.
13. A deterministic two-entrant, two-iteration dry run completes through the
    actual UI without using Race 7.
14. All existing and new tests pass.

If any item remains unmet, report the implementation as incomplete. Do not
describe a partial milestone as completion.

## Existing partial implementation

The repository already contains useful scaffolding. Reuse and finish it rather
than starting over.

### Present but incomplete

- `orchestrator/map_package.py`
  - parses topology, workflow, race settings, runtimes, instructions, and
    contracts;
  - derives basic reads and writes from topology edges;
  - validates some scenario and reachability rules;
  - currently expects `workflow.yaml` and `race.yaml` at package root;
  - does not enforce the root YAML allowlist;
  - does not use the full canonical Randow Maps validator;
  - performs only a shallow subset of JSON Schema validation;
  - accepts any number of seed scenarios rather than exactly one initial
    scenario at preparation time;
  - does not fully validate identity agreement or race-pair settings.

- `orchestrator/controller.py`
  - has a generic readiness loop and simple freeze verification;
  - has no production model/component executor;
  - runs only an already-existing single scenario;
  - does not create subsequent iteration scenarios;
  - does not run a complete two-entrant race;
  - does not publish final outputs;
  - initializes missing return entities with `not_available` payloads and then
    incorrectly treats them as available;
  - is not called by the Robot Race UI.

- `orchestrator/transactions.py`
  - stages scenario, entity, and event changes;
  - has limited hand-written contract checking rather than complete JSON Schema
    validation;
  - can append an event and checkpoint;
  - rejection/recovery semantics are incomplete;
  - rollback does not yet prove atomicity for every failure point;
  - does not include all budget/model/component metadata required for audit and
    resume.

- `tests/test_map_driven.py`
  - proves basic authorization, structural scenario rejection, prepared
    transaction rejection, and a simple generic topology;
  - uses toy executors and does not prove production execution or UI cutover.

- Race 5 package directories
  - are retrospective, incomplete prototypes;
  - contain root-level `workflow.yaml` and `race.yaml`;
  - must remain untouched and must not be used as templates.

### Still active legacy path

- `orchestrator/web.py` imports `ExperimentRunner` and `/start` immediately calls
  it.
- `orchestrator/runner.py` branches on `loopsense` and `control`, loads role
  instructions through hard-coded registries, and reconstructs maps after the
  run.
- `orchestrator/model_client.py` uses `ROLE_INSTRUCTION_PATHS` and
  `ACTOR_CONTRACTS` rather than package files.
- The `robotrace` and `robotrace-ui` entry points still point to the legacy
  runner and legacy UI behavior.

These facts are the reason the previous implementation was only half complete.

## Required final package format

Create clean templates under:

```text
robotrace/package-templates/
  randow-maps/
  opt-eval/
```

Each prepared race creates top-level, race-owned packages such as:

```text
robot-dry-run-map-driven-1-randow-maps/
robot-dry-run-map-driven-1-opt-eval/
```

Use a safe, validated slugging rule for named dry runs. Recorded numbered races
may use `robot-race-7-randow-maps/` and `robot-race-7-opt-eval/`, but this task
must not consume Race 7.

Canonical package layout:

```text
<package>/
  base.yaml
  scenario-iteration-0.yaml
  <map-id>.log.json
  provenance.json
  race-manifest.json

  config/
    workflow.yaml
    race.yaml

  actions/
    <action-id>/
      instructions.md       # required for model actions
      runtime.yaml          # required for every action

  entities/
    <entity-id>/
      contract.schema.json  # required when the entity has structured output

  iteration-0/
    events.jsonl
    checkpoint.json
    .transactions/
    <entity-id>/
      current
      versions/<version-id>/
        payload.json
        version.json
```

Only these YAML files are allowed at package root:

- `base.yaml`
- `scenario-iteration-[0-9]+.yaml`

Reject all other root-level YAML. Load workflow and race settings only from
`config/workflow.yaml` and `config/race.yaml`.

## Required implementation work

Complete the following sections in order, but continue through all sections in
the same task.

### 1. Reconcile the documentation

There are currently two overlapping architecture documents:

- `robotrace/MAP_DRIVEN_ARCHITECTURE_SPEC.md`
- `robotrace/MAP_DRIVEN_RACE_SYSTEM_SPEC.md`

Merge the relevant corrections from the newer document into
`MAP_DRIVEN_ARCHITECTURE_SPEC.md`, making it the single canonical architecture
specification. Remove the duplicate document only after confirming no unique
requirement is lost. This implementation brief remains the task checklist.

Update `robotrace/README.md` so it accurately distinguishes legacy historical
execution from the completed map-driven path.

### 2. Build clean templates

Create new `randow-maps` and `opt-eval` templates from the intended experiment
design, not by copying Race 5's retrospective directories wholesale.

For each template:

- author a canonical v0.2 topology;
- preserve the correct closed learning loops and addressed returns;
- use one actor per action;
- define all required measures and dimension axes;
- create model instructions by action ID;
- create runtime bindings for every action;
- create complete entity JSON Schemas;
- create minimal workflow policy;
- create race-setting defaults;
- create a valid initial scenario using block-style YAML;
- validate labels, IDs, boundaries, return flows, dimensions, and overrides
  against the canonical Randow Maps tooling.

Do not put live race IDs into templates.

### 3. Finish package validation

Update `MapPackage` and supporting code to:

- load configuration from `config/`;
- enforce the root YAML allowlist;
- reject hidden identity mismatches between directory, topology, scenarios,
  entrant metadata, and race metadata;
- invoke or faithfully share the canonical Randow Maps v0.2 validation rules;
- require exactly one `scenario-iteration-0.yaml` during preparation;
- reject gaps, duplicates, or malformed iteration scenario filenames during
  execution/resume;
- validate all scenario IDs, map IDs, inheritance, axes, dimension values,
  overrides, confidence values, and measurements;
- use a complete JSON Schema validator for contracts;
- validate runtime output contract references;
- prove return completeness and collision safety;
- prove workflow references and structural reachability;
- distinguish absent inputs from actual entity versions;
- validate common race settings across the entrant pair;
- include every authoritative definition file in package hashes.

Dimension consumers must accept all schema-valid scalar values. Do not add a
Loopsense-only workaround that assumes dimensions are strings.

### 4. Correct readiness and iteration semantics

Remove the `not_available` artifact approach. A missing entity must be absent
from the available-version set.

Define explicit iteration seed behavior:

- iteration 0 begins from the prepared scenario and declared seed entities;
- seed entities with real content must have actual versioned payloads;
- after iteration N completes, create
  `scenario-iteration-(N+1).yaml` transactionally from the completed state;
- carry forward only the state declared by iteration policy;
- update scenario name, notes, and dimensions;
- create the next iteration's seed entity versions without pretending absent
  values exist;
- record the scenario creation event and checkpoint;
- never rerun an action for an unchanged input-version tuple unless policy
  permits it.

Completion predicates operate on committed real entity versions, not filenames
or placeholders.

### 5. Implement production executors

Create a package-driven executor layer used by `MapDrivenController`.

#### Model-backed actions

- Read instructions from `actions/<action-id>/instructions.md`.
- Derive the response contract from the action runtime and target entity
  schemas.
- Supply only topology-authorized entity payloads.
- Supply relevant race constraints and remaining budget.
- Keep held-out data out of development prompts and returns.
- Support deterministic mock and OpenRouter providers.
- Validate output, apply bounded configured repair attempts, and persist request
  identifiers and token usage.
- Store private learning only in a topology-authorized, explicitly declared
  location; do not preserve the legacy actor-name registry implicitly.

Refactor the reusable low-level OpenRouter and deterministic-client code from
`model_client.py`. Remove `ROLE_INSTRUCTION_PATHS` and `ACTOR_CONTRACTS` from the
active map-driven path.

#### Component-backed actions

- Bind `robotrace.simulator` through `runtime.yaml`.
- Reuse the real simulator adapter and validators.
- Run development tracks during iterations and held-out tracks only at the
  declared final evaluation point.
- Produce authorized outcome and addressed return entities.
- Persist trial results, telemetry, track views, summaries, measurement sources,
  seeds, and simulator version.

No executor may branch on the entrant/package name. Differences must arise from
topology, instructions, contracts, workflow, and race settings.

### 6. Complete transactions and resume

Make one action transition atomic across:

- validated entity payload versions;
- current pointers;
- scenario overrides and measurements;
- version metadata;
- event append;
- budget ledger;
- checkpoint state.

Add failure-injection tests at every commit boundary. On failure, either roll
back completely or leave a deterministic recoverable prepared transaction.

Resume must:

- verify frozen hashes first;
- reject incompatible package or controller versions;
- recover or explicitly reject incomplete transactions;
- reconstruct budgets and availability from committed state;
- never repeat a committed model call or simulator trial;
- continue from the exact next eligible action.

### 7. Implement race-pair orchestration

Add a top-level map-driven race service that:

- prepares both entrant packages;
- validates their common experimental settings;
- freezes them as one intended race pair;
- runs the configured number of iterations for both entrants;
- records pair-level status and failure location;
- performs final held-out evaluation;
- creates leaderboard and race report;
- exposes package and iteration links;
- marks completion only after both entrants and final publication succeed.

The pair service must call `MapDrivenController`; it must not call or subclass
`ExperimentRunner`.

### 8. Replace the normal Robot Race UI workflow

Rewrite `orchestrator/web.py` around these explicit phases:

#### Prepare

- choose a fresh numbered race or named dry-run ID;
- select entrant templates;
- clone two race-owned packages;
- show provenance;
- expose editable topology, action instructions, runtimes, contracts, workflow,
  and race settings;
- show readable file/content diffs, not hashes alone;
- persist an unfinished draft safely.

#### Review

Require a separate acknowledgement for each entrant confirming that topology,
instructions, runtimes, contracts, workflow, and race settings were reviewed.
Editing is optional; acknowledgement is mandatory.

#### Validate and freeze

- run package and pair validation;
- show all validation failures without starting execution;
- show initially eligible actions and why;
- write complete manifests;
- disable definition editing for that frozen revision.

#### Run frozen race

- require a separate explicit action;
- re-run preflight verification at the execution boundary;
- execute only through the map-driven race service;
- display progress, current action, failures, package links, scenarios, events,
  leaderboard, and report;
- support safe resume.

The normal UI must not import `ExperimentRunner`. Add a guard test for this.

The legacy runner may remain accessible only through an explicitly named
historical/legacy CLI path until removal is safe. It must not be the default
`robotrace` or `robotrace-ui` behavior.

### 9. Preflight invariants

Immediately before the first model or simulator call, verify all of these in the
execution service, not merely in the UI:

- both race-owned package directories exist;
- neither is a template, Race 5, or Race 6;
- identities agree;
- each package has exactly one initial scenario;
- both packages and their pair validate;
- both review acknowledgements are recorded;
- both manifests exist and match current files;
- controller and simulator versions match the freeze record;
- the map-driven controller is selected;
- no unresolved transaction blocks execution;
- initial readiness yields an eligible action;
- output state is empty or a valid resumable run.

Any failure must stop before external work and produce a visible diagnostic.

### 10. Publication and Randow Maps verification

Scenarios inside the race-owned packages are authoritative. Do not reconstruct a
second independent set of maps after the run.

Generate reports and links from package state. For every topology and scenario:

- parse YAML;
- run canonical Randow Maps validation;
- resolve inheritance;
- build semantic layout;
- call the real layout API;
- perform a browser render smoke test.

The Loopsense implementation must ensure only real map YAML is at package root.
Do not modify the external Randow Maps UI or authoring skill as part of this task;
the owner is handling the dimension-scalar UI fix separately.

### 11. Tests required before completion

Add or update tests covering:

#### Package and schema

- `config/` paths and root YAML rejection;
- canonical topology/scenario validation;
- identity and race-pair mismatch rejection;
- complete JSON Schema enforcement;
- block-style generated scenario YAML;
- numeric and string dimensions accepted by package consumers;
- exact initial-scenario rules and iteration sequence.

#### Authorization and execution

- undeclared reads and writes rejected;
- directory proximity grants no access;
- addressed returns reach only declared consumers;
- a genuinely new valid topology runs without entrant-specific code;
- model and component actions use package bindings;
- missing entities do not satisfy readiness;
- budget exhaustion and workflow stalls fail visibly.

#### Transactions and resume

- failure injection before/after each commit boundary;
- no partial visible state;
- deterministic recovery/rejection;
- committed calls and trials not repeated;
- frozen-definition change blocks resume.

#### UI lifecycle

- Prepare creates two packages and does not execute;
- Review acknowledgement is required;
- freeze is required and separate;
- no model/simulator call before Run;
- normal UI cannot invoke `ExperimentRunner`;
- validation errors are visible;
- progress and failures are visible;
- resume works.

#### Rendering

- configuration files never appear as scenarios;
- every generated initial and iteration scenario returns HTTP 200 from the real
  layout endpoint;
- a browser smoke test confirms the canvas renders;
- published links target authoritative package scenarios.

## Mandatory acceptance run

Do not use Race 7. Prepare a named, disposable dry run such as:

```text
dry-run-map-driven-1
```

Run it through the actual Robot Race UI with:

- both clean templates;
- deterministic mock model provider;
- real simulator adapter;
- two iterations per entrant;
- minimal bounded budgets;
- development tracks and a final held-out evaluation.

Verify and record:

1. two fresh race-owned packages were created;
2. the preparation page exposed all authoritative definitions;
3. review and freeze were separate explicit actions;
4. no call occurred before Run;
5. manifests match package contents;
6. all actions were scheduled from topology;
7. every entity write passed authorization and contract validation;
8. both iterations produced valid authoritative scenarios;
9. events, versions, budgets, and checkpoints agree;
10. an interrupted copy can resume without repeating committed work;
11. held-out data was not exposed during development;
12. leaderboard and report were generated;
13. every scenario rendered through API and browser;
14. Race 5 and Race 6 are byte-for-byte untouched by the implementation task.

The dry-run packages and outputs may remain as explicitly named test evidence,
or be removed only if removal is part of the test's documented cleanup and is
safe. They must never be relabelled as Race 7.

## Verification commands

Use the repository's environment and record the exact commands run. At minimum:

```bash
cd /Users/danrandow/github/loopsense/robotrace
python -m unittest discover -s tests -v
```

Also run:

- the package validator against both templates and both prepared dry-run
  packages;
- the freeze verifier against both manifests;
- the deterministic end-to-end UI acceptance test;
- canonical Randow Maps validation and layout generation for every generated
  YAML map;
- the browser rendering smoke test;
- `git diff --check`.

If the project introduces a more specific test command, document it in
`robotrace/README.md` and run it as part of acceptance.

## Final report required from the implementation session

The final response must include:

- a concise architecture outcome;
- files and subsystems changed;
- the exact acceptance run identity;
- tests and commands executed;
- proof that the normal UI did not use `ExperimentRunner`;
- proof that no model/simulator call preceded freeze;
- proof that every scenario rendered;
- resume-test result;
- confirmation that Race 5 and Race 6 were untouched;
- every remaining unmet acceptance criterion, if any.

Do not claim completion while any required item is missing.
