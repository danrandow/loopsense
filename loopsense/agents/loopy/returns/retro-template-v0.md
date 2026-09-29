---
name: retro-template-v0
description: Per-agent retro conversation guide, run by Dan after an iteration closes
---

# Iteration retro — template (v0)

**How it runs.** After an iteration closes, Dan has a short chat with each agent (PM, Exec, Delivery, GTM) in its own project. The subject is what it was like to work in the harness, not the quality of its output. Ideally everyone is in one retro; for now it is one chat per agent.

**Questions (same for every agent):**
1. What did you receive from upstream, and was it what you needed to do your job?
2. What feedback reached you from downstream, and how long after you acted? What never reached you?
3. Where did you guess, get stuck, or wait?
4. What did you do that no file asked for?
5. What one change to the harness (flows, files, rules, timing) would have helped most?
6. Anything that surprised you?

**Output.** Ask the agent to write a short retro return (max one page: worked / didn't / change requested) to `agents/{id}/generates/entityR{n}-retro-v{iteration}.md` (path proposed; see the topology proposal). Log per standing rule 4.

**Then.** Dan and Loopy add a harness-level note (what we saw across the agents that no single agent could). PM reads all returns and decides what changes in the bet or topology. Dan approves any yaml or skill edits.

**Principles.** Held for the retro, not mid-iteration nudges. Agents are not hand-held during an iteration. Questions about the harness itself (e.g. Delivery's consideration-vs-environment question) are retro topics.
