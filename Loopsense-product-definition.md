# Loopsense: Product Definition

## At a glance

### The problem

AI agents can perform tasks, exchange messages and coordinate through predefined workflows, but they struggle to learn how their combined work produced an outcome. As work becomes more complex, feedback becomes separated from its causes. It becomes difficult to determine whether a result arose from how an agent performed, the entities it received, the way responsibilities were divided, or the topology of the work itself.

Improving individual agents is not enough when the organisation connecting them is the problem. Yet redesigning that organisation usually remains a human responsibility.

### The proposed advantage

**Loopsense sets out to help autonomous groups of AI agents learn from the consequences of their collective work and improve both how they perform and how they organise themselves.**

It is intended to help agent systems:

- adapt faster after failures or environmental change;
- perform better on complex, interdependent work;
- deliver relevant feedback without exposing every agent to all available context;
- reduce the human effort required to diagnose recurring problems; and
- recognise when their current organisation is inadequate and generate a better one.

These advantages are hypotheses. They have not yet been demonstrated experimentally.

### How Loopsense works

Loopsense provides a minimal interaction grammar derived from Randow Maps. The grammar is fixed; the way work is performed, the roles agents assume and the topology they form can evolve.

A map contains three nouns:

- **Actor**
- **Action**
- **Entity**

And two verbs:

- An actor **performs** an action and thereby **generates** one or more entities.
- An actor performing an action may **use** one or more entities.

From these primitives, agents can form chains, teams, networks, hierarchies, parallel structures, feedback loops and new forms of organisation. They can continually improve how they perform their actions and, when local improvement is insufficient, create and test a successor topology.

## The problem in detail

### Outcomes are separated from their causes

In complex work, the consequence of an early action may appear only after several other actors and actions have transformed its output. A final score, critic response or user outcome may reveal that something went wrong without revealing where or why.

The system must distinguish among several possibilities:

- an actor performed an action poorly;
- an action used an incomplete, incorrect or unsuitable entity;
- a necessary entity was unavailable;
- an entity was visible to the wrong actors or hidden from the right ones;
- feedback arrived too late or was not used;
- responsibilities were assigned poorly; or
- the topology itself was inappropriate for the problem.

Without an attributable path through the work, systems tend to compensate for symptoms, repeat failures or depend on people to diagnose the organisation for them.

### More shared context is not necessarily better context

A universal shared history makes information available, but it also increases context cost and exposes actors to material irrelevant to their actions. Important evidence may be present without being usable by the actor capable of improving the outcome.

The challenge is to achieve high feedback density without requiring high context density.

### Fixed workflows limit learning

Many systems respond to poor performance by revising prompts, retrying actions or replacing a model. These interventions assume that the current division and flow of work are sound.

Some failures are structural. An action may need to be divided, responsibilities may need to move between actors, a feedback entity may need a new route, or a sequential topology may need to become parallel or recursive. Improving performance inside a flawed topology may make a system more efficient at doing the wrong work.

### Human diagnosis limits autonomy

When people must repeatedly trace failures across agents, identify missing information and redesign workflows, the system automates execution while leaving organisational learning to its operators.

A more autonomous system must be able to learn not only how to act inside an organisation, but also when and how that organisation should change.

## The advantages Loopsense sets out to offer

### Faster adaptation

Loopsense aims to preserve the relationship between an entity, how it was used and the later entities and consequences that followed. Relevant feedback can then reach the actors and actions capable of learning from it.

This may allow a Loopsense system to improve or recover in fewer cycles after failure or change. The expected advantage is most visible across repeated attempts: Loopsense may not produce the best first result, but it should learn more efficiently from what happens next.

### Better performance on complex, interdependent work

Loopsense may be valuable where:

- later work depends strongly on entities generated earlier;
- failures emerge several transformations after their causes;
- multiple kinds of capability are required;
- the environment changes over time; and
- repeated action produces observable feedback.

It is not expected to offer the same advantage for one-shot questions, simple tasks or work that can be divided into genuinely independent subtasks.

