---
name: entityR1-v0
description: Viability signal from Exec back to PM. Iteration 0. Certified with questions and requests.
entity: entityR1
direction: return
from: actor1 (Exec)
to: actor0 (PM)
iteration: 0
status: open
last_updated: 2026-09-21
sources:
  - cowork
---

# entityR1: Viability Signal (iteration 0)

## Decision: Certified, low-medium on the problem, low on the mechanism

The revised entity0 changed the mechanism (from a manufactured referee to real-world feedback), and my earlier certification no longer described it. Dan asked me to re-brief and get Delivery building, so I certified on Dan's reframe (**the aim is to not need a human to verify**) and wrote the brief in `agents/exec/generates/entity1-v0.md`. The certification is conditional on you answering the questions below. Delivery is not waiting for them.

Inputs: entity0-v0 (rev. 2026-09-21), entityR3-v0, entityR3B-v0. **No entityR2A exists**, and R3B reports zero pipeline. That is why confidence is low.

## Business model thesis

Attention-first, open spec, revenue later. No revenue target this iteration.
- **Path A (precedented):** open spec, then a hosted service that carries outcome signals back into loops. Precedents: LangChain to LangSmith; Hugging Face Hub. The paid layer would be connectors and a ledger that the open version cannot provide.
- **Path B (nearest, hypothesis):** loop-design work for teams, from Dan's consulting base. Not enterprise sales, so it needs Dan's call.
- **Evidence:** loopi.tech charges PMs $10-40/month for "validate before you build", so buyers pay for validation; but it is a different buyer and uses synthetic personas. Grep.ai is commercial in regulated repetitive work.
- **Untested:** everything above; GTM says attention-first is untested.

## Questions for the PM (please answer in entity0-v1 or the iteration log)

1. **Referee or environment?** `iteration-0.yaml` notes still call the knowledge-file read "the manufactured referee" and name Dan as referee; entity0 rejects manufactured referees. Which is the claim? My suggestion: the environment is the verifier; the knowledge-file read is a consideration mechanism (better inputs), not verification.
2. **Who is the buyer of the environmental-feedback mechanism?** Same orchestration engineers, or someone else? GTM found no practitioner who says anything like environmental feedback (they say "who decides" and "which part failed"). Which domain comes first after content?
3. **What does "verified without a human" mean operationally?** I drafted a pre-registered rule for Delivery (D3 in entity1: baseline of 5 posts, verdict window posts 6-10, ICP-fit responses as the metric, human-override log). Accept, amend or replace it.
4. **Signal vs noise:** @loopsense has a very small audience. What n makes engagement data usable? If it cannot support even a directional read, we may be measuring noise.
5. **Contamination:** Dan holds the publish gate and voice. How do we separate his safety/brand edits from quality judgment, so the test isn't quietly a human-verified one?
6. **Counter-evidence (b) "no observable change in actor behaviour":** what counts as observed change? Delivery's ledger records what the drafter changed and why; is that enough?
7. **The topology-vs-loop-vs-pair comparison** (iteration-0 scenario title) was never run and entity0 no longer relies on it. Dropped or deferred?
8. **Sources for public claims:** the Navier-Stokes swarm claim (GTM found no source); "every great AI win has binary verification"; the 17.2x error-amplification figure. Verify before any public use.
9. **"Fault localisation"** (which node failed), suggested by GTM from @heyanjey: in the value proposition or not?

## Requests

- Fix the entity0 footer: entityR3 is filed, and cycles run to 2026-09-21.
- Revisit your confidence after Delivery's D1-D3 and the first ledger reads.
- Note that entity0 says practitioners feel the gap "from GTM verbatims". The clean signal is thinner than that: the best quote is from a content creator (downgraded) and another is from a competitor. Reword to match R3.
- Say which external customer segment iteration 1 should chase, so GTM can target it.

## What would change my certification

- **Up:** an ICP-matching practitioner who describes the referee problem in their own words; a ledger showing drafter changes traceable to signal; a falling quality-override rate.
- **Down / revoke:** an existing tool providing outcome-return topology for knowledge work; signal that cannot be routed; the loop's outputs worse than baseline; two iterations with no change in drafter behaviour; Dan overriding quality the same way every time.

## Confidence

Low-medium that the problem is real and named; low that outcome return closes it; cannot forecast revenue.
