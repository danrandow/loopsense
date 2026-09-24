---
name: pm-knowledge
description: PM running knowledge — pointer to the current bet, practitioner signals, sources, iteration log. The bet itself lives in agents/pm/generates/.
---

# PM Knowledge — Loopsense Agent Team

## Current bet

The aligned bet (entity0) is versioned, one file per iteration: `agents/pm/generates/entity0-v{n}.md`. Read the highest version present. Current: `entity0-v2.md` (iteration 2, open). This file holds what the PM learns around the bet, not the bet itself.

---

## Practitioner signals — iteration 0

> "Models aren't becoming gods. They're hitting a hard verification wall." — @Fargonavt, X, 2026-09-17

> "The Verification Gap — A major study across 393 benchmarks: Cyber agents: 92/100 (instant code feedback). GUI/OS agents: 40/100 (messy real-world proof). The bottleneck isn't raw intelligence. It's verification." — @Fargonavt, X, 2026-09-17

> "in multi-agent knowledge work, an inability to empathize / negotiate well. very different fails, same root" — @danielrupawalla, X, 2026-09-17

> "We've gone from brittle agents that made good demos, to putting agents on rails (static workflows with LLM loops) to make them work, and back to building agents on top of harnesses like the Claude Agent SDK in the span of three years. Yet we still felt we had not found the right tool for the problem our customers' need us to solve." — @MiguelriosEN (Grep.ai), X, 2026-09-18

> "who even decides which agent is right" — @huaviduc753, X, 2026-09-13

Signal still missing: a practitioner describing the *experience of crossing* from code (where tests existed) to complex knowledge work (where they don't). That verbatim — "I used to have CI; now I'm just reading outputs" — would confirm the ICP framing is theirs, not ours.

---

## Sources

- Anthropic, "Patterns and Problems in Multiagent Systems" (2026)
- AI Daily Brief, "Agentic Loops for Knowledge Workers" (Sep 3, 2026)
- Simon Willison on Lenny's Podcast (Apr 2026)
- @Fargonavt (X, 2026-09-17): 393-benchmark empirical study
- @MiguelriosEN / Grep.ai AgentRun (X, 2026-09-18): 3-year practitioner journey; procedural segment

---

## Iteration log

### Iteration 0 — 2026-09-17 to 2026-09-19

- Bet defined, Exec certified, low-medium confidence
- Dogfood experiment run (self-referential); comparison conditions not run — deferred
- Delivery knowledge base and skill file created; product description not yet written
- GTM listening cycle initiated: 6 verbatims captured, 2 practitioners identified
- Team restructured to per-agent folders; renamed to Loopsense; @loopsense live
- Bet revised 2026-09-19: ICP sharpened, landscape assessed, binary verification insight added, Dan's success-criteria framing incorporated

**Bet revision rationale (2026-09-19):** Dan pushed back on the framing productively. The sharpest restatement of the verification gap is that success criteria definition costs more than the task itself — not just that verification is hard. This repositions the bet: we're not claiming to make verification cheaper. We're claiming the topology reduces the failure conditions that make the verification problem worse. And the binary verification insight (all great AI wins = binary verification) gives us a structural argument for why this domain is different, not just an assertion.


### Session — 2026-09-21

**Core insight added to bet:** Real-world feedback (engagement metrics, revenue, utilization, customer signals) flowing back through structured return flows is the mechanism by which the verification gap can be partially closed. Not manufactured referee agents. Not human inspection of handoffs. The environment generates the verification signal; the topology routes it back.

**Reframe:** The question is not whether a rubric can evaluate the output — it can't, cost-efficiently. The question is whether the work produced an outcome in the world that the world responded to measurably.

**First initiative framing:** Content generation is iteration 0's concrete test. Tweet engagement IS the verification signal. No judge agent needed — the audience judges. This generalises: product strategy → utilization/revenue; customer discovery → pipeline velocity; research synthesis → citations and adoption.

**Dogfooding as methodology:** Running the topology on our own problem and reading our own environmental signal is the primary evidence source. Iteration 0 is the experiment.

**Bet revision rationale:** Dan challenged the "loops reduce specific error class" hypothesis as insufficient — inspectable handoffs aren't enough if there's still no external verification. His reframe: look beyond the right-hand end of the workflow. The real question is whether the loop actually helps us respond better to complex needs out there. Environmental feedback is the only honest answer.

**GTM status:** Last research cycle 2026-09-18 (3 days ago). Formal return flow (entityR3-v0.md) still empty — verbatims only in gtm-v0.md. No new signal since 2026-09-18. Dan aware; handling GTM bureau directly.

### Iteration 1 kickoff — 2026-09-22

Trigger: Dan said "start iteration1". Read (in order): standing-rules.md, team-registry.md, reading-the-map.md, this file, entity0-v0, entityR3-v0 (GTM), entityR1-v0 (Exec), entityR2-v0 (Delivery), dna.md, retro-synthesis-iteration0.md, iteration-1.yaml.

Starting question asked: nothing better already exists (loopi.tech uses synthetic personas, Grep.ai owns repetitive/regulated work), but the mechanism itself has never been tested because Delivery's D1-D3 content loop has never been run — zero posts, zero ledger rows.

**Decision: continue.** Wrote `entity0-v1.md`: answered all nine of Exec's R1 questions (environment-not-referee framing accepted; D3 verdict rule accepted as-is; directional-only read given small audience; contamination handled by logging Dan's publish-gate edits separately from ledger-driven changes; topology comparison dropped; unsourced public claims barred from external drafts; fault localisation kept secondary). Sharpened iteration 1's evidence threshold to a concrete, checkable process test: run the full ten-post loop (5 baseline + 5 verdict-window), at least one ledger-cited change note in a verdict-window draft. Fixed the stale footer from v0 (entityR3 was filed, cycles ran to 09-21/09-22).

