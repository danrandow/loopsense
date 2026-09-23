---
name: loopy-working-context
description: Loopy's running context — open decisions, what Dan and Loopy are working on, session continuity
sources:
  - cowork
last_updated: 2026-09-23
---

# Loopy — Working Context

## What we are building

Loopsense: a multi-agent topology for knowledge work, dogfooding itself.

Brand: Loopsense (@loopsense on X, loopsense.com taken)
Map: Loopsense (base.yaml is the source of truth)
Owner/architect: Dan Randow
Loopy: Dan's assistant (this file is mine)

## Dan's role

Owner, governance, architect. Works on the system, not in it.

## Our role (Dan + Loopy)

Set the team up for success. Maintain topology integrity. Evolve the system based on what
the agents return. Do not hold the bet, certify viability, build artifacts, or do market research
— those belong to PM, Exec, Delivery, GTM respectively.

## Current system state — 2026-09-23 (post-release)

### What exists
- base.yaml: full topology with actors, actions, entities, edges, bypass loops
- moonshot.yaml: the 18–36 month north star scenario
- agents/ folder structure: created this session (per-agent: SKILL.md, knowledge/, generates/, research/; Loopy keeps returns/ for briefings)
- knowledge/team-registry.md: role table with generates/consumes rows
- knowledge/standing-rules.md: team-wide governance (rule 8: tone/fairness for public accounts)
- knowledge/claims-certainty-standard.md: selective labeling for high-stakes claims ([Verified], [Unverified], [Hypothesis], [Our Interpretation])
- knowledge/social-agent-publishing-standard.md: three-stage workflow (draft -> human review -> official API publication) for agent social media posting
- agents/gtm/generates/entityR3-v0.md: market signal template with loopi.tech competitive section
- agents/loopy/: this folder
- Public release: Loopsense repository pushed to GitHub (2026-09-23) with intentionally-public audit trail (loopsense.log.json, history/)

### What doesn't exist yet (iteration 0 open items)
- entityR1.md (Exec hasn't written viability signal yet)
- entityR2.md (Delivery hasn't written delivery reality yet)
- entityR4.md (no practitioner contact yet)
- Claude projects (five tabs): not yet created — instructions in each agents/*/project-instructions.md
- Market offer (entity3): not yet made

### Open decisions
- Old files (skills/, knowledge/ flat files): duplicated by agents/ structure — Dan to delete when ready
- DONE 2026-09-19: SKILL.md files (pm, exec, delivery, gtm) — "Sales & Partners" -> GTM, "Randow Maps agent team" -> Loopsense agent team
- DONE 2026-09-19: remaining 'Sales & Partners' refs -> GTM across yaml/knowledge/landing page; sales-partners paths -> agents/gtm/knowledge/gtm-v0.md; @topologyengine -> @loopsense; near-term title renamed
- OPEN: @loopsense bio and email in agents/gtm/knowledge/{gtm-v0,market-offer-strategy-v0}.md still carry legacy @topologyengine values, flagged for Dan to supply
- "Randow Maps" as the schema/product name is intentionally kept; only "Randow Maps agent team" was renamed
- Agent project instructions are now 7-line stubs; protocol lives in each SKILL.md "Session protocol" + knowledge/standing-rules.md (incl. ignore context.md). Dan pastes stubs into the 5 Claude projects once.

### Entity file scheme (decided 2026-09-19)
- Flows an agent generates (forward entityN, return entityRN) live at agents/{id}/generates/{entityId}-v{n}.md; n = iteration; frozen when the iteration closes. Prv -> knowledge/, Pub -> research/. Rules 4-5 in knowledge/standing-rules.md; path table in team-registry.md.
- Bet = entity0, now agents/pm/generates/entity0-v0.md. iteration-0.yaml: label -> notes (summary + Full entity link) -> file.
- Empty legacy returns/ folders under pm, exec, delivery, gtm, practitioners: Dan to delete (no delete permission granted).
- Handoffs drafted in agents/loopy/returns/handoff-pm-rerun.md and handoff-exec-pickup.md; Dan pastes into the PM and Exec projects (Exec after PM).
- OPEN: agents/delivery/knowledge/delivery-v0.md still references knowledge/pm-v0.md (stale); Delivery to fix.

## Session log

| Date | Topic | Outcome |
|------|-------|---------|
| 2026-09-19 | Folder structure, role table, five projects setup, moonshot split | agents/ created, team-registry.md written, project-instructions.md files written |
| 2026-09-19 | Slim instructions; ignore context.md; stale-name cleanup | Stubs + Session protocol in SKILL.md, standing-rules.md added, SKILL.md names fixed |
| 2026-09-19 | Generalise bet versioning to all entities | generates/ scheme adopted, files migrated, SKILL.md/registry/standing-rules/yaml updated, PM and Exec handoffs drafted |
| 2026-09-22 | Lightweight retro prompt + iteration-1.yaml skeleton | retro-prompt-lightweight-v1.md written, iteration-1.yaml created (both Dan-approved) |
| 2026-09-23 | Public release safeguards and social media governance | Enhanced standing rule 8 (tone/fairness), claims-certainty standard (context-aware), social-agent-publishing-standard.md (3-stage workflow, Anthropic compliance) created and committed; agents authorized for Twitter/X and LinkedIn posting |

### Retro after each iteration (agreed 2026-09-21; lightened 2026-09-22)
- Dan chats with each agent (PM, Exec, Delivery, GTM) after an iteration closes: async, one chat each, about what it was like working in the harness. Ideally one shared retro later.
- Fuller template: agents/loopy/returns/retro-template-v0.md (6 questions). For iteration-0's close, using a lighter 3-bullet version instead: agents/loopy/returns/retro-prompt-lightweight-v1.md. Each agent writes agents/{id}/generates/retro-iteration0.md; Dan keeps discussion to a minimum.
- Topology proposal WITHDRAWN: retro is the outermost loop, outside base.yaml. Retro files use a plain filename (retro-iteration0.md), not an entity id.
- Principle: no mid-iteration hand-holding; harness insights are held for the retro and go to PM (holds vision). Delivery's consideration-vs-environment question: treat as one loop at different hops; iteration-0 retro topic. Not applied: entity0 line 88 rewording and iteration-0.yaml 'Consideration mechanism confirmed' softening (wait for PM).
- DONE 2026-09-22: retro-synthesis-iteration0.md written (log id 126) and recommendations actioned (log id 127). Corrected 2026-09-23: this item was previously listed as OPEN; that was wrong — the synthesis was done and acted on.
- DONE 2026-09-23: iteration-1 retro completed (log id 177 practice record, 178-181 role retros, 182 synthesis). Committed and pushed (6d99674, 3bbc914).

### Iteration 1 (started 2026-09-22; retro completed 2026-09-23)
- iteration-1.yaml created (log id 121); scenario set by PM 2026-09-22 (log id 134). Entity overrides in place (log ids 134, 138, 142, 145, 152). Iteration-1 retro completed and pushed (log id 182). Seven proposed harness improvements in agents/loopy/returns/retro-synthesis-iteration1.md await Dan/PM decision.
