# LoopSense

There are already many ways to organise agent harnesses. They can delegate work, share memory, critique outputs, call tools, and connect directly to evidence from the real world. But they still struggle with genuinely complex problems where outcomes are delayed, causes are distributed across several agents, and a human has to work out what went wrong.

We think LoopSense may offer something different. It uses the simple primitives of [Randow Maps](https://randowmaps.com/)—actors, actions, entities, and the relationships between them—to create agent topologies with explicit products, dense feedback loops, and attributable evidence. The aim is to help an agent team learn not only how to perform its work better, but eventually how to organise that work better.

This is a hypothesis, not a demonstrated result. The [LoopSense product definition](Loopsense-product-definition.md) describes the problem, proposed advantage, interaction grammar, and claims we ultimately want to test.

## Status: Robot Race concluded for now

We tested the LoopSense approach through **[Robot Race](robotrace/README.md)** — two agent teams repeatedly
designing and racing a line-following robot under the same model, token budget, simulator, and evaluation
conditions. Across ~20 pre-registered gates:

- **A lone agent beat all three two-agent structures we tested** — the original producer–integrator team,
  a conventional evaluator–optimizer pair, and a more elaborate two-round critique structure.
- **The first critique-and-revise round degraded the design 96.5% of the time**, traced to the critic
  confidently, and sometimes wrongly, asserting the current design didn't already work.
- **Giving a team explicit permission to hold its design and decline advice produced a large behavioural
  shift (3x more holding) but not yet a statistically confirmed score change.**

**Scope:** one model (Haiku 5.5), one task (this simulated line-follower), no simulator tool access for any
agent, 12 iterations per race. Nothing above has been tested outside that envelope.

Full detail: **[`robotrace/FINDINGS.md`](robotrace/FINDINGS.md)** (results table and summary) and
**[`robotrace/START_HERE.md`](robotrace/START_HERE.md)** (orientation, how to run a race, open ideas).

The open idea most worth pursuing next: **an orchestrator-style team forked from the original LoopSense
setup** below, rather than another variant of the two topologies already tested.

Robot Race's physics core is taken from [RobotraceSim](https://github.com/Koyoman/robotrace_Sim),
created by Arthur Jose Sary and distributed under the MIT License: the sensor-coverage and
motor/drivetrain functions of its native library. LoopSense's headless adapter supplies the tracks,
the parametric controller, the run loop, termination and scoring, and the experiment harness is a
separate addition. The original copyright and licence are preserved with the vendored source.

## Repo map

| Path | What's there |
|---|---|
| [`robotrace/`](robotrace/README.md) | The Robot Race experiment: harness, templates, race data, and every finding. |
| [`robotrace/FINDINGS.md`](robotrace/FINDINGS.md) | Results table and plain-language summary. |
| [`robotrace/START_HERE.md`](robotrace/START_HERE.md) | One-page orientation: headline result, how to run a race, gotchas, open ideas. |
| [`robotrace/PHASE0_FREEZE.md`](robotrace/PHASE0_FREEZE.md) | Every pre-registered decision rule, committed before the data it governs existed. |
| [`robotrace/races/`](robotrace/races/README.md) | Every race's packages, status, leaderboard, report and replay files. |
| [`loopsense/`](loopsense/README.md) | The original LoopSense experiment — set aside, kept as historical/conceptual foundation. |
| [`robotrace/earlier-conditions/`](robotrace/earlier-conditions/README.md) | Pre-map-driven-controller topology definitions, kept as historical record. |
| [`Loopsense-product-definition.md`](Loopsense-product-definition.md) | The broader hypothesis and product the experiments ultimately test. |

## The original LoopSense experiment

The [original LoopSense experiment](loopsense/README.md) explored a file-based agent team applying feedback from real-world knowledge work. It is currently set aside, but remains the conceptual and historical foundation for Robot Race.

## License

Licensed under the [Apache License 2.0](LICENSE).
