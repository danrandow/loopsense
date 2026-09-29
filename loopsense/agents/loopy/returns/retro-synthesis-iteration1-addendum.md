# Iteration-1 retro — addendum: owner decisions and a correction

**Date:** 2026-09-23 · **Responds to:** `agents/loopy/returns/retro-synthesis-iteration1.md`
**Status:** decisions recorded. Items 3, 4 and 7 implemented (log 184–190). Items 1/2/5 and 6
returned as draft proposals only (log 192–193), not implemented.

The four role retros (`agents/{pm,exec,delivery,gtm}/generates/retro-iteration1.md`) and the
synthesis itself are preserved unchanged as historical records. This addendum records the
owner's response and one correction to the synthesis.

## Correction: the synthesis overstated the convergence

The synthesis reported "no canonical current external state source" as a convergent finding
across all four roles, and lumped the account/gate questions together with Exec's missing-input
findings. The retros support a more careful reading:

- **PM, Delivery and GTM** converged on **live external state** — account identity and
  posting-gate status — each guessing it from scattered notes and each shipping or re-flagging
  a stale account-handle picture.
- **Exec** primarily identified **stale or missing internal inputs** — `entityR2A` never
  produced, `entityR3B` still an iteration old.

These problems are related — both are "check a fact before acting on it" failures — but they are
not identical: one is about live market/account facts outside the repo, the other about
completeness and freshness of the repo's own entity flows. The synthesis also conflated the
account/gate questions (which are owner-decision routing problems) with Exec's missing
entityR2A/entityR3B inputs (which are input-completeness problems). Convergent findings 1 and 2
should be read as covering the first problem; the second is best read as Exec's role-specific
finding, echoed by PM's and Delivery's input-flag experiences.

## Owner's primary lesson

The most important finding is that the internal workflow completed while the actual experiment
never ran and produced no new hypothesis evidence. **Iteration 2 must be designed around
obtaining real external evidence, or explicitly stopping when that cannot happen — not merely
completing another artifact loop.**

## Decisions on the seven recommendations

1. **Canonical external-state file — not created as a separate file.** Consolidated with items 2
   and 5 into one lightweight proposal using the existing iteration/map YAML
   (`harness-proposal-state-and-inputs-v0.md`, draft).
2. **Inputs-outstanding register — not created.** Consolidated likewise.
3. **Executability/gate check before handoff — approved, kept minimal.** Implemented as exactly
   one handoff check in `knowledge/standing-rules.md` (rule 9): no new process, no register.
4. **Enumerate `retro-iterationN.md` in every agent's write boundary — approved and
   implemented** across all five `SKILL.md` files (pm, exec, delivery, gtm, loopy).
5. **Staleness/escalation mechanism — not implemented separately.** Consolidated with items 1
   and 2.
6. **GTM tooling correction — necessary, but wording split by portability.** The canonical
   instruction must remain runtime-neutral; runtime-specific OpenClaw guidance belongs in the
   OpenClaw adapter. Proposed wording returned as a draft
   (`harness-proposal-gtm-tooling-v0.md`), not implemented.
7. **Delivery's Exec-source paths — approved and implemented.** Resolved to the actual
   canonical handoff source: `agents/exec/generates/entity1-v{n}.md`. Delivery's "before you
   act" list item 5 also mislabelled the aligned bet as `entity1`; corrected to `entity0`.
