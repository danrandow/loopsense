---
name: retro-topology-proposal-v0
description: Draft, not applied. Proposed retro flow for base.yaml, for Dan approval
---

# WITHDRAWN 2026-09-21: Dan says the retro sits outside the topology (outermost loop). Do not apply.

# Retro flow — proposal (not applied)

Nothing in base.yaml has been changed. Read base.yaml's schema before finalising ids and labels.

**Proposed shape**
- Action (after iteration closes): "Hold retro" (Dan + Loopy), reading each agent's retro return.
- Entity per agent: "Retro return" (return flow), each written to `agents/{id}/generates/`.
- Actor consumption: PM reads all four retro returns plus the Dan/Loopy harness note, then decides bet/topology changes.
- Edges: each of PM, Exec, Delivery, GTM -> retro return -> PM; Dan/Loopy note -> PM.

**Open questions for Dan**
1. One shared entity id (e.g. entityR5-retro) or one per agent?
2. Is the retro a new action, or an extra return flow on the existing iteration-close step?
3. Add to iteration-0.yaml now, or start at iteration 1 (iteration 0 is already running)?

On approval I will follow standing rule 6 (history record, log first, targeted edit, read-back).
