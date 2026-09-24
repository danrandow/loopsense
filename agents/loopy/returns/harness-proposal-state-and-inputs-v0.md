# Draft proposal — state & inputs (consolidates retro items 1, 2, 5)

**Status:** DRAFT for Dan's review. Not implemented. Responds to owner instruction 2026-09-23:
return one consolidated, lightweight proposal for items 1, 2 and 5 that uses the existing
iteration/map YAML where possible.

## The problem (two distinct gaps, not one)

Correcting the synthesis's conflation (see `retro-synthesis-iteration1-addendum.md`):

- **Live external state** (PM, Delivery, GTM retros): account identity, posting-gate status and
  open owner-only decisions live in scattered notes with no last-verified date. Three agents
  independently guessed the account-handle picture and shipped or re-flagged it stale.
- **Internal input freshness** (Exec retro): required inputs (`entityR2A`, `entityR3B`) can be
  missing or a full iteration stale with no bound. Exec certified on a partial input set and had
  to footnote it; the same gaps were re-discovered and re-flagged by three roles.

Both are "check the fact before acting" failures, but one concerns facts outside the repo and
the other the repo's own entity flows. One lightweight mechanism can cover both — without a new
file, a register, or an escalation process.

## Proposal: a `State & inputs` block in `iteration-N.yaml`'s map notes

`iteration-N.yaml` already carries open items in `map.notes` (see iteration-1.yaml). Add one
dated block there, maintained by whoever verifies a fact (the verifier updates the date), read
at kickoff by every agent:

```yaml
  notes: |
    ...

    **State & inputs — last verified YYYY-MM-DD**

    Live external state:
    - Account identity: @loopsense, live, confirmed <date> (whoever confirmed it)
    - Posting gate: original posts require PM Medium confidence (SKILL.md); current: Low-Medium — gate closed
    - Open owner-only decisions: <one line each; empty when none>

    Required inputs (freshness bound: one iteration):
    - entityR2A: missing (never produced) — flagged, Exec must certify on partial inputs or wait
    - entityR3B: current (v1, this iteration) / stale (v0, one iteration old) — ...
```

### What makes it lightweight

- **No new file** (item 1): the iteration/map YAML is already the shared state carriers, already
  read at kickoff and already logged under rule 6.
- **No register** (item 2): the block is prose inside an existing notes field, not a tracked
  list with its own lifecycle.
- **No escalation mechanism** (item 5): staleness bound is stated as a field convention — an
  input older than one iteration is marked `stale` in the block and named as a gap at handoff
  (standing rule 9's one check, already implemented). Naming a stale input is the escalation.

### Split of responsibilities

- Whoever confirms a live fact (any agent, or Dan via Loopy) updates its line **and its date**.
- Agents read the block at kickoff (it rides in the iteration YAML they already read) and verify
  any flag against it before shipping the flag.
- A required input that is missing or older than one iteration is marked as such in the block and
  named in the handoff that needs it; the consumer states whether it proceeds on partial inputs.

### Open questions for Dan

1. Should the block live in `iteration-N.yaml`'s map notes (as proposed) or also mirror a line
   into `base.yaml`? Proposal: iteration YAML only — `base.yaml` stays structural.
2. Who owns the posting-gate line — GTM (who reads it) or PM (who sets confidence)? Proposal:
   PM sets the confidence figure, GTM keeps the gate line current.

## Rule 8 mechanical-scan review (2026-09-23)

Flag: `@loopsense` in the YAML sketch above (the account identity line). Reviewed per standing
rule 8:

- **Source present:** yes — this is the project's own account, documented in
  `agents/gtm/knowledge/gtm-v0.md`; the line is illustrative template content.
- **Fact/inference distinction:** factual (account identity), with a `<date>` placeholder marking
  the line as illustrative, not a claim about any person.
- **Unnecessary personal information:** none — project account only; no third-party details.
- **Tone:** neutral; no characterization of any person or account.
- **Result: pass** — no revision required.

This review covers the sketch line above and its references in the audit trail. The change set's
other changed lines contain no public handles or profile links, email addresses or phone numbers.
