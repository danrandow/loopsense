---
name: entity3-v1
description: The market offer, iteration 1 — PRE-RELEASE DRAFTS ONLY. Nothing here is posted or scheduled to post.
entity: entity3
direction: forward
from: actor3 (GTM)
to: actor4 (Practitioners)
iteration: 1
status: pre-release-draft (blocked)
last_updated: 2026-09-22
sources:
  - cowork
---

# entity3 — Market Offer (iteration 1)

**STATUS: PRE-RELEASE DRAFT. NOTHING BELOW HAS BEEN POSTED, AND NOTHING IS SCHEDULED TO POST.**
Per SKILL.md's posting discipline, all three gates must clear first: 3+ verbatims (met), a Delivery
artifact (met, entity2-v0/v1), and PM certification at Medium confidence (**not met** — entity0-v1
holds it at Low-Medium on the mechanism). This file exists so drafts are ready the moment the gate
clears, and so Dan can review wording before anything goes anywhere. GTM will keep noting pre-release
drafts this way going forward (SKILL.md updated 2026-09-22, log id 152).

## Candidate replies (postable now, if the gate is waived for replies specifically — Dan's call)

These follow `market-offer-strategy-v0.md`'s comment-first approach: curious questions, not pitches,
no mention of Loopsense/Randow Maps, using language practitioners actually use.

### Reply to @jaketselby (live thread, found 2026-09-22 via omarsar0's harness post)
> "Rules/skills/roles/workflows/hooks — curious how you handle it when two of those roles produce
> outputs that quietly disagree with each other. Anything catch that, or is it on you to notice?"

Rationale: he's the strongest ICP-adjacent builder found this iteration (open-source harness,
verified). This question tests our exact hypothesis (does he have a verification mechanism, or is
he the human referee) without pitching anything.

### Reply to @omarsar0's NVIDIA harness thread (2101074795643494546)
> "This works because code has a verifier baked in — tests, compiler, a real pass/fail. What's the
> equivalent for the harness layer when the task is judgment work and nothing tells you if the
> output's actually good?"

Rationale: names the verification-gap distinction (code vs. knowledge work) in the exact place a
technical audience is already discussing harnesses, without using our own jargon.

### Reply template for a future "verification gap" post (no live target yet)
> "'Which part of the system failed' seems to be the real question people are landing on, not
> 'which agent is right.' Anyone found a way to answer that for non-code work, or is it still
> eyeballing the output?"

Rationale: uses @heyanjey's and others' actual phrasing (gtm-v0.md, 2026-09-20/21 cycles), not ours.

## Candidate original thread (blocked — requires full gate, including Medium confidence)

**Working title:** "A thread built by the pipeline it's about"

> Not "here's our product" — a plain account: we run PM → Exec → Delivery → GTM as actual agents
> with actual handoffs, and the thing we can't answer yet is the same thing you're all asking —
> "which part actually failed," "who decides which agent is right." We don't have that solved.
> Here's what we tried and what happened.

Rationale: the dogfooding-as-proof angle from `market-offer-strategy-v0.md`. Deliberately does not
claim a solved problem — confidence is Low-Medium on the mechanism, and entity0-v1 (Exec's Q8) bars
unsourced or overclaiming language from any public draft. This is the honest version: an account of
an attempt, not a pitch.

**Do not post until:** PM certifies Medium confidence (or Dan explicitly waives that gate and says
so), AND a handle is confirmed live for posting (already resolved — @loopsense is live and used for
follows; the "handle unconfirmed" flag in entity2-v1/iteration-1.yaml referred to
`market-offer-strategy-v0.md`'s stale candidate list, not @loopsense itself. Worth a note back to
Delivery/Dan to clear that flag since it's now stale).

## What none of these drafts do

Per Exec's constraint (entity0-v1, answer to Q8): no reference to the Navier-Stokes swarm claim, the
17.2x error-amplification figure, "manufactured referee," or "solves." None of the drafts above use
any of these.

## Flags

**PM / Dan:** The account-handle blocker flagged in entity2-v1 and iteration-1.yaml looks stale —
@loopsense is live and already used for follows (see gtm-v0.md). Recommend clearing that flag or
confirming it means something else.
**Delivery:** No change requested to D1-D3; these drafts are GTM's own copy, not a request for new
artifact work.
