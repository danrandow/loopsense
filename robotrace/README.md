# LoopSense Robot Race experiment

**Can the shape of an agent team change how quickly it learns?** Robot Race puts two differently organised, two-agent teams into the same measurable world and lets them repeatedly design, race, and improve a line-following robot.

Robot Race builds on [RobotraceSim](https://github.com/Koyoman/robotrace_Sim), created by Arthur Jose Sary and distributed under the MIT License. This repository vendors commit `2c99a9b63db8f9e0ef56c930cf1b360f2a1efc1c` with its original copyright and licence intact. The LoopSense experiment harness and headless adapter are separate additions.

## Map-driven controller

Races run from **map packages**: one self-contained package per entrant, cloned from `package-templates/` and owned by that race. A package holds `base.yaml` (the team's topology), `scenario-iteration-N.yaml` (the live work state), `config/workflow.yaml` and `config/race.yaml`, conventionally located action runtime and instruction files (`actions/<id>/`), entity contracts (`entities/<id>/`), and per-iteration artifacts and `events.jsonl` history. The map is the single source of truth for who does what; the controller reads it and nothing else to decide who may read, write and run.

The two entrants are **Randow Maps** (producer–integrator: Geometry Builder → Robot Integrator), which is the LoopSense condition, and **Opt/Eval** (Robot Optimizer ⇄ Evaluator), which is the evaluator–optimizer control. Templates are in `package-templates/randow-maps` and `package-templates/opt-eval`; the authoritative design is [MAP_DRIVEN_ARCHITECTURE_SPEC.md](MAP_DRIVEN_ARCHITECTURE_SPEC.md).

Verification from this directory:

```bash
python3 -m unittest discover -s tests -v
python3 -m orchestrator.controller validate package-templates/randow-maps
python3 -m orchestrator.controller validate package-templates/opt-eval
```

## Documents

| File | Role |
|---|---|
| [MAP_DRIVEN_ARCHITECTURE_SPEC.md](MAP_DRIVEN_ARCHITECTURE_SPEC.md) | What the system is. **Canonical** architecture. |
| [Loopsense-Robot-Race-Experiment-Design.md](Loopsense-Robot-Race-Experiment-Design.md) | The experiment: question, controls, measures, reporting rules. |
| [COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md](COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md) | Work order for the map-driven cutover. |
| [TRACK_VIEW_SVG_SPEC.md](TRACK_VIEW_SVG_SPEC.md) | Specification for the track-view SVGs. |
| `RACE_16_CHANGES.md`, `RACE_17_CHANGES.md`, `RACE_19_CHANGES.md` | Harness revisions and why scores are not comparable across them. |

This page serves three audiences, in order:

1. **Spectators** who want to understand the idea, watch the teams, and inspect results.
2. **The race operator** setting up a new race or returning to evidence from an existing one.
3. **Implementers** who want to reproduce, challenge, or improve the experiment.

## 1. For spectators

### How to read the maps

The maps are the quickest way to see the experiment. They show who does what, which concrete products move forward, and how race evidence and teammate feedback travel back. Compare both teams under one frozen setup and open the leaderboard beside them.

### Purpose

> Build a small, inspectable experiment that tests whether the LoopSense production topology helps a two-agent team adapt faster or better than a conventional optimizer/evaluator topology.

Both teams repeatedly design a line-following robot, test it in the same simulator, receive objective measurements, and learn across iterations. The agents work between races; they do not control the robot in real time.

The narrow research question is:

> Under the same model, total token budget, simulator, starting state, and evaluation conditions, does a serial producer–integrator topology exhibit a different adaptation trajectory from a conventional optimizer–evaluator pair?

This is a test of how work and feedback are organised—not a claim that LoopSense already solves arbitrary knowledge work. The broader hypothesis and intended product are described in the **[LoopSense product definition](../Loopsense-product-definition.md)**.

### Why this is interesting

Most agent harnesses improve work through a familiar evaluator–optimizer loop: one agent proposes a complete answer, another critiques it, and they revise until they ship. That is the control here.

LoopSense instead models a production relationship. One agent produces a component; another agent is its direct customer, integrates that component into a complete robot, and sends specific integration feedback upstream. After the race, objective evidence returns separately to both roles. The forward products and feedback routes are explicit and inspectable.

Robot Race makes that organisational difference visible. A robot either follows the track or it does not, every run produces measurements and trajectories, and repeated iterations reveal not just who wins but how each team learns.

### Why a robot race

The immediate inspiration was **Genetic Cars**, shared by Andy Masters: colourful, odd little machines are dropped onto a friendly-looking track, then stumble, roll and occasionally succeed. The spectacle makes an abstract improvement process instantly legible and gives people a reason to care about each attempt.

This experiment needs a different learning system. The robots are not a genetically evolved population; agent teams design one robot geometry and controller between trials, and the LoopSense harness organises the work and returns evidence. We therefore use the open-source [RobotraceSim](https://github.com/Koyoman/robotrace_Sim) as the measurable world. It supplies controllable robot geometry, line sensors, controllers, deterministic runs and useful telemetry, while the harness supplies the competing team topologies. Keeping those layers separate is fundamental to the experiment: both teams meet the same simulator, and neither presentation code nor the maps can alter the physics or scoring.

Genetic Cars remains the tonal reference for the spectator experience rather than the experimental mechanism. The goal is to preserve RobotraceSim's precise geometry and evidence while making the robots colourful, personable and funny to watch.

### Spectator views

The first spectator surface is the generated `track-view.svg`. It draws the exact track and recorded poses, but presents the robot as a small colourful character. Its path changes colour with centre-line error and its terminal marker says whether it finished, stalled, timed out or left the track. This works for good runs and for the much more common early failures without inventing movement that did not occur.

Every completed race also writes a self-contained `race-N-replay.html`. It plays every recorded development trial from both teams in iteration order, then ends with the held-out trials. The pit wall places each run beside the plan read from that iteration's scenario map and the result written back to it. The replay is therefore a view over the experiment's existing source of truth—not a separate story database—and all motion comes from recorded telemetry.

The useful next views are deliberately different rather than one overloaded dashboard:

1. **Race replay:** animate the recorded poses on the exact track, with a camera that can follow a successful robot. This is race footage, generated from telemetry rather than a second simulation.
2. **Failure close-up:** when progress is tiny, keep the camera at the start and show heading, wheel effort, sensor activation and line-loss moments at readable scale. A robot wobbling in place is then informative and can still be funny.
3. **Pit wall:** put the replay beside the iteration's score, measurement returns, robot changes and Randow Map. This is the behind-the-scenes story: what the team thought was happening, what the track reported, and what the agents changed next.

The current tracks are planar. They contain straights and arcs, so direction and curvature change, but there is no elevation axis, hill, gravity or road gradient. This is not a limitation of being 2D: Genetic Cars uses its two dimensions as a side view, so vertical position can describe hills, while RobotraceSim uses them as a top-down floor plan. A drawn gradient is easy; making it affect robot performance would require a new simulator model and would change the experimental task.

### What is common between the teams

Both conditions have:

- two AI agents using the same model and model settings;
- the same total token budget and visible budget ledger;
- the same starting state, design constraints, simulator, tracks, seeds, and scoring;
- exactly one selected robot package raced per condition per iteration;
- the same mechanical validation and bounded format-repair policy;
- the same objective race measurements, delivered through two independently addressed return entities;
- no access to held-out tracks and no operational access to the aggregate Race Outcome entity;
- the same deterministic orchestrator, audit log, checkpoints, telemetry, SVGs, and leaderboard; and
- no human routing or retrospective call inside an iteration.

The orchestrator is deterministic software, not another agent. Model output is validated data and can never become executable code, a command, or a filesystem path.

### What is different

| LoopSense condition | Evaluator–optimizer control |
|---|---|
| **Geometry Builder** creates a Geometry Proposal. | **Robot Optimizer** creates a complete robot candidate. |
| **Robot Integrator** is the Builder's direct customer. It incorporates the geometry, adds the controller, and produces the Complete Robot Package. | **Evaluator** inspects the complete candidate and its rationale, then either gives feedback for another revision or approves the candidate as the build to race. |
| The team advances once through a serial production spine before each race. | The pair may use multiple internal critique–revision cycles before each race while budget remains. |
| Explicit entities define the handoff, integration feedback, and addressed race-return paths. | Candidate, evaluator feedback and approved build are separate entities; the Evaluator's approval ends the revision loop. |

A shared Working Agreement, a shared blackboard and private role expertise are deliberately out of scope for now and are deferred to a later experiment.

The independent variable is therefore the organisation of work between races: an explicit producer–customer value flow with attributable return paths versus the classic whole-solution evaluator–optimizer loop.

### How the comparison works

Each iteration starts by cloning the completed state from the previous iteration. The LoopSense team produces a geometry and then an integrated robot. The control can critique and revise complete candidates within its budget. One valid selected build from each condition then runs through an identical batch of tracks and seeds.

The harness records raw performance and learning-system measures, including:

- completion, progress, speed, centre-line error, robustness, oscillation, control effort, and failures;
- current, best-so-far, and worst-case scores;
- improvement by iteration and improvement per 10,000 tokens;
- total tokens, estimated cost, invalid artifacts, and repair calls;
- evaluator–optimizer revision cycles; and
- which measurements were requested, received, and used in later reasoning.

Development evidence is returned to the agents; held-out tracks are reserved for the final evaluation. The exact score weights, model, budgets, geometry bounds, run length, and track sets must be frozen before a recorded run.

For the full protocol, contracts, controls, and rationale, see **[LoopSense Robot Race Experiment Design](Loopsense-Robot-Race-Experiment-Design.md)**. The architecture is specified in [MAP_DRIVEN_ARCHITECTURE_SPEC.md](MAP_DRIVEN_ARCHITECTURE_SPEC.md).

## 2. For the race operator

Use this section to run a race or find the evidence from an earlier one.

### Current status

The map-driven harness runs complete races end to end: prepare, review, freeze, run, then a final held-out evaluation, leaderboard and report. Several races have completed, but this is still a **pilot harness**, not a recorded experiment. Race 18, for example, scored Opt/Eval 12.9 and Randow Maps 0.0, which led to the changes recorded in [RACE_19_CHANGES.md](RACE_19_CHANGES.md). Harness changes alter what the agents see and how runs are scored, so scores are **not comparable across harness versions** (see the `RACE_*_CHANGES.md` files and the `controller_version` in each race manifest). Pilot, dry-run and smoke scores are not experimental evidence.

Before a recorded run, the settings listed in the [design document](Loopsense-Robot-Race-Experiment-Design.md#current-status-and-recorded-run-gate) must be frozen and the configuration tagged.

### Run a race

Start the local interface (it binds to localhost only, so an API key is never exposed on the network):

```sh
cd robotrace
python3 -m orchestrator.web
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). A race moves through four phases:

1. **Prepare.** Choose a fresh race id (the form suggests the next number), then set iterations, provider, model, and the token and action-run budgets. Preparing clones both templates into race-owned packages. The settings apply identically to both entrants. The **Settings reference** link (`/docs`) explains every field and where its value is enforced.
2. **Review.** Inspect each entrant's definition inventory, open the editor for any file you want to change (instructions, contracts, workflow, race configuration), and acknowledge each entrant's review. Saving a definition clears that acknowledgement.
3. **Validate and freeze.** Validation runs without model or simulator work. Freezing hashes the definitions and locks them.
4. **Run frozen race.** The service re-checks both reviews, package identities, common settings, frozen hashes, controller and simulator versions, and readiness, then runs every iteration for both entrants.

Never reuse a race id. A race that fails is recorded as `failed` with the error and cannot be resumed or edited; **Retire** it and prepare a fresh id. A race interrupted at a machine level can be resumed from its last atomic checkpoint with **Resume frozen race**.

### Offline mock or OpenRouter

Choose **Offline deterministic mock** for a no-key, deterministic check of the harness. For a model-backed race choose OpenRouter, enter the exact model slug from [OpenRouter's catalogue](https://openrouter.ai/models), and paste an API key or set it first:

```sh
export OPENROUTER_API_KEY='your-key-here'
python3 -m orchestrator.web
```

The key is held only in the server process and is never written to a package, manifest, log or Git. Before a run, the harness blocks OpenRouter with no key and warns when the model id looks like the offline mock. The model is a race parameter: changing it means a new race.

### What happens in an iteration

Each iteration clones the previous iteration's carried-forward state, runs each entrant's actions as the topology and workflow make them eligible, races one selected robot on the development track, and returns the evidence to the agents for the next iteration. After the last iteration, each entrant's final design is raced once on the held-out track, and that score ranks the leaderboard.

- Every model action is told its role, the objective, the iteration and budget, and which outputs it must write; a missing required output goes back to the model through a bounded repair loop.
- An iteration that cannot finish (no action can run, or a token or action-run budget is spent) does not fail the race. It writes `outcome.json` with the reason and undelivered entities, is not scored, and the next iteration is told.
- If an entrant's final iteration delivers no design, it scores 0.0 on the held-out evaluation and the race still completes.

### Find the leaderboard and evidence

Completed races are listed in the interface with report and leaderboard links. On disk, results are written to the repository root (the parent of `robotrace/`):

- `race-N-race-report.md` and `race-N-leaderboard.json` for the ranking and per-iteration summary;
- `race-N-pair.json` for the race's status, frozen manifests and result hash;
- `race-N-randow-maps/` and `race-N-opt-eval/` for each entrant's package, including `scenario-iteration-N.yaml`, `race-manifest.json`, `final-evaluation.json`, `leaderboard.svg` and `race-report.md`; and
- `iteration-N/` inside each package for `events.jsonl`, `budget-ledger.json`, `summary.json`, `outcome.json`, entity versions, trial telemetry, track views and `iteration-summary.svg`.

Open any `scenario-iteration-N.yaml` in Randow Maps to see that iteration's work state; its notes link to the artifacts behind it.

### Validate or compare packages from the command line

```sh
python3 -m orchestrator.controller validate <package>
python3 -m orchestrator.controller freeze <package> [--manifest PATH]
python3 -m orchestrator.controller compare <previous-package> <current-package>
```

`compare` reports a hash-level definition diff, which is how a change in topology, instructions, contracts, policy or model between races is made visible.

## 3. For implementers

Read in this order: [MAP_DRIVEN_ARCHITECTURE_SPEC.md](MAP_DRIVEN_ARCHITECTURE_SPEC.md) (canonical design), the [experiment design](Loopsense-Robot-Race-Experiment-Design.md) (the research question, controls and reporting rules), then [COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md](COMPLETE_MAP_DRIVEN_IMPLEMENTATION.md) (the work order for finishing the cutover). The `RACE_*_CHANGES.md` files record each harness revision. The broader product hypothesis is in the [LoopSense product definition](../Loopsense-product-definition.md).

The governing constraint: **the map is the single source of truth for team topology.** The controller must not branch on team names such as `randow-maps` or `opt-eval`, and must not keep a second routing table. Both entrants use the map identically; only the topology differs. Agents produce constrained data, a deterministic controller validates and routes it, and a fixed simulator produces the evidence.

### Where things live

- `orchestrator/map_package.py` loads and validates a package and derives read/write permissions from `used by` and `generates` edges. It also runs the canonical Randow Maps validator (`orchestrator/canonical.py`).
- `orchestrator/controller.py` is the generic readiness scheduler, iteration runner and freeze verification. Its CLI is the `robotrace` entry point.
- `orchestrator/transactions.py` applies one atomic artifact, scenario and event transition and rejects incomplete prepared transactions on resume.
- `orchestrator/executors.py` runs actions: model calls (prompt assembly, role brief, required outputs, repair loop) and the simulator action.
- `orchestrator/race_service.py` is the pair lifecycle (prepare, review, freeze, run, retire), final held-out evaluation, reports and leaderboard.
- `orchestrator/web.py` and `field_docs.py` are the local interface and its settings reference.
- `package-templates/` holds the entrant templates; `config/workflow.yaml` and `config/race.yaml` in each package carry the generic-default overrides, budgets, tracks, design bounds, score weights and objective.
- `simulator/` holds the headless adapter and the pinned upstream RobotraceSim; `tracks/` holds track definitions.

### Workflow policy

Generic defaults live in the harness (spec §7.2): `reentry_default: on_new_inputs`, `failure_policy: stop`, `transaction_recovery: reject_incomplete`. A package's `workflow.yaml` overrides only what cannot be inferred from topology: entry actions, required inputs, carry-forward entities, re-entry behaviour, the iteration completion predicate, and `stop_reentry_when_present`. Opt/Eval's inner revision loop is expressed that way, so the Evaluator decides when the build races, with no Opt/Eval code in the controller.

### Before changing anything

```sh
python3 -m unittest discover -s tests -v
```

Tests need the canonical Randow Maps checkout (set `RANDOW_MAPS_ROOT` if it is not at `~/github/randow-maps`), and a handful need the native simulator, built with `python3 simulator/native/build.py`. A substantive change to topology, evidence, budgets, scoring, tracks or agent permissions creates a new experimental design or race configuration, and must not alter a frozen or running race. Edit Randow Map YAML only as described in the repository's `AGENTS.md`.

### What “pinned RobotraceSim” means

The exact upstream source is vendored under `simulator/upstream/robotrace_Sim/`, with provenance in `simulator/upstream/UPSTREAM.json`. The adapter deliberately extracts the pinned native sensor-coverage and motor/drivetrain functions instead of importing the PySide6 desktop application. Rebuilding the native library from the pinned source must give the same deterministic results before a recorded run.
