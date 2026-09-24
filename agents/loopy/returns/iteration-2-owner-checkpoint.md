# Iteration 2 — owner checkpoint (framing before downstream execution)

**Date:** 2026-09-24 · **Trigger:** "Start Iteration 2" with owner input · **Status:** paused at
the owner checkpoint, per `workflows/start-next-iteration.md` and the owner's direction that no
downstream execution (Exec, Delivery, GTM) begins until the framing and required owner decisions
are settled.

## What is done

- Retro reconciliation and the one-combined-question checkpoint: approved 2026-09-24.
- **Harness improvements applied and pushed (`42e6bb6`):** Change A — one State & inputs kickoff
  line in all five `SKILL.md` files (retro items 1/2/5, consolidated);
  Change B — GTM listening step runtime-neutral, OpenClaw tool mapping in the adapter (item 6).
  Decision records: `decisions/2026-09-24-state-and-inputs-block.md`,
  `decisions/2026-09-24-gtm-tooling-wording-split.md`. Items 3/4/7 were already implemented and
  were not re-proposed.
- **Iteration-2 skeleton created and pushed (`f9a4192`):** direction, carry-forward state and the
  dated State & inputs block in `iteration-2.yaml`; scenario marked provisional for PM.
- **Owner decisions recorded (`decisions/2026-09-24-posting-gate-and-account.md`):** the evidence
  run may proceed at Low-Medium confidence (scoped to the run; the normal Medium gate stands for
  other original posts); `@loopsense` confirmed as the posting account, stale handle flag cleared.
- **PM kickoff run and pushed (`1759578`):** `agents/pm/generates/entity0-v2.md`,
  `agents/pm/knowledge/pm.md` iteration log, `iteration-2.yaml` scenario line + entity0 override.
  Verified: paths within PM's boundary, `git diff --check` clean, YAML read-back, standing rule 9
  flags recorded (entityR2A never produced, entityR3B stale at v0, entityR4 absent).

## PM's proposed iteration-2 question (the tested sentence)

> Iteration 2 tests whether a system without a continuous human can actually close the
> verification gap: real external evidence — a use-case catalogue grounded in real unsolved
> problems and the groups who have them, plus the first live evidence run — together with an
> honest mechanism analysis must yield a concrete sense-observe-interpret-learn mechanism, or the
> claim stops.

## The aligned bet, in brief (full text: `agents/pm/generates/entity0-v2.md`)

The verification gap is real and named in the wild, and no located alternative owns it
(loopi.tech = synthetic personas; Grep.ai = regulated work with rule-set verification) — but the
mechanism has zero direct evidence across two completed iterations because the test has never
run, and the buyer is unidentified after seven empty listening cycles. PM's decision: **continue,
designed around real external evidence with an explicit stop**. Three evidence moves (the
now-unblocked ten-post evidence run; the grounded use-case catalogue, reframing the ICP search as
"find real problems, then their people"; Delivery's mechanism analysis through the
sense–observe–interpret–learn frame, topology not presumed) plus one credibility deliverable (the
README). Evidence threshold: all three of grounded catalogue, concrete mechanism statement, first
live run. Counter-evidence (a)–(d) any one pivots or stops — including honest failure to obtain
external evidence. Confidence: Low-Medium on the problem, Low on the mechanism. New caution
integrated: positioning vocabulary is being commoditized by unaffiliated content accounts;
differentiation must come from demonstrated mechanism and evidence.

## What PM needs from each downstream role

- **Exec:** viability lens on the reframed bet; business-model question treated as fresh; state
  whether it proceeds on partial inputs (entityR2A never produced, entityR3B stale at v0).
- **Delivery:** the mechanism analysis — central question + Dan's seven sub-questions, no
  prescribed conclusion, "what exists vs must be built" made concrete; entityR2A if warranted.
  README execution pending the ownership decision below (named per standing rule 9).
- **GTM:** run the evidence run (gates cleared; no unsourced public claims in drafts; weigh the
  commoditization risk before finalising the posting voice) and build the grounded catalogue with
  the groups to listen to; Dan's direct directions are raw leads filtered through entityR3.

## Owner decisions needed before Exec, Delivery and GTM run

1. **Run in parallel or sequence?** PM proposes the ten-post run proceeds alongside Delivery's
   mechanism analysis, accepting the run's interpretation may be reshaped by the analysis. The
   gate waiver implies the run proceeds; confirm, or overrule and sequence the analysis first.
2. **README ownership and scope.** The root README sits outside every agent's write boundary.
   Who authors it (Delivery under your direction, or Loopy?), and how much internal DNA/relational
   material goes public (standing rule 8 review applies before publication).
3. **Sign off the stop framing.** If the catalogue cannot be grounded in real problems or the run
   cannot happen, iteration 2 ends with an explicit stop recommendation rather than delivered
   artifacts — this changes what "done" means for the iteration.

## Housekeeping noticed during the pass

- `.gitignore` was modified in the worktree outside any role's boundary after PM had settled and after boundary verification; its comment attributes the change to Dan
  (2026-09-24). Left in place, uncommitted and reported, not absorbed.
- Renderer not checked for `iteration-2.yaml`, per the workflow's standing caveat.

Rule 8 check on this briefing: `@loopsense` is the project's own account (factual); no
third-party personal information; neutral tone. Result: pass.