### Relevant feedback with controlled context

Actors do not need access to every entity in a map. They can use:

- entities received through the main flow of work;
- feedback entities generated downstream;
- private entities available only to themselves;
- public entities available across the map; and
- other entities made visible because they are relevant to the action being performed.

This may provide more attributable feedback per unit of context, computation and human attention. The goal is not minimal communication. It is useful communication with intentional visibility.

### Adaptation of roles and relationships

Actors may improve the way work is divided and connected. They may change:

- which actors perform which actions;
- how an action is performed;
- which entities an action uses;
- which entities an action generates;
- the form or timing of an entity;
- whether an entity is private or public; and
- where feedback is generated and used.

These changes may emerge through local learning, negotiation between actors or a broader governance process. Loopsense does not require one prescribed coordination mechanism.

### Evolution of the topology

When local improvements are insufficient, the system may conclude that the current map is wrong. It can generate a successor map with a different arrangement of actors, actions, entities, performance relationships and use relationships.

Candidate maps can be versioned, tested, compared and rejected or adopted. The system can retain the evidence and rationale connecting one organisational design to the next.

### Reduced dependence on human diagnosis

Given reliable environmental feedback, bounded authority and reversible experimentation, Loopsense may progressively increase the amount and complexity of useful work completed between human interventions.

This is not a claim that Loopsense should operate without human involvement in every domain. Safe autonomy also depends on the quality of environmental signals, the consequences of experimentation, recovery mechanisms and the human values that must be preserved.

## The Randow Map interaction grammar

### Actor

An actor is a participant capable of performing an action. In Loopsense, an actor will commonly be an AI agent, but the grammar can also represent people, groups, organisations or other acting systems.

### Action

An action is something an actor performs. It transforms the situation by using zero or more entities and generating one or more entities.

How an actor performs an action is not fixed by the map. The actor can change its method in response to the entities it receives, its private learning and feedback from elsewhere in the topology.

### Entity

An entity is something an action can use or generate. It may be information, a decision, a plan, an artefact, a request, a commitment, an observation, feedback, software, a physical result or another map.

An entity may be:

- part of the main spine of work;
- feedback moving upstream or across the map;
- private to an actor;
- public to the map; or
- selectively available to particular actors or actions.

### Performs and generates

When an actor performs an action, the action generates one or more entities.

```text
Actor → performs Action → generates Entity
```

### Performs and uses

When an actor performs an action, the action may use one or more entities.

```text
Entity → used in Action ← performed by Actor
```

Together, these relationships describe a topology of work:

```text
Actor A performs Action 1
    → generates Entity X

Actor B performs Action 2
    → uses Entity X
    → generates Entity Y

Actor C performs Action 3
    → uses Entity Y
    → generates Entity Z
```

The same primitives can express branching, convergence, parallelism, recursion, private working state, public knowledge and feedback loops.

## Emergent concepts, not additional primitives

Loopsense can describe familiar organisational concepts without making them part of its basic ontology:

- A **product** is an entity generated by one action and used by another.
- A **customer** is an actor performing an action that uses an entity generated upstream.
- A **producer** is an actor whose action generates that entity.
- A **role** is the current association between an actor and the actions it performs.
- A **handoff** occurs when a generated entity becomes available for another action to use.
- **Context** is the collection of entities available to an actor while performing an action.
- **Feedback** is an entity generated in response to use or consequence and used by another action, often upstream.
- A **consequence** is an entity or change generated downstream from prior actions.
- A **topology** is an arrangement of actors, actions, entities, performance relationships and use relationships.

These concepts remain important, but they are constructed from the grammar rather than added as new primitive types.

## How self-organisation occurs

### 1. Learning within an action

The initial and most frequent form of self-organisation occurs when an actor improves how it performs its current action.

The topology may remain unchanged while the actor learns from:

- entities received from upstream;
- private entities representing memory or prior experience;
- public entities available in the map;
- feedback generated by downstream actors; and
- observed consequences of previously generated entities.

