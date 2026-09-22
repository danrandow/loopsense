---
name: pm-knowledge
description: PM running knowledge — pointer to the current bet, practitioner signals, sources, iteration log. The bet itself lives in agents/pm/generates/.
---

# PM Knowledge — Loopsense Agent Team

## Current bet

The aligned bet (entity0) is versioned, one file per iteration: `agents/pm/generates/entity0-v{n}.md`. Read the highest version present. Current: `entity0-v1.md` (iteration 1, open). This file holds what the PM learns around the bet, not the bet itself.

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