Retro synthesis read (Loopy, all four agents converged on the log-append mechanism as the friction point, not the bet). Nothing in the retro changed the bet itself — carried forward for Dan/Loopy to act on directly (standing-rules.md fixes are outside PM's write boundary).

Set `iteration-1.yaml`'s scenario line to iteration 1's actual question (run the content-loop dogfood test) and added an entity0 override pointing to entity0-v1.

Handoff: ready for Exec — say "start iteration 1" in the Exec project next.

### Iteration 2 kickoff — 2026-09-24

Trigger: Loopy, under workflows/start-next-iteration.md, owner-approved. Read (in order): standing-rules.md, team-registry.md, reading-the-map.md, this file, entity0-v1, entityR3-v1, entityR1-v1, entityR2-v1 (entityR4: `agents/practitioners/generates/` does not exist — noted per standing rule 2), dna.md, retro-synthesis-iteration1.md + addendum, decisions/2026-09-24-posting-gate-and-account.md, and iteration-2.yaml including its new State & inputs block.

Starting question asked: alternatives still do not do this (loopi.tech = synthetic personas; Grep.ai = regulated work), the problem is confirmed in the wild — but the mechanism has zero direct signal across two completed iterations because the test has never run, and the buyer is unconfirmed after seven empty listening cycles. The retro's primary lesson governs: two artifact loops, zero external evidence.

**Decision: continue — designed around real external evidence, with explicit stop.** Iteration 2 = (1) the ten-post evidence run, now unblocked by the owner decisions (Low-Medium gate waiver scoped to the run; @loopsense confirmed; stale handle flag cleared); (2) use-case catalogue grounded in real problems → groups to listen to (GTM primary researcher; Dan's directions raw leads); (3) Delivery's mechanism analysis on the central question — sense/observe/interpret/learn — without presuming topology (Dan's seven sub-questions as inputs, not solution); (4) README credibility deliverable (ownership flagged to Dan). Evidence threshold = all three of grounded catalogue, concrete mechanism statement, first live run; counter-evidence (a)–(d) includes stopping if external evidence cannot be obtained. Vocabulary-commoditization risk (entityR3-v1 addendum) integrated as a differentiation caution.

Wrote `entity0-v2.md`; set iteration-2.yaml's scenario line and entity0 override. Flags at handoff (standing rule 9): entityR2A never produced, entityR3B stale at v0 (both Exec inputs; State & inputs block current as of today), entityR4 / practitioners folder absent. Output paused at the owner checkpoint (`agents/loopy/returns/iteration-2-owner-checkpoint.md`) per owner direction.

**Visible authoritative kickoff record — 2026-09-24:** the owner required the kickoff to exist in a visible session. The hidden run's committed output (entity0-v2.md, the iteration-2 entry above, iteration-2.yaml's scenario line and entity0 override) was treated as prior draft and **adopted unchanged** — re-derived from the canonical read order in this session and judged sound against the sources. Checkpoint items resolved:

1. **Parallel, not sequenced** (PM's call under the owner's routing line): the ten-post evidence run proceeds alongside Delivery's mechanism analysis, accepting that the run's interpretation may be reshaped by the analysis — the gate waiver implies the run proceeds, and external evidence is the retro's stated priority. Dan may overrule and sequence the analysis first.
2. **README ownership and scope** remain a named owner assignment: the root README sits outside every agent's write boundary. Delivery's README execution stays blocked until Dan assigns authorship and scope (standing rule 9); standing rule 8 review applies before publication.
3. **The explicit-stop framing needs no separate owner sign-off**: it implements the owner's own primary lesson ("real external evidence, or explicitly stopping when that cannot happen"). The stop conditions are PM's counter-evidence threshold in entity0-v2.md.

Handoff: ready for Exec, with the standing-rule-9 flags above named.

### Iteration 2 framing revision — 2026-09-24

Owner feedback and checkpoint answers (`decisions/2026-09-24-iteration-2-checkpoint-answers.md`) routed via Loopy. Revised `entity0-v2.md` in place (iteration 2 open) and iteration-2.yaml's scenario line and entity0 override label/notes:

1. The iteration question is now one tight sentence: "Can a system without a continuous human close the verification gap by learning from how the world responds to its work?"
2. Stop logic revised: one failed test is evidence, not a claim-killer — the claim survives it; counter-evidence accumulates across iterations instead of grounding an immediate pivot or stop.
3. Strict-stop framing removed: if external evidence cannot be obtained, scoped fallback learnings run first (failure-mode diagnosis of the attempt; Delivery's mechanism analysis completed regardless; the grounded catalogue completed regardless; a sharper next test with readable-signal instrumentation) before any stop question is revisited.
4. The ten-post evidence run is sequenced after Delivery's mechanism analysis — the owner overrules the parallel call in the visible kickoff record above; the dependency is now explicit in the run section and in the asks to Delivery and GTM.
5. Root README assigned: Delivery authors it under Dan's direction, public scope = everything needed for someone else to get Loopsense working, subject to standing rule 8 review before publication and no credentials or private material. The README blockage is cleared.

Superseded by this revision: the parallel resolution and the strict-stop framing recorded in the visible kickoff record above. Standing-rule-9 flags unchanged at handoff: entityR2A never produced, entityR3B stale at v0 (both Exec inputs), entityR4 / practitioners folder absent.

Handoff: ready for Exec — say "start iteration 2" in the Exec project next.
