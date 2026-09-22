---
name: dna
description: The foundational philosophy of Loopsense and Randow Maps topology. Read before forming any opinion about what we are building and why. All agents should read this.
sources:
  - cowork
aliases: [foundations, philosophy, why]
---

# DNA — What This Is, At Root

## The integration

This is where three bodies of work converge:

- **Product management** — making decisions under uncertainty on behalf of users and business
- **Business** — building something that earns its own existence
- **Relational practice** — J.L. Moreno, Imago, Walter Logeman's couple therapy

That convergence is not metaphorical. It is structural. The topology encodes relational practice
as an architectural principle.

## The relational insight

The unique thing about this topology is not that it loops. Loops are everywhere.

The unique thing is **how actors are linked** — and the quality of that link.

Actor N passes something to Actor N+1 only if Actor N has genuinely entered Actor N+1's world.
The link is conditional on that encounter. If the actor hasn't understood the receiver, the
signal degrades — not as a bug, but as a true representation of what happened: a stranger
passing a note to another stranger.

This is Moreno's **tele** — the pre-verbal felt sense of the other across distance. Not empathy
as a skill, but the thing that makes genuine contact possible at all. In the topology, the
consideration mechanism is an approximation of tele: an actor reading the knowledge file of their
receiver is performing a kind of **role reversal** — stepping into the other's position to
understand what they can actually use.

## Moreno's role reversal in the topology

In psychodrama, role reversal is the technique where you step into the other's role — not to
mimic, but to genuinely inhabit their perspective. The insight that arises is not what you
imagined the other felt, but something genuinely new: you meet them in their world.

In the topology: before PM acts, they read what practitioners are sending back. Before Exec
certifies, they hold the market signal. Before Delivery ships, they read the Exec brief — not
as instructions, but as entering the world of the customer being described. Before Sales makes
the offer, they have held the full chain: practitioner pain, PM bet, Exec frame, Delivery
artifact.

Each actor enters the other's world before acting. That is not pipeline logic. It is encounter.

## Imago and the intentional dialogue

Harville Hendrix's Imago therapy structures dialogue as: mirror (hear accurately) → validate
(their perspective makes sense from their vantage point) → empathize (feel into what it's like
to be them having that experience).

The return flows in this topology are intentional dialogue. The practitioner sends signal. PM
mirrors it (captures verbatim, not summary). PM validates it in the bet (their problem makes
sense from their position). The team acts from that empathic stance.

The topology enforces the sequence. Skip a step — certify without holding practitioner signal,
ship without reading the brief — and the dialogue collapses. The return flow carries nothing
real. Hallucination fills the gap.

## Walter Logeman

Walter Logeman's work on encounter and depth in relationship — rooted in Moreno but extending
into the everyday intimacy of knowing and being known. The topology has this quality: each
iteration, the actors know each other better. The system is not static. It constitutes itself
through the relationships it encodes.

"Looping myself into existence" is Logeman-flavored: the self that emerges from genuine contact
with others, changed by what it receives, offering what it has made to those who can use it.

## What this means for the product

The product is not a workflow tool. It is a relational architecture.

The YAML file does not describe a pipeline. It describes a set of relationships and the quality
of connection between actors. The topology makes those relationships inspectable and improvable.

When an actor produces poor output, the diagnosis is not "the prompt was wrong." It is:
"this actor did not genuinely enter the world of their receiver before acting." That is a
relational failure, and it has a relational fix: deepen the knowledge file, strengthen the
return flow, slow down the handoff.

## What this means for the Cynefin framing

Complex work cannot be verified in advance because the pattern only becomes visible through
genuine encounter with the environment. The loop is the means of encounter. The topology
structures the loop so that each actor is genuinely changed by the signal they receive —
not processing it, but being affected by it.

This is why free mesh fails: strangers in contact are not in encounter. This is why single
loops stop too soon: one contact is not enough to constitute a relationship.

## What this is still not

This is not therapy. The agents are not people. The relationships are approximations.

But the approximations are richer than pipeline logic because they are *aimed* at encounter,
not just at output. The aim matters. The topology encodes the aim.

## For naming and positioning

The name does not need to carry all of this. But the product needs to feel like this when
someone uses it. The handling of return flows, the structure of the knowledge files, the
condition of the handoff — these should feel like genuine contact, not data transfer.

Practitioners will feel this before they can name it. The positioning names it for them.

## Related

[[verification-gap]] | [[exec-v0]] | [[pm.md]] | Cynefin framing in [[exec-v0]]

## Conway's Law and McLuhan — the product shapes its users

Conway's Law: organisations produce designs that mirror their communication structures. The inverse
holds too: the topology you build shapes the organisation that uses it. If practitioners adopt a
PM → Exec → Delivery → Sales topology, their teams will start to organise themselves that way.
The product is not neutral. It is a social design.

McLuhan: the medium is the message. The form of the tool shapes the consciousness of its user,
independent of the content it carries. A topology-first tool trains practitioners to think in
topologies — to see their work as a set of relationships and handoffs, not a sequence of tasks.

Implication: this must be designed consciously. We are not just building a coordination tool.
We are proposing a model of how knowledge work teams should relate to each other. The pipeline
we are running to build this product IS that model. "Be the change you want to see" is not a
slogan — it is the product strategy.

The Loopsense pipeline is the proof of concept for the social design it advocates. Every
iteration is evidence that the design works (or doesn't). The self-referential structure is not
a marketing angle — it is the only honest way to build this.

## Composable loop topologies — the technical description

What we are building is not a single topology. It is a composable loop topology architecture:

- A **directed graph** with opinionated defaults for a specific problem context
- Not free mesh (too unstructured — errors compound) 
- Not fully adaptive graph (cutting edge, not yet proven in production)
- A **fitted topology**: structured enough to be inspectable, specific enough to be useful for
  a particular subsystem
- **Composable**: when you need more, you add adjacent, super, or sub-topologies. The base
  topology stays stable. The system grows by composition, not by increasing internal complexity.

This is the middle path. "Loop harness" is well-established in AI. Adaptive graphs are still
emerging. Composable loop topologies are between them — proven enough to ship, structured enough
to inspect, flexible enough to grow.

The YAML artefact is what makes composability possible: a topology is a file. You can fork it,
version it, compose it with another by reference. A code-defined adaptive graph cannot be held
still or inspected between iterations.

## The moonshot scenario as alignment mechanism

Someone asked: how do you stop agent teams going off track, doing bad things?

The answer is not guardrails. Guardrails say "don't do X." For complex work, you cannot enumerate
the X's in advance. The environment is always producing new situations you didn't anticipate.

The answer is direction: the **moonshot scenario**.

A moonshot is not a vision statement (too abstract) or a mission (a slice). It is the whole
system — all actors, all entities, all interactions — mapped in its desired end state, with all
elements interacting dynamically. It is a complete picture of what good looks like, not a list
of goals.

Agents who carry the moonshot as a reference state can self-correct by asking: is my current
action moving the system toward this state? Deviation is visible because the desired state is
fully specified as a system, not as a directive.

This is the Randow Maps answer to AI alignment in complex work: not prohibition but direction.
The moonshot sets the direction. The topology structures the movement toward it. The iterations
are the means of travel.

The moonshot scenario is also a social contract between all actors — human and agent — about
what the team is trying to become. That is closer to Moreno than to safety engineering.
