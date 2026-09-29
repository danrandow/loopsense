---
name: entity1-v0
description: Re-certified bet and brief from Exec to Delivery and GTM. Iteration 0, rebuilt on the PM's 2026-09-21 revision of entity0.
entity: entity1
direction: forward
from: actor1 (Exec)
to: actor2 (Delivery), actor3 (GTM)
iteration: 0
status: certified-conditional
based_on: agents/pm/generates/entity0-v0.md (revised 2026-09-21)
supersedes: brief of 2026-09-17 (kept in agents/exec/research/exec-v0-prev-2026-09-17.md)
last_updated: 2026-09-21
sources:
  - cowork
---

# Certified Bet & Brief — Iteration 0

## Decision

**Certified**, low-medium confidence on the problem, low on the mechanism. Mandate: build the artifact and run iteration 0 end to end. Resources: Dan's time, AI agents, public tooling. Nothing else.

Certification is conditional on the PM answering the questions in `entityR1-v0.md`. **Delivery does not wait for those answers.** Everything in section 5 can start now, and none of it depends on how the PM resolves them.

## The bet, in Dan's terms

Goal: a knowledge-work loop that can tell whether its output was any good **without a human having to verify it**. That dependence is what we mean by the verification gap.

Mechanism: the world responds to the work (replies, follows, clicks, forks, pipeline). That response returns through a defined return flow to the actor who produced the work. The actor changes what it does next. We measure whether it improved.

Claim, held lightly: this **partly** closes the gap. We do not claim to solve it. Dan is the source of the environmental-feedback insight; it replaced the earlier "manufactured referee" framing, which the PM has explicitly dropped.

Human role in iteration 0: Dan keeps a **publish gate** (safety, brand, accounts). He does not grade quality. Whether that separation holds is itself something we measure (5.3).

## 1. Who is the customer

**Iteration 0's real customer is ourselves.** The @loopsense content loop is the only place we can get real environmental signal this iteration.

**External target (hypothesis, not yet located):** people who build multi-agent systems for knowledge work (discovery, research synthesis, strategy, content) and are currently the referee themselves: they read the outputs and decide. Their own words, from GTM's verbatims:
- "who even decides which agent is right"
- "Can I identify which part of my system actually failed?"
- "agents just sit idle waiting on humans to referee"
- "you went back to running a single Claude"

Current tools: LangGraph, CrewAI, AutoGen, or one Claude plus manual review. Where they talk: X.

**Not, this iteration:**
- Hobbyist creators. @henrikhinai has the best quote but is a content creator, not a builder for a customer; he is a voice, not a buyer.
- Regulated repetitive work. Grep.ai serves it commercially.
- Enterprise buyers, and coding-agent users (verification is free there).

Honest status: GTM has found zero people who match this profile and are reachable. Finding five is GTM's first job.

## 2. Positioning (one sentence)

For people building multi-agent knowledge-work systems who are stuck being the referee because nothing tells them whether the output was good, Randow Maps is an open, YAML-defined topology that routes the real-world response to the work back to the agent that produced it, so the loop can learn whether it improved without a human grading it. Unlike LangGraph, CrewAI and AutoGen, which route work between agents but not outcomes back, and unlike simulated-persona tools (loopi.tech), we use what the world actually did as the grader.

**Language rules for Delivery and GTM:**
- Use practitioner phrases ("who decides which agent is right", "which part failed"), not ours.
- Do not describe us as a "manufactured referee". The PM dropped that framing.
- Say "partly closes", never "solves".
- Explain "consideration" before using it.
- **Do not use the Navier-Stokes swarm claim anywhere public.** Nobody has sourced it (GTM flag, unresolved).

## 3. Investment thesis: why now, why this

- **Why now:** "verification gap" is now organic vocabulary (8+ independent posters in 10 days, per GTM; also a trend in the Fall 2026 State of AI Report, per GTM). People are asking "who decides"; nobody is answering with outcomes.
- **Why this:** for complex work you cannot write the test before the loop runs, so the only honest verifier is what the environment does afterwards. Dan's insight: stop building a better judge; look past the right-hand end of the workflow. The piece nobody sells is the return edge that carries that response back to the right actor.
- **Caveat:** "nobody sells it" is absence of evidence from one channel (X) and five listening cycles.
- **Cost of being wrong is low:** the test runs on our own content, at Dan-time cost only.

