---
name: entity2-v1
description: The product, iteration 1. Confirms D1-D3 (entity2-v0) stand unchanged for the ten-post run Exec certified. No GTM field requests or practitioner defects arrived this iteration, so nothing here is a rebuild — it is a readiness check and an explicit release to run.
entity: entity2
direction: forward
from: actor2 (Delivery)
to: actor3 (GTM)
iteration: 1
status: ready-for-gtm (cleared to run)
based_on: agents/exec/generates/entity1-v1.md
supersedes_check: agents/delivery/generates/entity2-v0.md (D1-D3 unchanged; this file does not restate them)
last_updated: 2026-09-22
sources:
  - cowork
---

# entity2-v1: Iteration 1 readiness check

## What changed since entity2-v0

Nothing in D1 (start-here page), D2 (content-loop spec and ledger), D3 (verdict rule), the FAQ, or
the handover notes. I checked for two kinds of reason to revise them and found neither:

- **entityR3A (field requests from GTM):** does not exist. `agents/gtm/generates/` has no
  entityR3A file for any version. GTM has not asked for anything the artifact is missing.
- **entityR4C (usage defects from Practitioners):** does not exist. No practitioner has run the
  artifact yet, so there is no defect signal.

That means D1-D3 as written in `entity2-v0.md` are the artifact for this run. This file does not
duplicate them; read `entity2-v0.md` for the full spec.

## What Exec's certification (entity1-v1) changes for me

Exec certified PM's bet to run the existing spec, not to fund new build (`entity1-v1.md`, section
4: "No paid offer, no sales motion... this iteration"). So my iteration-1 job is narrower than
iteration 0's: confirm the spec is still fit to run, not write new documentation. The one thing
entity1-v1 adds that D1-D3 did not carry explicitly enough: the constraint on unsourced claims
(Navier-Stokes swarm, 17.2x figure, "manufactured referee", "solves") is now a hard constraint from
Exec, not just my own handover note. Handover notes in `entity2-v0.md` Part 6 already said this;
it now also binds anything GTM publishes, per Exec, not just what I wrote.

## Assumption status (D3, Part 4)

A1-A4 in `entity2-v0.md` Part 4 are unconfirmed by PM this iteration too — `entity0-v1.md`
explicitly adopts D3 "as written" and treats A1-A4 as accepted into the iteration-1 evidence
threshold, without resolving A4 (baseline posts drafted without acting on ledger reads) as
confirmed-by-PM versus Delivery's own reading. Dan has said D3 and the weights are preliminary and
may be simplified. I am not changing D3 on my own initiative this iteration — Exec certified it
"as specced." If GTM or Dan simplify the ledger or weights while running it, that is their call at
the gate and in the retro, not a Delivery rebuild.

## Cleared to run

D1-D3 are cleared for GTM to execute now: draft, Dan's publish gate, publish, read at 24h/72h/7d,
fill the ledger row, write the next change note citing rows. Ledger file:
`agents/gtm/knowledge/signal-ledger-v0.md` (currently empty — zero posts made, confirmed against
`agents/gtm/knowledge/gtm-v0.md`'s research log and `market-offer-strategy-v0.md`, which still
describes an account not yet chosen/posted from).

## One open item I cannot resolve

`market-offer-strategy-v0.md` lists four candidate handles and says "Dan picks" — no handle has
been confirmed as posting-ready in anything I can read. If GTM cannot post because the account
question is still open, that is a blocker above my authority and GTM's to raise (entityR3A to me,
or directly to Dan/Loopy) — not something D1-D3 can fix by more documentation.

## Not done, and not needed this iteration

Template files, standalone README, and implementation guide (carried forward from entity2-v0,
"not done, by choice" — Dan asked to keep them in scope for later). No field requests or defects
arrived to justify pulling them forward now.
