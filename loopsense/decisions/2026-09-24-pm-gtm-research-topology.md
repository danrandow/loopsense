# PM/GTM research topology — ownership clarification

## Context

The instruction files disagreed on who owns primary market research and practitioner listening. `agents/pm/SKILL.md` claimed the PM was "the raw signal collector — not GTM", while `knowledge/team-registry.md` and `base.yaml` put listening with GTM. The PM skill also referred to an undefined "Sales" role and a "weekly listening reports" cadence, and its session reading omitted `entityR4`.

## Decision

Dan approved this clarification on 2026-09-24. GTM is the primary market researcher and practitioner listener and owns the practitioner-facing offer (`entity3`). Dan's DM directions to GTM are raw research leads, questions or hypotheses to filter and test — not validated findings and not a bypass around PM. Substantiated, synthesized market insights reach PM through `entityR3`; PM also receives direct practitioner `entityR4`. PM remains the product interpreter and evidence integrator with final authority over the iteration question and the aligned bet. Entity topology unchanged.

## Why

The old wording put two agents on the same listening work, left the offer's owner undefined ("Sales"), and let DM-sourced ideas read as validated findings. Separating primary research (GTM) from interpretation and decision (PM) matches the existing entity routing in `base.yaml` without changing it.

## Consequences

`agents/pm/SKILL.md`, `agents/gtm/SKILL.md` and `knowledge/team-registry.md` now state the split. PM's session reading includes `entityR4`; GTM's includes `entityR4B` when present. The "PM as primary market researcher" and "Sales" wording is gone, and the registry's entityR4A/R4B/R4C paths are complete. Out of date: any reading of the PM skill as a listening charter. `base.yaml` needed no change.
