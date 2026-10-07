# Architecture

LoopSense has two layers. The **map** is the declarative topology in YAML. The **file system** is
where each entity's content actually lives. This doc covers both, and the conventions that
connect them.

## 1. Repository layout

```
loopsense/                          <- repo root: repository-facing files only
|-- README.md                          product story + replication guide
|-- PUBLIC_EXTRACTION.md               provenance of this standalone repo
|-- LICENSE                            Apache-2.0
|-- docs/                              these developer docs
`-- loopsense/                      <- SOURCE ROOT. Every path in skills/rules is relative to here
    |-- base.yaml                      canonical topology            [owner/Loopy only]
    |-- iteration-N.yaml               one scenario per iteration    [agents: own entries only]
    |-- moonshot.yaml                  long-horizon target scenario  [owner/Loopy only]
    |-- landing-page-v0.mdx            early landing page draft
    |-- agents/
    |   |-- pm/ exec/ delivery/ gtm/   one folder per map role
    |   |   |-- SKILL.md               role, read order, write boundary, triggers
    |   |   |-- project-instructions.md  short stub pasted into a chat project
    |   |   |-- knowledge/             running knowledge (= the role's Prv entity)
    |   |   |-- generates/             entity files: <entityId>-v<N>.md, retro-iterationN.md
    |   |   `-- research/              Pub-style research notes
    |   |-- loopy/                     owner's assistant (outside the map)
    |   |   |-- knowledge/working-context.md
    |   |   `-- returns/               briefings, retro syntheses, harness proposals
    |   `-- practitioners/             (not created yet) customer-side R4* flows
    |-- knowledge/                     team-wide rules and reference
    |   |-- standing-rules.md          READ FIRST, every session
    |   |-- team-registry.md           who generates/consumes what + entity paths
    |   |-- reading-the-map.md         how to read the YAML; label limits
    |   |-- audit-policy.md            git-native audit + publish procedure
    |   |-- dna.md                     design philosophy
    |   |-- social-agent-publishing-standard.md
    |   `-- research/                  stable, sourced findings
    |-- decisions/                     YYYY-MM-DD-slug.md decision records
    |-- workflows/                     retro.md, start-next-iteration.md
    |-- openclaw/                      runtime adapter (see runtime.md)
    |-- history/  loopsense.log.json   FROZEN legacy ledger. Never edit, never treat as current.
```

## 2. The topology

Five actors, each with exactly one action. Generated from `base.yaml` edges:

```
     PM           Exec        Delivery         GTM      Practitioners
  (actor0)      (actor1)      (actor2)      (actor3)      (actor4)
      |             |             |             |             |
      |-- entity0 ->|             |             |             |     SPINE (forward work)
      |             |-- entity1 ->|             |             |
      |             |             |-- entity2 ->|             |
      |             |             |             |-- entity3 ->|
      |             |             |             |             |     entity4 --> the world
      |             |             |             |             |
      |<--- R1 -----|             |             |             |     SPINE RETURNS
      |<---------- R2 ------------|             |             |     (all land on PM)
      |<----------------- R3 -------------------|             |
      |<------------------------ R4 --------------------------|
      |             |             |             |             |
      |             |<--- R2A ----|             |             |     BYPASSES
      |             |             |<--- R3A ----|             |     (skip PM, go straight
      |             |<---------- R3B -----------|             |      to the actor who can
      |             |<----------------- R4A ------------------|      use the signal)
      |             |             |             |<--- R4B ----|
      |             |             |<---------- R4C -----------|
      |             |             |             |             |
```

Each role applies one lens. PM integrates the three.

```
                 +----------------------------+
                 |  PM  - holds the BET       |   authority over nobody;
                 |  "why are we still doing   |   wins commitment through
                 |   this?"                   |   quality of synthesis
                 +-------------+--------------+
                               |
        +----------------------+----------------------+
        |                      |                      |
 +------+-------+      +-------+------+      +--------+-------+
 | Exec         |      | Delivery     |      | GTM            |
 | VIABILITY    |      | FEASIBILITY  |      | DESIRABILITY   |
 | fundable?    |      | buildable?   |      | wanted? listen |
 | certify or   |      | build the    |      | before you     |
 | return       |      | artifact     |      | broadcast      |
 +--------------+      +--------------+      +----------------+
```

### Environment bands

Besides the spine and returns, each action reads a **private** band (its own accumulated
judgment) and sometimes the **public** band.

```
   entityPrv0 PM Judgment ........... <-> action0 (PM)        used AND generated (edgePrv0AG)
   entityPrv1 Business Model Thesis . --> action1 (Exec)      used; the map has no generates
   entityPrv2 Technical Capability .. --> action2 (Delivery)  edge yet, though each role does
   entityPrv3 Community Map ......... --> action3 (GTM)       update its knowledge file

   entityPub0 Agent Frameworks Research ---> action1 (Exec)
   (competitors, literature)            ---> action3 (GTM)
                                        ---> action4 (Practitioners compare alternatives)
```

## 3. Entity catalogue

| Entity | Label | From -> To | Kind |
|---|---|---|---|
| entity0 | Aligned Bet | PM -> Exec | spine |
| entity1 | Validated Bet | Exec -> Delivery | spine |
| entity2 | Product | Delivery -> GTM | spine |
| entity3 | Market Offer | GTM -> Practitioners | spine |
| entity4 | Practitioner Response | Practitioners -> world | spine |
| entityR1 | Viability Signal | Exec -> PM | return |
| entityR2 | Delivery Reality | Delivery -> PM | return |
| entityR3 | Market Signal | GTM -> PM | return (ends the iteration) |
| entityR4 | Usage & Feedback | Practitioners -> PM | return |
| entityR4A | Revenue | Practitioners -> Exec | return |
| entityR2A | Cost & Risk Case | Delivery -> Exec | bypass |
| entityR3A | Field Requests | GTM -> Delivery | bypass (bet-drift risk) |
| entityR3B | Pipeline & Forecast | GTM -> Exec | bypass |
| entityR4B | Demand & Objections | Practitioners -> GTM | bypass |
| entityR4C | Usage & Defects | Practitioners -> Delivery | bypass |
| entityPrv0..3 | per-role judgment | own knowledge -> own action | private |
| entityPub0 | Agent Frameworks Research | world -> Exec, GTM, Practitioners | public |

`base.yaml` is the source of truth for entity descriptions. `knowledge/team-registry.md` is the
source of truth for file paths. Do not duplicate either one; link to them.

## 4. Map data model

```yaml
map:        { schema: "v0.2", id, title, scenario, notes, iteration_definition, dimension_axes }
actors:     [ { id: actorN,  label, notes } ]                 # label <= 25 chars / 3-4 words
actions:    [ { id: actionN, actor: actorN, label, notes } ]  # label <= 25 chars / 3-4 words
entities:   [ { id, label, notes, direction?: return,          # label <= ~50 chars
                system_boundary?: internal|private|public } ]
edges:      [ { id, type: generates|used by, from, to,
                direction?: return, notes? } ]
```

- `generates` edges go action -> entity. `used by` edges go entity -> action.
- An actor's **inputs** are its `used by` edges and its **outputs** are its `generates` edges.
- A label containing `:` **must be double-quoted** or the YAML will not parse.
- The renderer clips actor and action labels longer than 25 characters. Put the detail in
  `notes`.

### Scenario inheritance

```
                        base.yaml
               (canonical topology; agents never edit)
                            |
          inherits: base.yaml  +  overrides: { actors: [...], entities: [...] }
                            |
     +----------------+-----+----------+-----------------+
     |                |                |                 |
iteration-0.yaml iteration-1.yaml iteration-2.yaml  moonshot.yaml
   (closed)         (closed)        (OPEN)          (2028+ north star)
```

A scenario only lists what differs from the base. In an iteration file each entity override
follows a strict **detail hierarchy**:

```
  label   ->  one-line headline                         (in iteration-N.yaml)
  notes   ->  short summary ending "Full entity: <path>" (in iteration-N.yaml)
  file    ->  the full content                          (agents/<role>/generates/...)
```

`map.notes` in the active iteration also holds the **State & inputs** block: live external
facts and required inputs, each with a last-verified date. Every role reads it at kickoff.

## 5. Entity files and versioning

```
  agents/<role>/generates/<entityId>-v<N>.md        N = iteration number

  iteration 2 OPEN                      iteration 2 CLOSED (owner, via Loopy)
  +----------------------------+        +----------------------------+
  | entityR3-v2.md  editable   |  ===>  | entityR3-v2.md   FROZEN    |
  +----------------------------+        +----------------------------+
                                                     |
                                   next change goes to a NEW file
                                                     v
                                        +----------------------------+
                                        | entityR3-v3.md  editable   |
                                        +----------------------------+

  Readers take the HIGHEST version present unless told otherwise.
```

Where each type of thing lives:

| Thing | Location |
|---|---|
| Forward/return flow | `agents/<role>/generates/<entityId>-v<N>.md` |
| Private entity (Prv) | `agents/<role>/knowledge/` |
| Research (Pub-style) | `agents/<role>/research/` |
| Role retro | `agents/<role>/generates/retro-iterationN.md` (plain name, not an entity) |
| Retro synthesis | `agents/loopy/returns/retro-synthesis-iterationN.md` |
| Publication approvals + post URLs | `agents/gtm/knowledge/publication-ledger.md` |
| Why a material decision was made | `decisions/YYYY-MM-DD-slug.md` |
| What changed, exactly | git history |

## 6. Where Loopy sits

Loopy is **not** a node in the map. It operates on the system from outside.

```
          Dan (owner)
               |  direction, approvals
               v
        +--------------+    runs workflows, drafts harness changes,
        |    Loopy     |    writes briefings; never holds the bet,
        +------+-------+    never writes into a role's folder
               |
   - - - - - - | - - - - - - - - - - - - - - - - - - - - - -   the map
               v
         PM -> Exec -> Delivery -> GTM -> Practitioners
```

Owner feedback reaches the team **through PM** (standing rule 7). Dan and Loopy do not direct
other agents past PM.
