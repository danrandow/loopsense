# State & inputs block in the iteration YAML

## Context

The iteration-1 retro found three roles guessing live external state (the stale account-handle flag) and one role certifying on missing or stale internal inputs (`entityR2A` never produced, `entityR3B` a full iteration old), with no staleness bound or single escalation path. Retro proposals 1, 2 and 5 were consolidated into `agents/loopy/returns/harness-proposal-state-and-inputs-v0.md` on owner instruction 2026-09-23 (see `agents/loopy/returns/retro-synthesis-iteration1-addendum.md`).

## Decision

Dan approved the consolidated proposal on 2026-09-24. A dated `State & inputs` block lives in `iteration-N.yaml`'s `map.notes`: live external facts (account identity, posting-gate status, open owner-only decisions) and required inputs with a one-iteration freshness bound, each line carrying its last-verified date. All five agents (pm, exec, delivery, gtm, loopy) read it at kickoff and verify any flag against it before shipping. The block lives in the iteration YAML only; `base.yaml` stays structural. PM sets the confidence figure; GTM keeps the posting-gate line current.

## Why

It reuses a file every agent already reads — no new file, register or escalation process — makes "verified" versus "inferred" explicit at handoff, and replaces three parallel re-discoveries of the same gap with one dated status line. Both open questions in the draft were settled as proposed.

## Consequences

Each `agents/*/SKILL.md` carries one State & inputs kickoff line. A missing or one-iteration-stale required input is named at handoff under standing rule 9. Out of date: carrying live facts only in scattered knowledge-file notes; retro proposals 1, 2 and 5 as separate mechanisms.
