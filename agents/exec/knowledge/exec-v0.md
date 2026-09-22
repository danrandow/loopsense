---
name: exec-v0
description: Exec & Business knowledge, iteration 0. Certification history, business model thesis and precedents. The brief itself lives in agents/exec/generates/entity1-v0.md.
iteration: 0
sources:
  - cowork
---

# Exec & Business: Iteration 0

## Certification history

- **2026-09-17:** Certified the first bet (topology as a lightweight manufactured referee for orchestration engineers). Low-medium confidence. Brief archived in `agents/exec/research/exec-v0-prev-2026-09-17.md`.
- **2026-09-21:** PM revised the bet (real-world feedback through structured return flows replaces the manufactured referee; Dan's insight). Re-certified on Dan's reframe: aim is to not need a human to verify. Low-medium on the problem, low on the mechanism. Brief: `agents/exec/generates/entity1-v0.md`. Signal and questions to PM: `agents/exec/generates/entityR1-v0.md`. Inputs missing: no entityR2A; R3B shows zero pipeline.
- **2026-09-22:** Certified PM's iteration-1 bet (`entity0-v1.md`, continue / run the ten-post content loop). Low-medium on the problem (now independently confirmed in the wild), low on the mechanism (unchanged, zero direct evidence). Brief: `agents/exec/generates/entity1-v1.md`. Signal to PM: `agents/exec/generates/entityR1-v1.md`. Inputs still missing: no entityR2A; entityR3B on file is still iteration-0's (pipeline: none). ICP supply-side gap is now the sharpest open risk in the bet.

## Business model thesis

Attention-first, open spec, revenue later; no revenue target this iteration. Paid layer, if adoption comes: hosted signal-routing and ledger connectors the open version cannot provide (path A). Nearest revenue, hypothesis only: loop-design work from Dan's consulting base (path B, needs Dan's call). entityR4A (revenue) is empty, correctly.

## Precedents

- **Open spec + hosted infrastructure:** LangChain to LangSmith; Hugging Face Hub.
- **Attention-first, monetise later:** developer adoption through open source; works if the technology is novel and adoption creates network effects.
- **Community + data flywheel:** requires the tool to generate valuable signal, not just users.
- **Comparable pricing:** loopi.tech $10-40/month for synthetic-persona validation (PM buyers); Grep.ai commercial in regulated repetitive work (GTM, 2026-09-21).

## Open questions

- Is the environmental-feedback mechanism a category people will pay for, and who is the buyer? (entityR1 Q2)
- Can a small account produce a usable signal? (entityR1 Q4)
- Does the paid layer (signal routing) hold up if platforms restrict analytics access?

### Technical positioning — composable loop topologies

**What we are, precisely:** A directed graph with opinionated defaults, fitted to a specific
subsystem — product coordination. Not a free mesh (too chaotic to inspect, error compounds).
Not a fully adaptive graph (cutting edge, unproven at scale, expensive to build and maintain).
Something in between: a composable loop topology.

**The middle path:**
- Free mesh (AutoGen, many multi-agent frameworks): agents route themselves. Maximum flexibility.
  Hard to inspect. Errors cascade without structural intervention.
- Adaptive graph (emerging, 2026 research): topology reshapes in response to task. Powerful.
  Still experimental. Requires significant investment to build and trust.
- Composable loop topology (Randow Maps): topology is defined in advance, in YAML, for a specific
  context. Directed. Inspectable. Opinionated. When the topology fits the subsystem well, you don't
  need to adapt it — you use it. When you need more, you compose: add an adjacent topology
  (a parallel loop), a super-topology (a loop that governs this loop), or a sub-topology
  (a specialist loop inside an actor node).

**The constraint is the feature:** practitioners assume maximum flexibility is the goal. What they
actually need is structure that surfaces errors. YAML constraint produces inspectability.
YAML composability means growth without increasing internal complexity.

**YAML enables composability:** forkable, versionable, composable by reference. The map is a
shareable, diffable, citable artifact — not just a runtime config.

See [[dna]] for the full relational philosophy behind the topology design.

## Viability research

See [[bag-of-agents-2026]], [[multi-agent-production-2026]], [[verification-gap]], [[agentic-pipelines-in-production-2026]] in knowledge/research/.

Production data (2026): 11% of multi-agent systems reach production (Gartner/MIT). 64% of tasks
perform better with single agent + tools than multi-agent orchestration. Practitioners currently
solving the verification gap with manual human-review-gates at each handoff — the opening for
an automatic structural mechanism (the topology).
