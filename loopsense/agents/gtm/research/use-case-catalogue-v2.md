---
name: use-case-catalogue-v2
description: Grounded use-case catalogue, iteration 2 — representative problems not well solved by current agent-harness, loop-engineering or graph-engineering approaches, with the groups who have them. Built only from real, sourced problems (recorded practitioner verbatims and filtered Dan-supplied leads).
iteration: 2
author: gtm
last_updated: 2026-09-25
sources:
  - cowork
status: research (Pub boundary); grounding rule of entity0-v2 applied
---

# Use-case catalogue v2 — real problems, real groups

## Grounding rule (entity0-v2) and how it was applied

entity0-v2: *"If real problems cannot be sourced, say so and stop this initiative — a fabricated
catalogue is failure, not partial success."*

**Result: real problems WERE sourced, so the initiative proceeds.** Everything below rests on
practitioner verbatims already captured with URLs in `agents/gtm/knowledge/gtm-v0.md` (listening
cycles 2026-09-17 → 2026-09-23) plus Dan-supplied leads filtered on 2026-09-22. Nothing here is
invented, generalised from theory, or reconstructed from memory of a summary. Where evidence is
secondhand, older than 30 days, vendor-linked, duplicated or URL-less, it is tagged as such and
weighed accordingly.

**Exclusions applied (with reasons):**
- The 17.2× error-amplification figure, the Navier-Stokes swarm framing, "manufactured referee",
  "solves": barred (unsourced; entity0-v2 / entity1-v2 constraints). Not used anywhere.
- entity1-v2's 11%/64% production statistics: uncited at source. Not used.
- "Every great AI capability win has binary verification": unverified per Exec (entity2-v0
  handover). Not used as a claim.