## 4. Constraints: what is off the table

- No code runner. The artifact is YAML + Markdown; practitioners bring their own agents.
- No judge or referee agent inside the loop. An LLM-as-judge would void the test. If Delivery believes one is needed, flag it to Exec; do not add it.
- The return signal must be **real platform data**, not simulated or estimated.
- No enterprise sales, no paid plans, no hiring.
- No posting without Dan's OK. Never touch @danrandow. Dan decides when posting starts.
- Build only what practitioners have asked for, or what this brief names.

**I revoke certification if:** an existing tool already provides outcome-return topology for knowledge work; environmental signal cannot be routed at all; after two full iterations the loop's behaviour does not change in response to signal, or Dan overrides quality in the same way every time (PM's counter-evidence thresholds a/b/c); or the looped outputs are worse than the baseline.

## 5. What Delivery builds (priority order)

**D1. Practitioner-readable description (entity2, the current top gap).**
A "start here" page. It contains: the one-sentence positioning; the problem in practitioner words; a worked example (the @loopsense content loop); how to fork the map and run one iteration with YAML + Markdown and your own AI agent; and a short "tested vs not tested" box, since nothing has been tested yet. Two pages at most.
*Acceptance:* a cold reader (Dan, or someone outside the project) can say back what it does in one sentence.

**D2. Content-loop spec (the iteration 0 experiment).**
Describe the concrete topology for the @loopsense content loop using the existing map vocabulary. Flow: draft, Dan publish gate, post, the world responds, signal read, return edge into the drafter's knowledge file, next draft. Include the **signal ledger**: one row per post with post id, date, angle tested, raw metrics read at 24h and 72h (and 7d where available), ICP-fit responses (handle plus reply/follow/fork), and "what the drafter changed next and why."
*Metric weights:* an ICP-fit reply outranks any reply, which outranks reposts, which outrank likes and impressions.

**D3. Pre-registered verdict rule (write it before the first post).**
A rule set that decides "did the loop improve" with no human judging quality:
1. Baseline: the first 5 posts on the verification-gap angle.
2. After each read, the drafter writes what it will change, citing ledger rows.
3. Verdict window: posts 6-10.
4. Improved = a higher share of posts with at least one ICP-fit response, or a higher median weighted score, than baseline, **and** every change traceable to a ledger row.
5. State plainly that n=5 vs n=5 on a small account is a directional go/no-go, not proof. Do not overclaim.
6. **Human-override log:** for every draft, record whether Dan edited or rejected it and whether the reason was safety/brand or quality. A falling quality-override rate is the direct evidence for "no human verification needed."

*Sequencing:* D1 and D2 in parallel; D3 before the first post. Iteration 0 is the team learning to work together, so the posting gates and verbatim counts are guidance, not blockers. Dan decides when to post.

## 6. Success

**Two-week loop (check first):**
- Week 1: D1-D3 done; first post out; 5 ICP-matching profiles identified (public repo or post showing agent work plus knowledge-work now).
- Week 2: signal ledger has 5 posts with 24h/72h reads; at least one ICP-fit resonance (reply, repost, DM, follow, fork, "yes that's the problem"); PM has updated the bet from the signal, not from internal reasoning.
- **Learning signals to watch:** zero resonance after the first offer plus 5 targeted practitioners means change the offer before posting again; a ledger that cannot be filled (signal not routable) means stop and report.

**90 days (checkable):**
1. At least 5 practitioners can describe what it does without prompting.
2. At least 1 practitioner has forked the template and run one iteration.
3. At least two full loop iterations run, each drafter change traceable to a ledger row, with the quality-override rate reported.
4. GTM's signal confirms or redirects the problem framing, using real verbatims.
5. The PM has changed the bet at least once because of practitioner or ledger signal.

## 7. Open items for Dan (Loopy)

- **Signal access:** GTM will pull X analytics and feedback for the ledger. No decision needed.
- **Stale files:** `entity0-v0.md` footer says entityR3 is unfiled (it is filed). `iteration-0.yaml` notes still call the knowledge-file read "the manufactured referee". Dan is fixing the scenario title.
- **Missing inputs:** no `entityR2A` and `entityR3B` reports zero pipeline. That is expected in iteration 0; cost analysis is deferred, not needed yet.
