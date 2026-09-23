# Iteration 1 — Retro Synthesis

All four retros filed (pm log 178, exec 179, delivery 180, gtm 181). None missing.

---

## Convergent findings (independently raised by 2+ roles)

**1. No canonical "current external state" source for live facts.**
PM, Delivery, and GTM each independently identified this as a root cause of the stale account-handle flag. PM set the evidence threshold without checking it against GTM's posting gate; Delivery flagged "account handle unconfirmed" straight from `market-offer-strategy-v0.md` without verifying live account state; GTM accepted that flag without checking, then flagged it back as "stale" — still without a canonical source to confirm against. Each role inferred the handle status from scattered notes rather than a single verified fact. [pm, delivery, gtm]

**2. No single escalation register for Dan-only decisions.**
Three roles re-flagged the same two decisions — posting-gate waiver vs. Medium confidence, and account-handle confirmation — independently across multiple files. PM, Delivery, and GTM all waited on these with no shared register; GTM re-flagged them in three separate files. The loop stalled without resolution. [pm, exec, delivery, gtm]

**3. Retro files not enumerated in any agent's write boundary.**
All four roles paused on the same gap: `retro-iteration1.md` is not listed in any SKILL.md write boundary. Each wrote under owner instruction + iteration-0 precedent. Safe, but cost a judgement call each time and left a small gap in the audit trail. [pm, exec, delivery, gtm]

**4. The harness does not enforce the distinction between workflow completion and experiment execution at handoff.**
Exec's certification ("run the ten-post loop") could be misread as evidence the mechanism works; Delivery's readiness check ("cleared to run") could be conflated with progress. Both had to state scope guards explicitly because nothing in the harness enforces the distinction. [exec, delivery]

---

## Role-specific findings

**PM:** Evidence threshold was not gate-checked against downstream agent's posting gate before handoff. The ask ("run the ten-post loop") and GTM's gate (Medium confidence) contradicted each other; GTM burned a cycle discovering it. No protocol required PM to check executability before handoff. [pm]

**Exec:** No staleness bound or blocker rule for missing required inputs. Two of four required inputs (entityR2A, entityR3B) were missing or stale at every session. Flagged as gaps per standing rule 2 and proceeded on a partial input set — a workaround, not a protocol. Nothing says "missing input after N cycles → blocker, not footnote." [exec]

**Delivery:** Skill ambiguity — the "before you act" list says `agents/exec/knowledge/exec-v0.md`, the session protocol says `agents/exec/generates/entity1-v{n}.md`. Delivery read both to resolve the ambiguity. [delivery]

**GTM:** Tooling gap — the skill's listening cycle says to search X "through Claude in Chrome," but that capability is not in this runtime. Every scheduled cycle fell back to whatever browser access was available; some cycles rendered one result per query, one thread would not load, and two cycles skipped search terms on time budget. [gtm]

---

## Loopy's interpretation

The convergent findings all point to the same root cause: the harness has no single source of truth for live state and no forced reconciliation before a flag or decision request is shipped. The stale account-handle flag is the clearest symptom — three agents independently guessed at the same fact from scattered notes and all three were working from an outdated picture.

The write-boundary gap is trivially fixable (one line in each SKILL.md). The tooling gap is a runtime configuration issue, not a harness design issue. The two structural gaps — canonical external state and escalation register — are the ones that would have changed the outcome of this iteration if they had existed.

The fact that all four roles independently named the same structural gap (without Loopy's prior diagnosis leading their answers) is strong signal that it is real and load-bearing.

---

## Proposed changes requiring owner approval (not implemented)

1. **Canonical "current external state" file** — live account identity, posting-gate status, open Dan-only decisions, last-verified date. Checked at kickoff; updated before any flag ships. [convergent: pm, delivery, gtm]

2. **Single dated "inputs outstanding" register** — missing/stale required inputs (entityR2A, entityR3B), checked at kickoff, surfaced as a blocker not a footnote when missing or older than one iteration. [exec]

3. **Gate-check the evidence threshold before handoff** — every required action must clear the downstream agent's gates; any gate that must yield becomes one dated decision request in the register above. [pm]

4. **Enumerate `retro-iterationN.md` in each agent's write boundary.** [all four]

5. **Add a staleness bound and single escalation path for required inputs.** [exec]

6. **Fix GTM's listening-cycle tooling instruction** to match available runtime capabilities. [gtm]

7. **Resolve Delivery's skill ambiguity** (Exec brief path listed in two places). [delivery]

---

## Missing retros

None. All four roles filed.

---

## Iteration status (kept distinct)

- **Workflow completion:** done — kickoff → role outputs → YAML updates → handoff lines → this retro.
- **Experiment execution:** the ten-post loop was never run (blocked on posting-gate/confidence tension and account-handle question).
- **Hypothesis outcome:** unchanged — zero direct mechanism signal, positive or negative.
- **Formal closure:** this retro. No hypothesis is confirmed or disconfirmed.
