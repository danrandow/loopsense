# LoopSense developer docs

Start here if you are going to **change, run, fork or extend** this repository. The root
[README](../README.md) makes the product case. These docs explain how the system actually works.

> **Read this first: there is no code here.** No build, no package manager, no test suite, no
> runtime. The "program" is a set of YAML and Markdown files. AI agents read them, act, and
> write back. Developing on LoopSense means editing **specs, role instructions and
> workflows** and keeping the file contracts intact. The only tooling is `git`, a YAML
> parser and `node` for JSON checks.

---

## TL;DR

LoopSense runs a **team of AI agents on knowledge work** (strategy, research, content). The world
checks their output, not a human grading each draft.

```
   +--------------------+        owner gate        +---------------------+
   |  agent produces    |  (safety/brand only) --> |      the world      |
   |  work + a CHANGE   | -----------------------> |  replies, follows,  |
   |  NOTE              |         publish          |  clicks, forks...   |
   +--------------------+                          +---------------------+
             ^                                                |
             | next output must visibly differ                | read at fixed windows
             | AND cite specific ledger rows                  | (24h / 72h / 7d)
             |                                                v
   +--------------------+     named RETURN FLOW    +---------------------+
   |  agent's knowledge | <----------------------- |   signal ledger     |
   |  file (what it     |    (entityR...)          |   raw numbers +     |
   |  learned)          |                          |   typed responses   |
   +--------------------+                          +---------------------+

   Checkable from files alone: did the change note cite rows, and did the
   next output change in the named way?
```

- **The map** (`loopsense/base.yaml`) is a graph of 5 actors, 20 entities and 37 edges. It
  defines who produces what, who reads what, and which feedback flows go back upstream.
- **The team** has four agent roles: PM → Exec → Delivery → GTM. There is also **Loopy**, the
  owner's assistant, which works *on* the system and not *in* it. Practitioners (real users)
  are the fifth actor in the map. They are outside the team.
- **An iteration** is one forward pass through the roles. Each role writes versioned entity
  files and a return flow. The pass ends when GTM returns market signal to PM. Each iteration
  is recorded as an `iteration-N.yaml` scenario that inherits from `base.yaml`.
- **Governance is file-based.** Every role has a strict write boundary. Git commits are the
  audit trail, and `decisions/` holds the reasons for material choices.
- **Honest status:** it is dogfooded: the team building LoopSense runs on LoopSense. The core
  claim, that outcome signal improves agent output, is **not yet tested**.

## Current state (snapshot as of 2026-09-29)

| | |
|---|---|
| Active iteration | `iteration-2.yaml`: *"Can a system without a continuous human close the verification gap by learning from how the world responds to its work?"* |
| Delivery verdict (entity2-v2) | The gap is **shrunk and made auditable, not solved**. Human judgment moves from once-per-output to once-per-frame. |
| Evidence run | Ten-post run is pre-registered. 5 baseline drafts are queued and **blocked on Stage 2 human review**. Nothing has been posted. |
| Known blocker | x.com returns HTTP 403 from the headless cloud environment, so per-post metric capture on X is at risk. |
| Practitioner signal | None yet. `agents/practitioners/` does not exist. |

Check `loopsense/iteration-2.yaml`, in its `State & inputs` block, before trusting this table.

## Docs index

| Doc | Read it when you need to... |
|---|---|
| [architecture.md](architecture.md) | understand the map, the entities, the file layout and how scenarios inherit |
| [operating.md](operating.md) | run an iteration, run a retro, or understand the gates and stop conditions |
| [contributing.md](contributing.md) | change anything: write boundaries, commit and validation discipline, lint snippets |
| [runtime.md](runtime.md) | wire the roles onto an agent platform (harness contract, OpenClaw adapters) |

## Reading paths

```
 "What is this?"            root README  ->  docs/README (this)  ->  loopsense/knowledge/dna.md

 "I'm changing files"       contributing.md  ->  loopsense/knowledge/standing-rules.md
                            ->  loopsense/knowledge/audit-policy.md

 "I'm running a pass"       operating.md  ->  loopsense/workflows/*.md
                            ->  loopsense/agents/<role>/SKILL.md

 "I'm forking it"           architecture.md  ->  loopsense/base.yaml
                            ->  loopsense/knowledge/reading-the-map.md  ->  runtime.md
```

## Glossary

| Term | Meaning |
|---|---|
| **Actor / action** | A role (`actorN`) and the one thing it does (`actionN`). |
| **Entity** | Something that flows between actions. `entityN` goes forward (the *spine*). `entityR…` is a *return*. `Prv` is private to one actor, `Pub` is public environment. |
| **Bypass** | A return flow that skips PM: R2A, R3A, R3B, R4A, R4B, R4C. These are treated as real tensions, not noise. |
| **Bet** | `entity0`, PM's current hypothesis: what, for whom, why, and what evidence would change it. |
| **Scenario** | A YAML file that `inherits: base.yaml` and lists `overrides`. One per iteration, plus `moonshot.yaml`. |
| **Consideration** | A practice, not a schema field: before acting, read your receiver's knowledge file and write for what they can use. |
| **Change note** | What differs from the last output, citing the ledger rows that justify it. |
| **Loopy** | The owner's assistant. It runs workflows, drafts harness changes and writes briefings. It is not a map actor. |
| **Dan** | The project owner. Approves consequential and public actions. |
| **Frozen** | Files from a closed iteration. Never edit them; write `v{N+1}` instead. |
