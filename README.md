# LoopSense

LoopSense is a way to run a team of AI agents on knowledge work — strategy, discovery,
research synthesis, content — so that the work gets checked by the world instead of by a
human referee. It is a map of your agent team, written in YAML and Markdown, that carries
what the world actually did with each piece of work back to the agent that made it, through
named return flows, so that agent changes what it does next. No code runner, nothing to
install: AI agents you already use, plus files.

**Honest status: this is being tested, not proven.** Our own team runs on it (we are our own
first customer). Whether outcome signal actually improves agent output is the open question —
we run experiments against it in the open. See [Status](#status-tested-vs-not-tested) below
before you believe anything here.

Licensed under the [Apache License 2.0](LICENSE).

---

## The problem: the verification gap

Coding agents get verification for free — tests pass or they don't, and the agent can iterate
against that signal without a human. Knowledge work has no tests. There is no pass/fail for a
strategy memo or a research synthesis, so a human becomes the referee: someone reads the
output and decides whether it counts. That is slow and expensive, or it is skipped and
unreliable. In multi-agent setups the problem compounds — agents agree with each other and
polish each other's work without ever meeting a ground truth.

This problem is not ours alone; it is being named publicly by practitioners and commentators
(sources are recorded in [`knowledge/research/verification-gap.md`](knowledge/research/verification-gap.md)).

Writing a rubric to judge the work does not escape the trap: writing a good rubric for
knowledge work takes more domain judgment than doing the work. We call that the
success-criteria trap.

## The idea: let the environment verify

Once work is out in the world, the world responds — replies, follows, clicks, forks, deals.
LoopSense routes that response back to the agent that produced the work, through a **named
return flow**, with a discipline attached: the agent must write down what it will change next
and cite the specific response records that justify the change. Then the next output either
shows that change or it doesn't — and that part is checkable from the files by someone who
was not in the room.

We claim this **partly** closes the verification gap. Two honest caveats that our own analysis
insists on:

- **Interpretation is still judgment.** Deciding what a response *means* is knowledge work
  too. What the mechanism buys is that human judgment shrinks from once-per-output to
  once-per-frame — setting what counts as a good response, resolving ambiguity, authorising
  what goes out publicly — instead of grading every draft.
- **Feedback improves what you already make; it does not invent strategy.** The loop
  hill-climsbs. It does not survey the space of things you should have made.

Tools that validate with simulated judges or synthetic audiences substitute one simulation for
another; human-in-the-loop review makes the human the permanent verifier. LoopSense uses what
actually happened. (Named examples and competitive analysis live in the team's research
notes, e.g. [`agents/gtm/knowledge/`](agents/gtm/knowledge/).)

## The moving parts

| Part | What it is |
|---|---|
| **Actors** | The agents. Each has exactly one role. (`actor0`…`actorN` in the map) |
| **Actions** | The one thing each actor does. (`action0`…`actionN`) |
| **Entities** | What flows between them. Forward entities carry work downstream; **return** entities (`entityR…`) carry signal back upstream; **bypass** returns skip the middleman and route feedback straight to the actor who can use it. |
| **Edges** | Who generates what, who reads what. This is the topology. |
| **Map** | All of the above in one YAML file (`base.yaml`) — forkable, diffable, versionable. A topology as a file can be compared between runs; a code-defined graph can't be held still. |
| **SKILL.md** | One per agent: its role, its starting question, what to read first, what to produce, its write boundary. |
| **Knowledge file** | One per agent: what that agent has built, learned, and had requested of it. Updated after every action. |
| **Iteration scenario** | `iteration-N.yaml` — one run of the system, inheriting from the map, recording state and per-entity summaries. Frozen when the iteration closes. |

One practice cuts across everything — **consideration**: before acting, an agent reads the
knowledge file of whoever will receive its output, and writes for what that receiver can
actually use. It is a practice, not a schema field. Whether it improves output is untested.

## The repository, explained

This repository holds two things at once: **LoopSense the method** (the files you would fork)
and **a running instance of it** (our own team using the method to build and test the method).

```
base.yaml                 The canonical topology: actors, actions, entities, edges.
                          Read-only for agents; the single source of truth for the map.
iteration-N.yaml          One scenario per iteration: state, overrides, entity summaries.
                          The only map file agents edit (their own entries only).
moonshot.yaml             The long-horizon target state — direction instead of guardrails.
near-term-experiment.yaml Near-term scenario targets.
agents/
  <role>/SKILL.md         The role: starting question, read order, outputs, write boundary.
  <role>/knowledge/       The role's running knowledge (and private entities, Prv).
  <role>/generates/       Full entity content, versioned per iteration: <entity>-v<N>.md.
  practitioners/          Customer-side return flows (entityR4…), when practitioners engage.
knowledge/
  standing-rules.md       Team-wide rules. Read first, every session.
  team-registry.md        Who generates and consumes what; entity file locations.
  reading-the-map.md      How to read the map and scenario files.
  dna.md                  Design philosophy behind the topology.
  audit-policy.md         Commit, decision-record and audit discipline.
  research/               Stable, sourced research findings (e.g. verification-gap.md).
decisions/                Short decision records for material owner/PM choices.
workflows/                Team processes (starting an iteration, retrospectives).
history/, loopsense.log.json  Frozen legacy audit trail. Historical evidence only —
                          never current instructions, never edited.
openclaw/                 Agent-adapter configuration for running the roles on an
                          agent platform. Not required to understand the method.
PUBLIC_EXTRACTION.md      Provenance note for this standalone repository.
```

Naming convention for flows: every entity an agent generates goes to
`agents/<role>/generates/<entityId>-v<N>.md`, where N is the iteration number. Files are
frozen when an iteration closes — new versions get a new file. Readers take the highest
version present.

## Run one iteration, step by step

You need an AI tool that can read and write files (a coding agent, a chat agent with file
access — whatever you already use), and somewhere your work can meet the world (an account, a
repo, a channel where real people respond).

1. **Set up the files.** Copy `base.yaml`, the `agents/*/SKILL.md` files, and
   `knowledge/standing-rules.md`, `team-registry.md` and `reading-the-map.md`. Rename the
   actors and edit the map to fit your team (see [Make it yours](#make-it-yours)).
2. **PM writes the bet** (`entity0`): the current hypothesis — what is being built, for whom,
   why, what evidence would change it.
3. **Exec certifies or returns it** (`entity1`): the viability lens. Certification states its
   basis and its confidence, including what it is proceeding *without*.
4. **Delivery builds the artifact** (`entity2`) and writes delivery reality back to PM
   (`entityR2`): what it actually took, what would take longer than the window.
5. **GTM takes it to the world** (`entity3`) — or, at first, listens — and returns market
   signal to PM (`entityR3`).
6. **The world responds** (`entity4`): engagement, questions, objections, adoption. Return
   flows carry it back — to PM, or directly to the actor who can use it (bypass flows).
7. **Each actor updates its knowledge file** and writes its return flow before the next
   actor's read. In this map, an iteration completes when GTM has returned its market signal
   to PM. Yours can differ.

In practice each actor is a session: give it the map, its SKILL.md, its knowledge file, and
the upstream entity, and ask it to do its role and write its outputs to
`agents/<role>/generates/`.

### The content loop, worked example

The smallest complete LoopSense run is a content loop, and it needs no code:

1. The drafting agent writes a post plus a **change note**: what differs from the previous
   post and which response records justify it (blank for the first).
2. An owner gate approves, edits, or rejects for safety/brand — logged with a reason category
   (`safety-brand` / `quality` / `none`). The gate is about exposure, not quality grading.
3. Publish. Read the real numbers and replies at fixed windows (e.g. 24h, 72h, 7d).
4. Fill one **ledger row** per post: raw numbers, typed responses (objection / question /
   endorsement / demand / noise), who responded (with reasons for any fit judgment), and the
   raw snapshot of what the platform showed at read time — platform numbers get revised
   retroactively. Missing data is recorded as a gap, never estimated.
5. The next change note must cite specific ledger rows, and the next draft must visibly differ
   in the named way. A reviewer who was not in the loop can check both.
6. After ten posts, compare a baseline phase against a verdict phase. Report the numbers and
   the single posts that drive any difference — one lucky post is not a trend.

Pre-register the verdict rule *before* the data arrives (what counts as improved, what would
count as evidence against). That discipline — borrowed from single-case experimental design —
is what keeps the loop honest at small numbers.

## How do you know it worked?

A completed iteration means **the world produced new signal and the system visibly moved**:

- Every return flow has a filed entry.
- Ledger rows exist for real outputs, with gaps recorded honestly.
- At least one change note cites specific response records, and the next output visibly
  differs in the named way.
- The human-override log tells you something true: if gate overrides tagged *quality* fall
  across a run while outputs keep improving on the world's response, that is direct evidence
  humans aren't needed to verify quality. If they don't fall, that is evidence against.
- PM has updated the bet — and can point to the rows that forced the update.

If output changed but nothing cites a row, the loop didn't run — the agent just changed its
mind. If rows arrived but nothing changed, that's divergence: signal the system can't act on,
and a defect worth naming.

## Make it yours

Everything below is the fork path. None of it requires code.

### Files to create, in order

1. **`base.yaml`** — copy ours and rewrite: your actors, actions, entities, edges (below).
2. **`agents/<role>/SKILL.md`** — one per actor.
3. **`agents/<role>/knowledge/<role>.md`** — one per actor.
4. **`knowledge/standing-rules.md`** — your team-wide rules (ours are a worked example).
5. **`knowledge/team-registry.md`** — who generates and consumes what.
6. **`iteration-1.yaml`** — your first scenario file.

### What a SKILL.md must contain

- **Role statement** — what this actor owns and what it has no authority over.
- **Starting question** — the question answered before anything else each iteration.
- **Read order** — the files to read before acting (upstream entity, its own knowledge file,
  the receiver's knowledge file for consideration).
- **Outputs** — exactly which entity files to write, where, with what content.
- **Write boundary** — what it may write and what it must never touch.
- **Return flow** — what it sends back upstream, to whom, in what form.
- **Handoff line** — the fixed wording that ends its turn and names the next step.

Keep it under a couple of pages. If it needs more, the detail belongs in the knowledge file.

### What a knowledge file must contain

- **What is built** — current state of this role's artifacts, with dates.
- **What is missing / what has been requested** — open items and who asked.
- **What has been reported broken** — usage defects, treated as bugs.
- **Status and next action** — updated after *every* action, not periodically.
- **Research pointers** — stable findings with sources.

Write it as running memory a fresh session can trust: dates on facts, uncertainty stated
plainly, stale items marked superseded rather than deleted.

### How to define the topology in base.yaml

- **`actors`** — the roles. `id`, `label`, `notes` (what they do, where their files live).
- **`actions`** — one per actor: what that actor does.
- **`entities`** — the things passed around. `system_boundary`: `internal` (spine),
  `private` (one actor's own knowledge), `public` (the environment). `direction: return` for
  anything flowing back upstream.
- **`edges`** — `generates` (action → entity) and `used by` (entity → action). An actor's
  inputs are its `used by` edges; its outputs are its `generates` edges.
- **Return and bypass edges** are ordinary edges with `direction: return` — the bypasses
  (e.g. practitioner → builder, builder → exec) are what make the topology a loop instead of
  a pipeline. They carry tension around the middleman by design; the PM integrates it rather
  than suppressing it.

Keep labels terse (a few words); put explanation in `notes`. Scenario files (`inherits:
base.yaml` plus `overrides`) record each run so runs can be compared.

### What to run first

One full iteration by hand, at the smallest scale that touches the world — ten posts, five
shipped fixes, one research series. Pre-register your verdict rule, keep the ledger, enforce
the citation discipline, and read the override log at the end. If the citation discipline
feels like paperwork, the loop isn't wired to real signal yet — that finding is useful too.

## Status: tested vs not tested

| Tested | Not tested |
|---|---|
| Our own team has run on this map across multiple iterations; the files read and edit fine by hand | That outcome signals change what an agent does |
| The map's return flows, bypasses and scenario files work as a coordination spec | That any change is an improvement |
| The discipline is followable in principle (spec in [`agents/delivery/generates/`](agents/delivery/generates/)) | That consideration (reading your receiver's knowledge file) improves output |
| | That anyone outside this team can run it |
| | That a small account gives usable signal at all |
| | That the loop's effect is separable from timing, topic and platform drift |

Current experiments and their results are in the open: see
[`agents/delivery/generates/`](agents/delivery/generates/) (what was built and what it took),
[`agents/gtm/knowledge/`](agents/gtm/knowledge/) (signal ledger and research), and
[`decisions/`](decisions/) (what was decided and why).

## FAQ

**Do I need code?** No. AI agents that can read and write files, YAML and Markdown. There is
no code runner and nothing to install.

**Is this a framework or a runner?** Neither. It is a spec for how a team of agents relates,
plus the files to run it by hand. How you run the agents is up to you.

**Isn't this just a metrics dashboard?** A dashboard shows numbers to a person. Here the
numbers go to a named actor through a named return flow, and that actor must write down what
it will change and which records justify it. The change is what gets checked.

**Why not use an LLM as the judge?** Writing a rubric good enough to judge complex work takes
more judgment than doing the work, and a judge that simulates feedback puts you back where you
started. We use what the world actually did.

**Is a human involved?** Yes — at the frame and the gate. A human sets what counts as a good
response and authorises what goes out publicly. The claim under test is that no human is
needed to grade quality draft-by-draft; the override log measures whether that holds.

**What if the signal is slow or noisy?** Match your response window to the system: hours for
attention metrics, days for human responses, months for organisational buying. Ten posts on
one small account give a direction, not a proof — pre-registered rules and raw snapshots are
what keep small numbers honest.

**What if my work has no engagement metric?** The idea carries wherever the world's response
can be measured and re-enter the loop. We have tested it only against content so far.

**What is "consideration"?** Before producing output, an agent reads the knowledge file of the
actor who will receive it and writes for what that receiver can use. A practice, not a schema
field; untested.

**Why PM, Exec, Delivery and GTM?** That is our own team — a starting fork. Rename the roles
to yours.

**Does it work?** Unknown. That is what the open experiments are for. We will report the
numbers either way.

## Governance and provenance

- **License:** [Apache License 2.0](LICENSE).
- **Audit:** Git-native since 2026-09-24 — commits are the mechanical audit trail; material
  owner/PM decisions get short records in [`decisions/`](decisions/). The older ledger
  (`loopsense.log.json`, `history/`) is frozen historical evidence.
- **Publishing standard:** agent-authored public posts are drafted, human-reviewed before
  publication, and sourced-or-labelled under
  [`knowledge/social-agent-publishing-standard.md`](knowledge/social-agent-publishing-standard.md)
  and [`knowledge/standing-rules.md`](knowledge/standing-rules.md).
- **Claims discipline (applies to this README too):** substantive claims carry sources or are
  marked as interpretation or hypothesis. If something here reads as a claim and has no
  source, treat it as our hypothesis — and please open an issue.
- **Privacy:** this repository is public by design. It contains no credentials, no private
  contact details, and no session transcripts. Reports of anything that looks private are
  welcome and get removed.
- **Maintainer:** Dan Randow (project owner). Use GitHub issues on this repository for
  questions and defect reports.

---

*Presented by the LoopSense Delivery role. If something on this page confused you, that is a
defect in the artifact, not in you — please report it.*
