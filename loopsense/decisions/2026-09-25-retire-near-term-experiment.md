# Retire near-term-experiment.yaml

## Context

`near-term-experiment.yaml` sat in the map's scenario set as "Iteration 1: First Evidence Threshold", but it predates the iteration-0/1/2 series: the frozen ledger has no create entry for it, and its first mention is a 2026-09-17 reframe made alongside `iteration-0.yaml`. Its "Iteration 1" label collided with the real `iteration-1.yaml` (created 2026-09-22), and its content — product description, GTM listening, posting gates — had been absorbed into iteration 0's delivery job and the entityR3 flow, or superseded (the "5+ practitioners" gate; posting from Dan's personal X account).

## Decision

Dan (owner), 2026-09-25: delete `near-term-experiment.yaml` — "it's just noise". Loopy removed the file and cleaned its active references in `knowledge/reading-the-map.md`, standing rule 5, the four role `SKILL.md` write boundaries, `agents/delivery/knowledge/delivery-v0.md`'s artifact list, and `README.md`.

## Why

A superseded pre-iteration plan was presented as live map structure, and its numbering misled readers of the real iteration series. The plan itself survives in git history and in the frozen ledger.

## Consequences

The scenario set is now `base.yaml` + `moonshot.yaml` + `iteration-N.yaml`. Frozen historical outputs keep their references unchanged: `agents/delivery/generates/entity2-v0.md` (quotes standing rule 5 as it stood) and the frozen legacy ledger (`loopsense.log.json`, `history/`). The open "5+ practitioners vs 3+ verbatims" gate flag in `agents/gtm/generates/entityR3-v0.md` is unaffected by this change; the "5+" wording is confirmed dead.