- @hanakoxbt / @Mahaximus_ / @iiiichigo_chan celebrity-attribution quotes: unverified
  attributions (2026-09-22 review). Not used as evidence of anything except vocabulary
  commoditisation (which is about the posts' own existence, not their quoted claims).
- Secondhand @KaranVaidya6 talk lines: never as his words. Used only as (secondhand) evidence
  of a problem being discussed publicly (P5).

**Session limitation (2026-09-25 NZ) — updated after the follow-up sweep:** at iteration-2
kickoff the sweep channel was unavailable (`web_search` disabled; no browser) and the catalogue
was built from the recorded cycles only. The browser (read-only `openclaw` profile) became
available later the same NZ date and a follow-up sweep ran; its evidence is appended below
("Evidence added"). `web_search` remains disabled and was not used. **X gap: X (x.com) returns
HTTP 403 from this headless cloud environment — X and X DMs were NOT checked, searched or read
(no unofficial proxy, mirror or scraper used as if it were X); the @danrandow DM check remains
not performed.** The catalogue's X-sourced captures remain the verified record through
2026-09-23; the appended evidence is HN/GitHub/open-web only and does not narrow the X gap.

## The problems

Each entry: the problem in the practitioners' own words first; then why current agent-harness,
loop-engineering and graph-engineering approaches do not well solve it; then the groups who have
it. Confidence is GTM's judgment of the evidence base, not a claim about prevalence.

---

### P1. Judgment/knowledge work has no pass/fail — the checking problem

**In their words:**

> "This is exactly the verification gap that lets agents hallucinate their way through 'research.'"
> — @harleyfoote_, X, 2026-09-20 https://x.com/harleyfoote_/status/2101285262462538226

> "Session A shipped a green build that would have broken the frontend. Session B shipped a
> validated change across two services with almost no intervention beyond the initial prompt. Same
> model. Same prompt. Same code. Very different outcomes. The difference was whether the agent
> could close the verification loop against a realistic environment before declaring done. […]
> Don't, and they ship a best guess with green tests."
> — @itsharmanjot, X, 2026-08-14 (older than 30 days) https://x.com/itsharmanjot/status/2088191169146634245

> "Verification becomes the bottleneck. From idea to merge, AI makes everyone faster — and shifts
> the bottleneck to verification."
> — @xeminipro, X, 2026-09-17 (URL not seen)

> "The bottleneck isn't raw intelligence. It's verification."
> — @Fargonavt, X, 2026-09-17 https://x.com/Fargonavt/status/2100240899532022163
> (this poster's framing of an unnamed "393 benchmarks" study; the study is not linked in the
> post — treat any figures attached to it as [Unverified] circulation)

**Why current approaches don't solve it** [Our Interpretation, from the record]: coding-agent
harnesses work where a verifier exists (tests/CI — @itsharmanjot's side-by-side). Loop-engineering's
answer for judgment work is a model-judged gate ("checker node… evaluate each output before it
moves forward" — @Mahaximus_, X article, 2026-07-30, older than 30 days,
https://x.com/Mahaximus_/status/2082442856417956173), which substitutes simulated judgement for an
outcome. Three years of enterprise harness iteration did not close it either: "Yet we still felt we
had not found the right tool for the problem our customers' need us to solve" — @MiguelriosEN,
X Article, 2026-09-18 https://x.com/MiguelriosEN/status/2101029313906987422 (vendor; first-hand
build experience). Their answer (typed judgment nodes) targets *repetitive* regulated work —
"thousands of times a day, each case a little different from the last" (same article) — not novel
or complex work.

**Groups who have it (listen to):**
- G1: coding-agent harness builders crossing into judgment work (see Groups below)
- G3: multi-agent knowledge-work builders and teachers
- Provisional buyer frame from entity1-v2: anyone whose AI-assisted strategy/discovery/research/
  content output currently needs a human check before it counts

**Confidence: high that the problem is real and named; unknown prevalence.** 6+ independent
sources over 5 weeks, two of them first-hand build accounts.

---

### P2. Contradicting agents; nothing decides which agent is right

**In their words:**

> "who even decides which agent is right"
> — @huaviduc753, X, 2026-09-13 https://x.com/huaviduc753/status/2098854812557427044

> "You read the thread. You spun up eight agents. Twenty minutes later you had a bill four times
> the usual, an answer that contradicted itself in two places, and the strong suspicion that one
> agent had confidently built on something another one had made up. So you went back to running a
> single Claude, and quietly decided the multi-agent thing was hype. It isn't hype. But it also
> isn't what the threads say it is."
> — @henrikhinai, X, 2026-08-17 (older than 30 days) https://x.com/henrikhinai/status/2089281239425417521
> (role tag: guide writer; but the described experience is specific and first-hand in form)

> "agents just sit idle waiting on humans to referee. Curious how termix handles disputes when two
> agents disagree on results."
> — @0xMegamus, X, 2026-09-18 (URL not seen)

> "seems to me like many model failures in non-code evals come from misalignment with
> human/societal functions. in voice (FD), an inability to comprehend indecisiveness. in
> multi-agent knowledge work, an inability to empathize / negotiate well. very different fails,
> same root"
> — @danielrupawalla, X, 2026-09-17 https://x.com/danielrupawalla/status/2100737405716475967
> (role tag: analyst)

**Why current approaches don't solve it** [Our Interpretation]: graph-engineering adds structure
(hub, layers, convergence) but the arbitration of conflicting outputs is still a human or a model
gate (P1's problem one level up); harness patterns (rules/skills/roles/workflows/hooks — see G1)
govern behaviour, not truth between disagreeing outputs. The observed practitioner response is
retreat to a single agent (@henrikhinai) — cost paid in capability, not solved.

**Groups:** G3 primarily; G5 secondarily (disagreement surfaces in long unattended runs).

**Confidence: medium-high.** Four independent posters, one a detailed first-hand narrative.

---

### P3. Silent failure — you can't tell which part of the system failed

**In their words:**

> "Three agents repeating the same source isn't verification. […] The skill I'm becoming more
> interested in isn't 'How do I use the smartest AI?' It's: 'Can I identify which part of my system
> actually failed?' Because once you can answer that, you stop upgrading everything. You fix the
> one thing that's actually broken."
> — @heyanjey, X, 2026-09-20 https://x.com/heyanjey/status/2101358400512692662

> "Crash before first durable checkpoint can silently drop an accepted run with no durable
> failure…"
> — @mattinfra, X, 2026-09-23 https://x.com/mattinfra/status/2102384460134244416
> (6-part thread citing langchain-ai/langgraph#8764, a 60-trial evidence report and a merged CI
> fixture — strongest evidence quality in the record)

> "LangGraph: after a tool timeout, resume the checkpoint. A full restart fires the tool again. The
> failure lives [in the restart behavior]."
> — @AgentEtna, X, 2026-09-20 https://x.com/AgentEtna/status/2101392326924890419
> (role tag: tooling vendor; also a first-hand LangGraph practitioner)

> "mini-swe-agent: a correct submit still scored as failure. Boot noise, a crash, no resume. The
> patch was fine. The harness discarded it."
> — @AgentEtna, X, 2026-09-19 (URL not seen; cites a GitHub issue "Harness-side false negatives")

**Why current approaches don't solve it** [Our Interpretation]: these are failures *of* the
harness/loop layer itself — restart semantics, checkpoint durability, submit handling — so the
tooling that routes and loops work is the object of the complaint, not the remedy. Nothing in the
record shows a graph- or loop-engineering approach attributing failure to a component for
judgment work.

**Groups:** G2 (graph-framework practitioners) and G1 (harness builders); the diagnostic question
"is which part failed" is also the closest recorded precursor to our value proposition
(@heyanjey) — listen hard here.

**Confidence: high** (issue links, trial reports, merged fixtures — not just complaints).

---

### P4. Chained agents for client work: trust breaks the chain

**In their words:**

> "The verification gap grows when agents chain tasks, The client's demand for more breaks the
> chain unless trust is coded in"
> — @cx_00, X, 2026-09-12 https://x.com/cx_00/status/2098454342864978017

> "The verification gap grows when agents chain tasks"
> — @d3rekson, X, 2026-09-12 https://x.com/d3rekson/status/2098508920520094023

**Evidence-quality caution:** two accounts posted near-identical lines on the same day. This may
be copied phrasing or coordinated posting. Treat as **weak** — one distinct observation, not two.

**Why current approaches don't solve it** [Our Interpretation]: "trust coded in" is exactly what
rule/loop scaffolds attempt, but the record shows no example of it holding under client demand
pressure; no counter-evidence either. Thin.

**Groups:** G4-adjacent — agencies/consultancies running agent chains for clients.

**Confidence: low** (duplicate-phrasing caution; single distinct observation).

---

### P5. Agents with real-world side effects fail after the fact

**In their words (secondhand — do not attribute to the speaker of the talk):**

> "Verification. Tests, types, and a compiler catch bad code before it ships. Karan describes
> pointing an agent at hiring outreach that sent real emails to real candidates, and only finding
> out it had gone wrong once it was already public."
> — @CoreyGallon, X, 2026-09-20 (**secondhand**: summary of @KaranVaidya6's AI Engineer World's
> Fair talk "From coding to Knowledge work agents") https://x.com/CoreyGallon/status/2101360331536703788

> "Governance. He points to a director of alignment at Meta's Superintelligence Lab whose agent
> kept deleting emails after she told it to stop, because the instruction only lived in a prompt;
> 200 emails were gone by the time she reached a physical machine."
> — @CoreyGallon, X, 2026-09-20 (**secondhand**, same source, same URL)

**Evidence-quality caution:** secondhand summaries of a talk; the talk itself has not been checked.
Use as evidence that this problem is being discussed publicly, not as verified case detail.

**Why current approaches don't solve it** [Our Interpretation]: the failure is that nothing reads
the real outcome (the emails went out; the deletions happened) until a human notices — precisely
the missing return path. Harness guardrails in the record are behavioural (prompts, rules), and
the second anecdote is literally about a prompt-level instruction failing.

**Groups:** G4 — teams pointing agents at real external comms, hiring, ops. Currently evidenced
only via this talk; listening target is people repeating or extending these stories.

**Confidence: low-medium** (one secondhand source; the underlying talk unverified).

---

### P6. Long unattended runs drift and degrade

**In their words:**

> "My agents keep doing dumb shit if I let them run too long alone haha"
> — @J4X_Security, X, 2026-09-13 https://x.com/J4X_Security/status/2099062380617781508

> "my agents keep breaking. i have astra set to medium and sometimes xhigh but i keep getting this"
> — @pkyanam, X, 2026-09-13 https://x.com/pkyanam/status/2098825869695311896

> "MOST AI AGENTS DON'T FAIL BECAUSE THE MODEL IS DUMB. They fail because the task lasts longer
> than the demo."
> — @Model_Culture, X, 2026-09-20 https://x.com/Model_Culture/status/2101723395406586123
> (role tag: commentary account; long-run reliability, not knowledge-work-specific)

**Why current approaches don't solve it** [Our Interpretation]: raising model effort settings did
not fix it (@pkyanam tried). Loop/graph scaffolds in the record extend run length without adding
a read of actual outcomes mid-run — the drift accumulates unobserved.

**Groups:** G5 — builders operating long-running/autonomous agents.

**Confidence: medium** (three posters; two thin on detail, one commentary).

---

### P7. Cross-run memory: agents reset and forget

**In their words:**

> "TLDR: Most agents reset and forget. Here's the exact memory stack I've built so my agents share
> context [across runs]."
> — @MatthewGunnin, X, 2026-07-03 (older than 30 days) https://x.com/MatthewGunnin/status/2072772100973007203

**Why current approaches don't solve it:** **partially served** — memory products and stacks
exist (this poster built his own; a positive product claim was sighted 2026-09-23). Include in
the catalogue as a real problem, marked as the cluster where current tooling is most competitive.

**Groups:** G5 (overlap with P6).

**Confidence: medium; competition: high.**

---

### P8. Starting from zero: non-technical teams can't get in

**In their words:**

> "Awesome, but how do I build a harness for a non tech company. Im starting from 0. Literally..."
> — @maropetignat, X, 2026-09-20 https://x.com/maropetignat/status/2101434290881900579

**Why current approaches don't solve it** [Our Interpretation]: harness/loop/graph engineering is
addressed to engineers by construction (the record's builders all ship code). This group is a
buyer-side gap, not a technical one.

**Groups:** G6 — non-technical knowledge workers and small businesses.

**Confidence: low** (one observation; flagged in the 2026-09-22 comment review as worth
remembering if we widen beyond orchestration engineers).

---

## The groups to listen to (potential ICPs)

| Group | Who they are | Evidence anchors | Reachability | Priority |
|---|---|---|---|---|
| G1 | Coding-agent harness builders crossing into judgment work | @jaketselby ("Define your rules, skills, roles, workflows, an[d hooks]", open-source repo, https://x.com/jaketselby/status/2101405978121982156); @sermakarevich (tutorial series — weak/content-adjacent) | Identified handles; @jaketselby already followed | **Listen first** |
| G2 | Graph-framework practitioners hitting reliability limits | @mattinfra (with issue+trials), @AgentEtna (vendor tag), @sydneyrunkle (framework side — listen, not ICP) | Identified handles | High |
| G3 | Multi-agent knowledge-work builders/teachers | @henrikhinai, @KaranVaidya6 (vendor-side CTO but first-hand build voice), @danielrupawalla (analyst) | Identified handles | High |
| G4 | Teams running agents against real external side effects (hiring/comms/ops) | Secondhand only (P5) | No direct handles yet | Listen via P5 story spread |
| G5 | Long-run autonomy operators | @J4X_Security, @pkyanam, @Model_Culture (commentator) | Identified handles | Medium |
| G6 | Non-technical knowledge workers/SMBs starting from zero | @maropetignat | Identified handle | Later (widening) |
| G7 | Regulated repetitive-work agent shops | Grep.ai customers via @MiguelriosEN's article | Vendor-mediated | Monitor; listen for complex-case spillover |

**Watch-only, not ICP:** content marketers teaching "loops/graphs/harness/checker node"
(@hanakoxbt, @Mahaximus_, @iiiichigo_chan) — competitive-attention and vocabulary-commoditisation
signal only; analysts/press (@mfishbein, @Fargonavt) — amplification channel, not buyers.

## Cross-cutting notes

- **[Our Interpretation] The strongest unifying thread across P1–P3 and P5–P6 is absence of a
  return path for real outcomes**, not absence of structure. Current harness/loop/graph approaches
  in the record add structure, gates or memory; the complaints survive all three. This is
  consistent with the bet (environment as verifier) and is the sentence the catalogue adds to it.
- **Vocabulary commoditisation is confirmed as a positioning constraint:** the problem space's
  words are mass-taught (2.9M-view article). Differentiate on tested/untested status and
  demonstrated mechanism, not naming.
- **What the catalogue does NOT establish:** prevalence, willingness to pay, or that any group
  above is the buyer. Seven prior cycles found zero ICP matches because they hunted for a
  pre-shaped ICP; this catalogue inverts the search — these groups are the ones to sit with next.

---

## Evidence added — 2026-09-25 (browser follow-up sweep, same NZ date)

Extension, not a rebuild. Captured via the browser: HN (public Algolia index), GitHub issues
(public search API), vendor pages. All quotes carry URLs and source dates; capture date is
2026-09-25 (NZ) throughout. **X (x.com) returns HTTP 403 from this headless cloud environment —
X and X DMs were NOT checked, searched or read; the @danrandow DM check remains not performed;
nothing below is X evidence.**

### P1 additions (checking is the problem — now including the measurement layer)

> "it specifically converts 'the agent failed to produce a real answer' into a recorded pass" —
> shaurya416, GitHub issue microsoft/autogen#8276, 2026-09-23
> https://github.com/microsoft/autogen/issues/8276

[Our Interpretation] a benchmark scorer silently recording failure as pass: the verifier itself
fails silently, so a green number downstream is not evidence. P1 in the measurement layer.

> "at these levels of capability we've found that benchmark margins have become a less reliable
> guide to real-world differences" — Anthropic, Claude Opus 5.5 release page (vendor copy),
> accessed 2026-09-25 https://www.anthropic.com/claude-opus-5-5 (**[Verified] at source** — this
> is the line km144 quoted on HN 2026-09-22; his quote in gtm-v0.md upgrades accordingly)

> "In our own use, this has made Opus 5.5's work easier to follow and check—which is a safety
> benefit as well as a practical one." — same page, same date (vendor copy)

> "Self-verification loops feel easier to set up." — Mitch Fierro, Engineering, Column, in an
> Anthropic-published early-tester testimonial, accessed 2026-09-25, same URL (role tag:
> **vendor-page testimonial** — evidence of vocabulary in circulation, not independent sentiment)

[Our Interpretation] the frontier vendor now markets checking/self-verification as a model
feature. Differentiation pressure: our claim is about reading real outcomes, not self-checking.

### P3 additions (silent / misattributed failure — GitHub corpora, all created since 2026-08-24)

> "No error. The filter silently returns no results." — samintisar, langchain-ai/langgraph#9074,
> 2026-09-24 https://github.com/langchain-ai/langgraph/issues/9074 (minimal repro + tested
> one-line fix proposed; reporter also names #8786/#8759/#8829 as similar divergences — their
> claim, not independently checked here)

> "Stored: {'my_key': 'meow', 'node': 'node'} / Restored: {}" — kwsYegar,
> langchain-ai/langgraph#9070, 2026-09-24 https://github.com/langchain-ai/langgraph/issues/9070
> (silent empty restore; root-cause claim is the reporter's)

> "a timeout, an authentication failure, a permissions error or an unreachable node all report
> that the bucket does not exist" — ericdelorefice, crewAIInc/crewAI#7736, 2026-09-23
> https://github.com/crewAIInc/crewAI/issues/7736

> "That loop held the agent executor for more than a minute on a one-word user message." —
> TehilaTheStudent, crewAIInc/crewAI#7724, 2026-09-23
> https://github.com/crewAIInc/crewAI/issues/7724 (issue self-discloses AI-assisted writing)

[Our Interpretation] same P3 signature as the X record — the system does not say what happened,
or names the wrong cause (crewAI#7736 is error misattribution: the inverse of "which part
failed"). Corpus scale in window: langgraph `checkpoint` 61 hits; CrewAI 41; AutoGen 5. The
record no longer rests on X alone (langgraph#8764 re-sighted in this corpus — recorded
2026-09-23, not repeated).

### P5-family addition (real side effects / governance)

> "peer content reaches host subprocesses with no approval and no model in the loop; the shipped
> docstring additionally tells developers a filter exists when it does not." — AUTHENSOR,
> microsoft/autogen#8239, 2026-09-15 https://github.com/microsoft/autogen/issues/8239 (reporter-
> verified at a named commit on autogen-agentchat 0.7.5 / autogen-ext 0.7.5)

### P6/P7 watch item (partial-solution candidate)

> "OSS/MIT Harness that helps agentic tasks run for up to 4 days using without performance
> degradation. […] Does a good job with knowledge work" — demeyer1, Hacker News, 2026-09-18
> https://news.ycombinator.com/item?id=49749222 (self-promotion thread; project:
> github.com/demeyer1/Autobot; mechanism "a canonical event ledger, heartbeat […], extends
> foundation memory"; benchmark claims self-reported [Unverified])

[Our Interpretation] the closest observed mechanism to a real-outcome return path outside our
own design — but no outcome-return mechanism is confirmed in it. Watch, not engage; tracks P6/P7.

### Recency test (the follow-up's second purpose)

HN core vocabulary ("verification gap", "which agent is right", "agents disagree/contradicting",
"agentic loop", "my agents", "agents keep") returned **0 hits** in the last-30-day window.
[Our Interpretation] the named vocabulary is X-side; channel difference, not a market result —
and with X unreachable it cannot currently be re-tested where it lives.
