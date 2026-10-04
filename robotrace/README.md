# LoopSense Robot Race experiment

**Can the shape of an agent team change how quickly it learns?** Robot Race puts two differently organised, two-agent teams into the same measurable world and lets them repeatedly design, race, and improve a line-following robot.

Robot Race builds on [RobotraceSim](https://github.com/Koyoman/robotrace_Sim), created by Arthur Jose Sary and distributed under the MIT License. This repository vendors commit `2c99a9b63db8f9e0ef56c930cf1b360f2a1efc1c` with its original copyright and licence intact. The LoopSense experiment harness and headless adapter are separate additions.

This page serves three audiences, in order:

1. **Spectators** who want to understand the idea, watch the teams, and inspect results.
2. **The race operator** setting up a new race or returning to evidence from an existing one.
3. **Implementers** who want to reproduce, challenge, or improve the experiment.

## 1. For spectators

### Races and results

Every numbered race gets its own pair of maps and one shared leaderboard. The two maps show the same race from the perspective of the two competing team topologies; the leaderboard is the common result record.

| Race | LoopSense team | Evaluator–optimizer control | Shared leaderboard |
|---|---|---|---|
| Race 0 | **[Open the LoopSense map](https://loopsense.randowmaps.com/?map=robotrace&scenario=base&view=full)** | **[Open the control map](https://loopsense.randowmaps.com/?map=robotrace-control&scenario=base&view=full)** | Not available yet |
| Race 1 | Not published yet | Not published yet | Not available yet |
| Race 4 | **[Open the LoopSense map](https://loopsense.randowmaps.com/?map=robotrace&scenario=iteration-4&view=full)** | **[Open the control map](https://loopsense.randowmaps.com/?map=robotrace-control&scenario=iteration-4&view=full)** | **[Open the leaderboard](https://randowmaps.com/robotrace/runs/race-4/leaderboard.svg)** |

Add one row here whenever a race is published, linking its LoopSense map, control map, and shared leaderboard. Within either map, move through its numbered iteration scenarios to watch that team change over the course of the race.

### How to read the maps

The maps are the quickest way to see the experiment. They show who does what, which concrete products move forward, and how race evidence and teammate feedback travel back. Start with the Race 0 row above to understand the two designs; as later races are published, use each numbered row to compare both teams under one frozen setup and open the leaderboard beside them.

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

### What is common between the teams

Both conditions have:

- two AI agents using the same model and model settings;
- the same total token budget and visible budget ledger;
- the same starting state, design constraints, simulator, tracks, seeds, and scoring;
- exactly one selected robot package raced per condition per iteration;
- the same mechanical validation and bounded format-repair policy;
- the same objective race measurements, delivered through two independently addressed return entities;
- private role expertise plus persisted coordination state;
- no access to held-out tracks and no operational access to the aggregate Race Outcome entity;
- the same deterministic orchestrator, audit log, checkpoints, telemetry, SVGs, and leaderboard; and
- no human routing or retrospective call inside an iteration.

The orchestrator is deterministic software, not another agent. Model output is validated data and can never become executable code, a command, or a filesystem path.

### What is different

| LoopSense condition | Evaluator–optimizer control |
|---|---|
| **Geometry Builder** creates a Geometry Proposal. | **Robot Optimizer** creates a complete robot candidate. |
| **Robot Integrator** is the Builder's direct customer. It incorporates the geometry, adds the controller, and produces the Complete Robot Package. | **Evaluator** inspects the complete candidate and its rationale, then either requests a revision or passes one recorded candidate through unchanged. |
| The team advances once through a serial production spine before each race. | The pair may use multiple internal critique–revision cycles before each race while budget remains. |
| Explicit entities define the handoff, integration feedback, and addressed race-return paths. | Both agents work through a shared, unstructured blackboard containing candidate and feedback versions. |
| The agents may evolve their working agreement, but the two roles, two-agent boundary, and forward topology stay fixed in this initial experiment. | The agents may organise their blackboard work as they choose, but the optimizer–evaluator topology stays fixed. |

The independent variable is therefore the organisation of work between races: an explicit producer–customer value flow with attributable return paths versus the classic whole-solution evaluator–optimizer loop.

### How the comparison works

Each iteration starts by cloning the completed state from the previous iteration. The LoopSense team produces a geometry and then an integrated robot. The control can critique and revise complete candidates within its budget. One valid selected build from each condition then runs through an identical batch of tracks and seeds.

The harness records raw performance and learning-system measures, including:

- completion, progress, speed, centre-line error, robustness, oscillation, control effort, and failures;
- current, best-so-far, and worst-case scores;
- improvement by iteration and improvement per 10,000 tokens;
- total tokens, estimated cost, invalid artifacts, and repair calls;
- working-agreement changes and evaluator–optimizer revision cycles; and
- which measurements were requested, received, and used in later reasoning.

Development evidence is returned to the agents; held-out tracks are reserved for preregistered checkpoints and final evaluation. The exact score weights, model, budgets, geometry bounds, run length, and track sets must be frozen before a recorded run.

For the full protocol, contracts, controls, and rationale, see **[LoopSense Robot Race Experiment Design](Loopsense-Robot-Race-Experiment-Design.md)**. The implementation details and build sequence remain in the [Implementation Plan](IMPLEMENTATION_PLAN.md).

## 2. For the race operator

Use this section to see whether the experiment is ready, set up the next race, or find the maps, leaderboard, and underlying evidence from an earlier race.

### Current status

The checked-in system is a safe, deterministic **pilot harness**, not yet a completed recorded experiment. It can use either the bundled mock model or a real model through OpenRouter. RobotraceSim is pinned at commit `2c99a9b63db8f9e0ef56c930cf1b360f2a1efc1c`, its MIT license is preserved, and the headless adapter uses its portable native sensor and motor/drivetrain physics without importing the PySide6 desktop UI. Canonical packages are translated into RobotTraceSim's robot representation, every trial owns a seeded random generator, and controllers receive sensor readings and timestep only.

Smoke and pilot scores are not final experimental evidence. Before the first recorded run, freeze all preregistered settings, complete and reset disposable pilot runs, and tag the exact configuration.

### Run the offline smoke experiment

From this directory:

```sh
python3 -m orchestrator.runner
```

This validates configuration, runs two iterations for both conditions with the bundled deterministic mock model, races exactly one selected package per condition and iteration, and writes the complete spectator and audit record under `runs/robotrace-smoke/`.

Validate without running:

```sh
python3 -m orchestrator.runner --validate-only
python3 -m unittest discover -s tests -v
```

Resume an interrupted run without replaying completed calls or trials:

```sh
python3 -m orchestrator.runner --resume
```

### What a run produces

Each run contains a manifest, immutable JSONL audit log, input-context manifests, budget ledgers, hashed result records, agent entities and feedback, per-trial telemetry, trajectory SVGs, iteration summary SVGs, condition scenario maps, atomic completion checkpoints, and one shared leaderboard.

That record is intended to make a positive, negative, or ambiguous result useful: another person should be able to see what every actor received and produced, what happened on the track, which feedback was available, what changed next, and what that learning cost.

### Set up and run a race from a config file

The config-file workflow is the primary operator path. Create a fresh race definition:

```sh
cd /Users/danrandow/github/loopsense/robotrace
python3 -m orchestrator.runner --init-race race-0
```

This creates `race-definitions/race-0/config.json`. Open that file and edit the values for the race. In particular:

- set `iterations`;
- set `model.provider` to `openrouter` and `model.id` to the exact OpenRouter model slug;
- set `budget.total_tokens_per_condition`, `budget.max_tokens_per_iteration`, and `budget.max_control_cycles`;
- edit `initial_conditions.loopsense_working_agreement`;
- edit `initial_conditions.control_criteria`; and
- review the tracks, seeds, design bounds, score weights, and publication URL.

Then provide the API key without putting it in the file and start the race:

```sh
export OPENROUTER_API_KEY='your-key-here'
python3 -m orchestrator.runner \
  --config race-definitions/race-0/config.json \
  --output runs
```

The runner freezes the full config in `runs/race-0/manifest.json`, creates a fresh pair of race maps under `runs/race-0/maps/`, and runs the numbered scenarios for both teams. To run the next comparison, initialise `race-1`, edit its config, and run it the same way. Existing race definitions and outputs are never overwritten.

### Optional local setup interface

If you prefer a form instead of editing JSON, start the local interface:

```sh
cd /Users/danrandow/github/loopsense/robotrace
python3 -m orchestrator.web
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765). The interface is deliberately local-only so an API key is not exposed on the network.

The setup page lets you choose:

- the next race number;
- iterations per team;
- OpenRouter or the deterministic offline mock;
- the exact OpenRouter model slug;
- total token budget per team, per-iteration budget, and maximum output tokens;
- the LoopSense team's starter Working Agreement; and
- the optimizer/evaluator team's initial evaluation criteria.

Press **Start race** once. The same model, model settings, total budget, tracks, seeds, simulator, and scoring are applied to both teams. The page links to the leaderboard and manifest when the race completes. Completed races also remain listed on the setup page.

Stop the interface with `Control-C` in the terminal.

### Use OpenRouter

Create an API key in OpenRouter and choose an exact model slug from [OpenRouter's model catalogue](https://openrouter.ai/models). The model is a race parameter: changing it means starting a new race, not changing an active one.

You can paste the key into the setup page. It is held only in the server process and is never written to a config, manifest, audit log, or Git. Alternatively, set it before starting the interface:

```sh
export OPENROUTER_API_KEY='your-key-here'
python3 -m orchestrator.web
```

Do not put a real key in `config/experiment.yaml` or commit it. `.env.example` documents the variable name; `.env` files are ignored by Git.

The OpenRouter adapter is already implemented. It calls the official chat-completions endpoint, requires JSON-only actor artifacts, records the provider request identifier and token use, and applies the same validation and budgets to both conditions. OpenRouter documents the endpoint and authentication in its [quickstart](https://openrouter.ai/docs/quickstart).

### Initial conditions and editable files

The setup page is the operator-facing source for each new race's mutable initial conditions. When a race starts, it saves a frozen copy under `race-definitions/race-N/config.json`; generated evidence goes under `runs/race-N/`. Both directories are local run state and ignored by Git.

Checked-in defaults live in:

- `config/experiment.yaml` — model defaults, budgets, tracks, seeds, design bounds, score weights, and initial-condition text;
- `conditions/loopsense/working-agreement-v0.md` — readable source version of the LoopSense starter agreement;
- `conditions/control/working-agreement-v0.md` — readable source version of the control team's minimal criteria;
- `conditions/*/private/` — actor-specific starting expertise;
- `tracks/` — anchor, development, and held-out track definitions; and
- `config/*.schema.json` — artifact contracts.

The web form overrides the two initial-condition texts and common budget/model fields for that race. Edit the checked-in configuration directly only when deliberately changing the experiment design for future races.

### Race, map, and iteration numbering

A **race** is one complete comparison between both teams under one frozen configuration. Each race owns a new pair of maps:

```text
runs/race-0/
  maps/
    loopsense/
      base.yaml
      iteration-0.yaml
      iteration-1.yaml
    control/
      base.yaml
      iteration-0.yaml
      iteration-1.yaml
  loopsense/iteration-0/ ...
  control/iteration-0/ ...
  leaderboard.json
  leaderboard.md
  leaderboard.svg

runs/race-1/
  maps/loopsense/ ...
  maps/control/ ...
  ...
```

In human terms these are race/iteration pairs such as `0.0`, `0.1`, `1.0`, and `1.1`. On disk they remain explicit names such as `race-0/maps/loopsense/iteration-1.yaml`, avoiding ambiguous decimal filenames. The two checked-in `base.yaml` files are templates; every race receives frozen copies that can carry race-specific starting conditions without changing earlier maps.

Each completed iteration supplies the starting evidence for the next iteration in the same race. A later race starts from its own setup form and configuration; it does not silently inherit an earlier race unless you deliberately copy those settings into the new form.

### Find the leaderboard and evidence

While the local interface is running, its **Previous races** table links to every race leaderboard. On disk, open:

- `runs/race-N/leaderboard.svg` for the visual leaderboard;
- `runs/race-N/leaderboard.md` for the table;
- `runs/race-N/manifest.json` for the frozen configuration and result hashes;
- `runs/race-N/maps/` for both map/scenario sets; and
- `runs/race-N/<condition>/iteration-N/entity2/iteration-summary.svg` for one iteration's trajectories and score.

After publishing a completed race to Randow Maps, add it to the **Races and results** table at the top of this page. Each row must point to that race's LoopSense map, control map, and shared leaderboard; do not repoint an older row to a newer race.

The old `runs/robotrace-smoke/` output is a disposable harness check, not race 0 and not evidence.

### Resume and troubleshoot

The interface prevents reusing a race ID. If a machine interruption leaves a race incomplete, resume from the terminal with its saved definition:

```sh
python3 -m orchestrator.runner \
  --config race-definitions/race-0/config.json \
  --output runs \
  --resume
```

Completed checkpoints are not replayed. If OpenRouter rejects a model name, choose a current exact slug from its catalogue and start a fresh race definition. If an agent returns malformed JSON or violates a schema, the run stops with the validation error rather than silently racing an invalid or changed design.

## 3. For implementers

Start with the **[LoopSense Robot Race Experiment Design](Loopsense-Robot-Race-Experiment-Design.md)** for the research question, independent variable, common controls, lifecycle, measures, and interpretation. Then use the [Implementation Plan](IMPLEMENTATION_PLAN.md) for the detailed artifact contracts, simulator boundary, orchestration rules, build phases, tests, and recorded-run gate. The broader product hypothesis is in the [LoopSense product definition](../Loopsense-product-definition.md).

The key implementation constraint is separation of responsibilities: the agents produce constrained data; a deterministic orchestrator validates and routes it; and a fixed simulator produces the evidence. Both conditions share the same infrastructure. Condition-specific workflow definitions should express the topology difference without quietly changing models, budgets, world evidence, validation, or scoring.

Useful places to begin:

- `config/experiment.yaml` and `config/*.schema.json` define the common experiment and artifact boundaries;
- `orchestrator/` contains the shared runner, condition workflows, model adapter, audit trail, and local setup interface;
- `conditions/` contains the starting coordination material and private role expertise;
- `tracks/` contains anchor, development, and held-out track definitions;
- `simulator/` contains the safe headless boundary and pinned upstream simulator source; and
- `tests/` checks fairness, determinism, isolation, validation, resumption, and artifact generation.

Run the validation and test commands in the operator section before changing the experiment. A substantive change to topology, evidence, budgets, scoring, tracks, or agent permissions creates a new experimental design or run configuration and must not silently alter an active race.

### What “pinned RobotraceSim” means

The exact upstream source is vendored under `simulator/upstream/robotrace_Sim/`, with provenance in `simulator/upstream/UPSTREAM.json`. Rebuild its native C helper with:

```sh
python3 simulator/native/build.py
```

No operator action is needed to pin it again. The adapter deliberately extracts the pinned native sensor-coverage and motor/drivetrain functions instead of importing the PySide6 desktop application. Rebuilding the native library from the pinned source must produce the same deterministic test results before a recorded run.
