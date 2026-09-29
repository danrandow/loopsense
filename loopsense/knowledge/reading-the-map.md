---
name: reading-the-map
description: How to read base.yaml and the scenario files (iteration-*.yaml, moonshot.yaml) as an agent, and what you may write. Read before acting.
sources:
  - cowork
last_updated: 2026-09-25
---

# Reading the Map

The map (base.yaml) is the canonical topology. Scenario files inherit from it: `iteration-*.yaml`
(one per iteration) and `moonshot.yaml` (the long-horizon target).

## Who writes what
- `base.yaml`: read-only for agents. Never edit it.
- `moonshot.yaml`: Dan and Loopy only.
- `iteration-*.yaml`: the only map files agents write to. Follow the detail hierarchy in
  standing-rules.md (label = headline, notes = short summary, full content in your `generates/` file).
- If base.yaml or moonshot.yaml looks wrong, flag it in your output for Dan (Loopy).

## Labels
Actor and action labels are terse summaries of no more than 25 characters or 3-4 words, whichever
is shorter. This is a hard limit: the renderer clips anything longer. Entity labels may run longer,
up to about 50 characters. Put the explanation in `notes` and the detail in your `generates/` file.
A label that contains a colon must be wrapped in double quotes, or the YAML fails to parse.

## Parts
- actors: the roles. actorN performs actionN.
- entities: the things passed around. `direction: return` means it flows back upstream.
  system_boundary is internal, private (one actor's own knowledge) or public (the environment).
- edges: `generates` (action -> entity) and `used by` (entity -> action). An actor's inputs are
  its `used by` edges, its outputs its `generates` edges. team-registry.md tabulates this per role.

## Flows
- Spine (entity0..4): the forward chain. Each actor reads the upstream spine entity.
- Return flows (entityR1..R4, R4A..R4C, R2A, R3A, R3B): signal flowing back upstream.
  The ones that skip the PM (R2A, R3A, R3B, R4B, R4C) are the same kind of flow, just multi-hop.
  They matter a great deal: they are feedback packaged for the specific actor who will use it,
  in the form that actor can act on. Write them for that reader.

## Iteration
An iteration starts at actor0 (PM), who acts on all return flows plus the environment. For now it
is complete when GTM (actor3) has returned its market signal (entityR3) to the PM. GTM is
responsible for finding the practitioner signal. Later, practitioner signal will be measured and
monitored independently, and the iteration definition will change then.

## Scenario files
`inherits: base.yaml` means take everything from base.yaml. `overrides` changes only what is listed.
A scenario is one run or one target state, kept so runs can be compared.

## Naming
An entity's full content is written to `agents/{yourid}/generates/{entityId}-v{n}.md`
(e.g. entityR3 -> agents/gtm/generates/entityR3-v0.md). Paths are in team-registry.md.

## Consideration
Consideration is a practice you perform, not a schema element in the map. Before you act, read your
receiver's knowledge and the signals they will use, and step into their world first. It is the
topology's core mechanism (see dna.md).
