---
name: delivery-v0
description: Delivery agent knowledge — iteration 0. The artifact exists as the map; needs a practitioner-readable description.
iteration: 0
sources:
  - cowork
---

# Delivery — Iteration 0

## What is built

The agent harness exists. It is the map itself.

**Files that constitute the artifact:**
- `base.yaml` — the topology: actors, actions, entities, edges, return flows, bypass loops, considerations
- `agents/pm/SKILL.md`, `agents/exec/SKILL.md`, `agents/delivery/SKILL.md`, `agents/gtm/SKILL.md` — role definitions
- `agents/pm/knowledge/pm.md`, `agents/exec/knowledge/exec-v0.md`, `agents/gtm/knowledge/gtm-v0.md`, `agents/delivery/knowledge/delivery-v0.md` — running knowledge
- `knowledge/` — team-wide files (standing rules, team registry, reading the map, dna) and `knowledge/research/`
- `iteration-0.yaml` — scenario: current iteration state
- `moonshot.yaml` — scenario: long horizon
- `near-term-experiment.yaml` — scenario: iteration 1 targets

## Status (2026-09-21)

- Exec brief received: `agents/exec/generates/entity1-v0.md` (certified-conditional; low-medium on the problem, low on the mechanism). Builds D1 (start-here page), D2 (content-loop spec), D3 (pre-registered verdict rule, not yet started).
- **entity2-v0 finalised for iteration 0** (2026-09-21): six parts in `agents/delivery/generates/entity2-v0.md` (start-here page, content-loop spec and ledger, design rationale, verdict rule, FAQ, handover notes for GTM). Handed to GTM by Dan. Not read by anyone outside the team; the one-sentence acceptance test is checked only by me.
- D3 rests on stated Delivery assumptions (A1 to A4 in Part 4) because Dan says no more PM input will arrive this iteration. A4 (baseline drafted without acting on ledger reads) is unconfirmed. Dan (2026-09-21): D3 and the metric weights are preliminary, not locked, and may be simplified; ledger file is `agents/gtm/knowledge/signal-ledger-v0.md`, approved.
- Rationale sources: `history/`, the log, standing rules, `dna.md`. Reasons for early folder and naming choices were not recorded (retro question). Standing rule 7 now requires a WHY on harness changes.
- Dan: keep the full iteration-0 scope in SKILL.md (README, implementation guide, FAQ, templates) for now; those are expected to come through the Exec's certified brief later. Watch entity0 for changes.
- Open flags for Dan/Loopy: content-loop return edge uses existing entityR4B plus a file convention; a dedicated signal entity in `base.yaml` is optional. `iteration-0.yaml` entity2 and entityR2 entries updated (log 112, 113). Actor2 label there still reads "Not Yet Active" (not mine to edit).

## What is missing

- **Practitioner-readable description** — the artifact is not yet packaged for someone who has never seen it. No README, no "start here" document, no implementation guide.
- **Practitioners file** — no `knowledge/practitioners/` yet; no practitioner signals on file.
- **Knowledge versioning for Exec and PM** — exec.md and pm.md not yet versioned as v0.
- **entity3 (Market Offer)** — not made. GTM needs to act.
- **entity4 (Practitioner Response)** — no practitioners reached.

## What the artifact needs to say

The product description must answer (in practitioner language, no jargon):

1. **What is this?** A multi-agent coordination system defined in YAML and Markdown. No code required.
2. **What problem does it solve?** Knowledge work agents have no automatic pass/fail (the verification gap). This gives them structure that surfaces errors rather than compounding them.
3. **What are the moving parts?** Actors (agents with roles), actions (what each actor does), entities (what they produce), edges (who uses what), skills (role definitions), knowledge files (what each agent knows and has learned).
4. **How do you run it?** Each actor reads the topology + their SKILL.md + their knowledge file, executes their action, produces their entity. Next actor reads the result. Return flows carry correction signal back.
5. **How do you know it worked?** A completed iteration means Practitioners have provided new signal. Return flows are populated. PM has updated the bet.

## Field requests from Sales (entityR3A)

*None yet received — GTM has not yet made practitioner contact.*

## Usage defects from Practitioners (entityR4C)

*None yet received — no practitioners reached.*

## Delivery escalations to Exec (entityR2A)

*None current.*

## Next action

Write the product description. Make the artifact pickupable. This is the primary delivery job in iteration 0.

## Research files

No research files yet for delivery. When practitioners use the system and report defects, those go in [[knowledge/research/]] as stable findings.


## Iteration 1 (2026-09-22)

- Exec certified `entity1-v1.md`: run D1-D3 (`entity2-v0.md`) as specced, no new build. Checked
  `agents/gtm/generates/` and `agents/practitioners/generates/` for entityR3A/entityR4C — neither
  exists, so nothing requires a rebuild.
- Wrote `entity2-v1.md` (readiness check, not new artifact content) and `entityR2-v1.md`
  (delivery reality to PM). No entityR2A — no blocker rose to an Exec escalation.
- **Open flag:** `market-offer-strategy-v0.md` lists four candidate account handles with "Dan
  picks" unresolved. Signal ledger (`agents/gtm/knowledge/signal-ledger-v0.md`) is still empty —
  zero posts made. If the account question blocks GTM from posting, it blocks the whole
  iteration-1 evidence threshold before the loop can start.
- D3's A4 assumption (baseline posts drafted without acting on ledger reads) remains adopted by PM
  into the evidence threshold but not independently reconfirmed this iteration; carried forward as
  open.
