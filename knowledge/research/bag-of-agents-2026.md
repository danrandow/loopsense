---
name: bag-of-agents-2026
description: Stable research finding — flat multi-agent topologies amplify error rather than solve coordination
sources:
  - "Towards Data Science, 2026"
---

# Bag of Agents (2026)

**Source**: Towards Data Science (2026)

## Core finding

Flat multi-agent topology — agents operating without hierarchy, without verification gates, without structured orchestration — amplifies error rather than distributing it. Measured error amplification: up to **17.2×** versus a single-agent baseline.

## Mechanism

Without structure:
- Each agent adds noise to what it receives
- Errors compound across the chain without correction
- Token budget is consumed by coordination chatter rather than productive work
- Output drift increases as agent count increases

## Implication for Loopsense

The product-manager-bet topology is NOT a bag of agents. It has:
- Named roles with distinct lenses (not generic agents)
- Return flows that carry correction signal back upstream
- Bypass loops for field escalations
- A consideration mechanism (each agent reads its knowledge file before acting)

The verification gap remains: the topology manufactures structure, but structure alone doesn't guarantee correctness — it guarantees that errors surface rather than compound silently.

## Counter-evidence

More agents with good structure can outperform fewer agents with poor structure. The finding is specifically about **flat, unstructured** topologies, not multi-agent systems generally.

## Related

- [[multi-agent-production-2026]] — what actually survived in production
- [[verification-gap]] — the unsolved problem this finding points toward
