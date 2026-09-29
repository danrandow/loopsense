# Public-account and rule 8 review — GTM pass material (iteration 2)

**Date:** 2026-09-24 (material dated 2026-09-25 NZ) · **Reviewer:** Loopy (designated reviewer,
standing rule 8) · **Result: pass — mergeable to the public branch**, with two reviewer notes
for the Stage 2 publication review (not revisions).

**Material:** `agents/gtm/research/use-case-catalogue-v2.md`, `agents/gtm/generates/entity3-v2.md`
(five queued drafts), `entityR3-v2.md`, `entityR3B-v2.md`, `agents/gtm/knowledge/gtm-v0.md` run
note + run log, `agents/gtm/knowledge/publication-ledger.md` queue notes.

## Mechanical scan

- **Public handles:** ~26 practitioner, vendor and commentator handles across quotations and
  group lists — each reviewed as quotation/attribution below.
- **Profile links:** x.com status URLs — the evidence links behind every quotation (required by
  rule 8, present throughout).
- **Reputation-sensitive terms:** one mild profanity inside a verbatim quote (post 5 / P6);
  tool-failure claims about named software (LangGraph, mini-swe-agent) with linked issues —
  observable behaviour, attributed.
- **Email addresses and phone numbers:** none (ISO dates re-match the phone pattern — false
  positives, as in the README review).
- **Own/owner handles:** `@loopsense` (own account; bio quoted for the disclosure check) and
  `@danrandow` (owner handle in a run note) — factual, previously reviewed.

## Flagged passages

1. **Practitioner verbatims (catalogue P1–P8 and posts 1–5).** Source present: a URL per quote,
   with "(URL not seen)" tagged where absent ✓. Quotation vs inference: quotes in quote blocks
   with attribution; GTM's analysis explicitly tagged [Our Interpretation]/[Hypothesis] ✓.
   Uncertainty explicit: evidence-quality tags (older than 30 days, secondhand, URL not seen),
   role tags (vendor, analyst, commentator, guide writer), duplicate-phrasing caution on P4 ✓.
   Tone: quotes are speakers' own words about their own experience; our text addresses evidence
   and positioning, never character or motive ✓. **Result: pass.**

2. **P5 secondhand anecdote** (unnamed "director of alignment at Meta's Superintelligence Lab";
   agent deleted emails). Secondhand-tagged (via @CoreyGallon's talk summary), the talk itself
   marked unverified, the person unnamed, the content observable work behaviour — no character
   speculation, no sensitive personal information. **Result: pass.** Note: if the underlying talk
   is ever checked and the person named, re-review before any public use of that detail.

3. **Post 5 verbatim with mild profanity** (@J4X_Security's own words, self-deprecating, linked).
   Fair direct quotation. Note for the Stage 2 reviewer to decide whether to trim for tone — not
   a rule 8 violation.

4. **Celebrity-attribution accounts** (@hanakoxbt, @Mahaximus_, @iiiichigo_chan). Excluded from
   evidence under the unverified-attribution rule; referenced only as vocabulary-commoditisation
   signal (observable posting behaviour). **Result: pass.**

5. **Competitive/product references** (LangGraph, mini-swe-agent, Grep.ai/AgentRun, loopi.tech).
   Observable behaviour and positioning, sourced or marked monitor-only; role tags applied.
   **Result: pass.**

Rule 8 checklist: source present ✓ · fact/inference distinction ✓ · unnecessary personal
information ✓ · tone ✓ · identifying the accounts adds legitimate value ✓ (traceable evidence is
the catalogue's purpose).