The basic learning loop is:

```text
use entities
→ perform action
→ generate entities
→ receive feedback
→ change future performance
```

### 2. Adaptation of roles and relationships

Actors may alter which actions they perform or how their actions relate to the rest of the map. This can involve local optimisation, negotiation between actors or collective agreement.

Loopsense permits these governance forms but does not prescribe one. Its requirement is that the resulting work can still be expressed and inspected through the interaction grammar.

### 3. Evolution of the map

The system may determine that local learning cannot adequately improve the outcome because the existing topology is unsuitable.

Actors can then perform actions that generate a candidate map. That map can be used by later actions to instantiate, test and evaluate a new organisation.

```text
Map v1 generates outcomes and evidence
→ actors evaluate Map v1
→ an action generates candidate Map v2
→ actors use Map v2 to organise new work
→ outcomes are compared
```

This makes the grammar recursive: a Randow Map can contain actors performing actions that generate and use Randow Maps.

## What differentiates Loopsense

Many multi-agent systems can delegate tasks, share memory, critique outputs, route messages or optimise a workflow. Individual Loopsense mechanisms are not necessarily unprecedented.

Loopsense's distinctive proposition is the combination of:

- a minimal grammar rather than a prescribed organisational topology;
- explicit relationships between entities, their generation and their use;
- feedback represented within the same grammar as the work itself;
- intentional public, private and selective entity visibility;
- continual learning inside each actor's performance;
- adaptation of roles and relationships; and
- recursive, versioned evolution of the topology itself.

Loopsense prescribes the language through which organisation is made inspectable while leaving the organisation open to evolution.

> **The interaction grammar is fixed; performance, roles and topology can evolve.**

## Testable hypotheses

### Primary hypothesis: adaptation efficiency

> **For complex, repeated tasks with delayed and interdependent outcomes, an agent system organised through the Loopsense interaction grammar will improve outcome quality faster—and with less shared context and human correction—than comparable single-agent, centrally orchestrated and shared-context multi-agent systems.**

This predicts:

1. Better eventual outcomes
2. Fewer cycles required to improve or recover after change
3. Less context and computational cost for a given outcome
4. Fewer human corrective interventions

### Secondary hypothesis: topology evolution

> **When performance failures arise from the organisation of work rather than an individual actor's execution, a Loopsense system allowed to generate and test successor maps will recover faster and reach better outcomes than a system limited to improving agents or actions within a fixed topology.**

Both hypotheses are untested. They state what Loopsense is intended to achieve and provide criteria by which its proposed advantages can be supported, refined or rejected.

## What Loopsense is not

Loopsense is not inherently:

- a group chat involving several AI personas;
- a supervisor delegating independent subtasks to workers;
- a fixed sequence of prompts;
- a generator–critic loop;
- a universally shared blackboard;
- a particular network shape; or
- a graph optimiser seeking only to maximise a final benchmark score.

Any of these patterns could be expressed in a Randow Map. None defines Loopsense.

## Product promise

> **Loopsense helps autonomous groups of agents improve both the work and the way the work is organised.**

It does this by giving agents a simple, inspectable grammar through which they can act, exchange entities, learn from consequences and generate better arrangements of work.

This promise remains provisional until comparative experiments demonstrate that Loopsense improves adaptation, outcome quality, context efficiency or human-effort requirements against credible alternatives.

## Internal design test

A capability belongs at the centre of Loopsense when it strengthens one or more of the following:

1. Actors, actions and entities remain sufficient to describe the work.
2. Generated entities and their subsequent use are traceable.
3. Actors receive relevant evidence about downstream consequences.
4. Feedback is useful without requiring universal context exposure.
5. Actors can improve how they perform actions.
6. Roles and relationships can adapt without making the system illegible.
7. The system can identify limitations in its current map.
8. Candidate maps can be generated, tested, compared and traced over time.

If a feature adds agent activity without improving action, entity flow, feedback, learning or organisational evolution, it is peripheral to the Loopsense proposition.
