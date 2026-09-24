---
name: team-registry
description: Agent team role table — who generates and consumes what. Source of truth for topology. Entity descriptions live in base.yaml.
sources:
  - cowork
last_updated: 2026-09-19
---

# Team Registry — Agent Team v0

Entity IDs reference base.yaml. Descriptions live there — not duplicated here.

## Role table

| | **PM** | **Exec** | **Delivery** | **GTM** | **Loopy** |
|---|---|---|---|---|---|
| **actorID** | actor0 | actor1 | actor2 | actor3 | loopy |
| **actionID** | action0 | action1 | action2 | action3 | — |
| **Role** | Hold & iterate the bet | Apply viability lens | Build & deliver | Listen & validate | Owner's assistant |
| **Accounts** | — | — | GitHub | @loopsense | — |
| **Skill file** | agents/pm/SKILL.md | agents/exec/SKILL.md | agents/delivery/SKILL.md | agents/gtm/SKILL.md | agents/loopy/SKILL.md |
| **Generates folder** | agents/pm/generates/ | agents/exec/generates/ | agents/delivery/generates/ | agents/gtm/generates/ | agents/loopy/returns/ (briefings) |
| **Knowledge folder** | agents/pm/knowledge/ | agents/exec/knowledge/ | agents/delivery/knowledge/ | agents/gtm/knowledge/ | agents/loopy/knowledge/ |
| **Generates** | entity0, entityPrv0 | entity1, entityR1 | entity2, entityR2, entityR2A | entity3, entityR3, entityR3A, entityR3B | briefings → Dan |
| **Consumes** | entityR1, entityR2, entityR3, entityR4, entityPrv0 | entity0, entityPrv1, entityPub0, entityR2A, entityR3B, entityR4A | entity1, entityPrv2, entityR3A, entityR4C | entity2, entityPrv3, entityPub0, entityR4B | all agent outputs |

**Practitioners** (actor4) are customers, not team members. Their return flows (entityR4, entityR4A, entityR4B, entityR4C) are recorded in agents/practitioners/generates/.

## Entity file locations

Every flow an agent generates is written to `agents/{id}/generates/{entityId}-v{n}.md` (n = iteration; frozen when the iteration closes; readers take the highest v present). `Prv` entities are the agent's `knowledge/` files; `Pub` entities live in `research/`. Loopy's briefings to Dan stay in `agents/loopy/returns/`.

| Entity | Written by | Path | Read by |
|---|---|---|---|
| entity0 | PM | agents/pm/generates/entity0-v{n}.md | Exec, Delivery, GTM |
| entity1 | Exec | agents/exec/generates/entity1-v{n}.md | Delivery, GTM |
| entity2 | Delivery | agents/delivery/generates/entity2-v{n}.md | GTM |
| entity3 | GTM | agents/gtm/generates/entity3-v{n}.md | Practitioners |
| entityR1 | Exec | agents/exec/generates/entityR1-v{n}.md | PM |
| entityR2 | Delivery | agents/delivery/generates/entityR2-v{n}.md | PM |
| entityR2A | Delivery | agents/delivery/generates/entityR2A-v{n}.md | Exec |
| entityR3 | GTM | agents/gtm/generates/entityR3-v{n}.md | PM |
| entityR3A | GTM | agents/gtm/generates/entityR3A-v{n}.md | Delivery |
| entityR3B | GTM | agents/gtm/generates/entityR3B-v{n}.md | Exec |
| entityR4 | Practitioners | agents/practitioners/generates/entityR4-v{n}.md | PM |
| entityR4A | Practitioners | agents/practitioners/generates/entityR4A-v{n}.md | Exec |
| entityR4B | Practitioners | agents/practitioners/generates/entityR4B-v{n}.md | GTM |
| entityR4C | Practitioners | agents/practitioners/generates/entityR4C-v{n}.md | Delivery |

## Log discipline

Follow `knowledge/audit-policy.md` for commit and sync.
