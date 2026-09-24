# Iteration 2 checkpoint — owner answers and framing feedback

## Context

PM's iteration-2 framing (`agents/pm/generates/entity0-v2.md`, authoritative visible record `ed68ed2`) put three items to Dan: run the evidence loop parallel with or sequenced after Delivery's mechanism analysis; root README ownership and public scope; and sign-off on the explicit-stop framing.

## Decision

Dan, 2026-09-24 11:06 UTC:

1. **Sequenced:** the ten-post evidence run runs **after** Delivery's mechanism analysis, not in parallel — this overrules PM's parallel call.
2. **README:** the root README is authored by **Delivery, under Dan's direction**. Public scope: everything needed for someone else to get Loopsense working, as long as our rules apply (standing rule 8 review before publication; no credentials or private material). Delivery's README blockage is cleared.
3. **No strict stop sign-off:** if external evidence cannot be obtained, iteration 2 does other learning before it stops. And it is premature to stop the claim after one failed test — one failed test is evidence, not a claim-killer; the claim survives it.

Feedback on the framing: the proposed iteration-2 question is far too long — make it one tight sentence.

## Why

The claim should not die on a single failed test; accumulating evidence across iterations is the honest read. Sequencing keeps the first live run informed by the mechanism analysis. Full public replication guidance is the credibility goal, bounded by the team's publishing and privacy rules.

## Consequences

PM revises `entity0-v2.md` (editable while iteration 2 is open) and `iteration-2.yaml`'s scenario line and entity0 override: short question, amended counter-evidence/stop logic (failure to obtain external evidence leads to other learning first), explicit Delivery-analysis-before-run dependency. The forward pass is Exec → Delivery → GTM with GTM's evidence run after Delivery's analysis. Out of date: PM's parallel resolution (`ed68ed2` item 1), the strict "explicit stop" framing in the evidence threshold as originally drafted, the README blockage in `agents/loopy/returns/iteration-2-owner-checkpoint.md`, and the question sentence as originally proposed.