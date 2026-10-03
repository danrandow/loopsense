# LoopSense

There are already many ways to organise agent harnesses. They can delegate work, share memory, critique outputs, call tools, and connect directly to evidence from the real world. But they still struggle with genuinely complex problems where outcomes are delayed, causes are distributed across several agents, and a human has to work out what went wrong.

We think LoopSense may offer something different. It uses the simple primitives of [Randow Maps](https://randowmaps.com/)—actors, actions, entities, and the relationships between them—to create agent topologies with explicit products, dense feedback loops, and attributable evidence. The aim is to help an agent team learn not only how to perform its work better, but eventually how to organise that work better.

This is a hypothesis, not a demonstrated result. The [LoopSense product definition](Loopsense-product-definition.md) describes the problem, proposed advantage, interaction grammar, and claims we ultimately want to test.

## The current experiment: Robot Race

We are testing the LoopSense approach through **[Robot Race](robotrace/README.md)**. Two agent teams repeatedly design and test a line-following robot under the same model, token budget, simulator, starting state, and evaluation conditions:

- a **LoopSense producer–integrator team**, connected by explicit products and addressed feedback loops; and
- a conventional **evaluator–optimizer team**, working through iterative critique and revision on a shared blackboard.

Robot Race asks whether those different ways of organising the same underlying capabilities produce different adaptation trajectories. It creates a bounded environment where every input, design, race, measurement, feedback item, token, and change can be inspected.

Start with the [Robot Race overview and live maps](robotrace/README.md).

Robot Race builds on [RobotraceSim](https://github.com/Koyoman/robotrace_Sim),
created by Arthur Jose Sary and distributed under the MIT License. The original
copyright and licence are preserved with the vendored source; LoopSense's
experiment harness and headless adapter are separate additions.

## The original LoopSense experiment

The [original LoopSense experiment](loopsense/README.md) explored a file-based agent team applying feedback from real-world knowledge work. It is currently set aside, but remains the conceptual and historical foundation for Robot Race.

## License

Licensed under the [Apache License 2.0](LICENSE).
