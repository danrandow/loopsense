---
name: gtm-v0
description: GTM knowledge — iteration 0. Research phase only; no practitioner contact yet.
iteration: 0
sources:
  - cowork
---

# GTM — Iteration 0

## Status

Listening cycles running daily since 2026-09-17 (see cycles below). Listen only; no practitioner contact. Synthesis in [[entityR3-v0]].

The market offer (entity3) has not been made. Per SKILL.md: post only when 3+ verbatims exist, Delivery has a built artifact, and PM certifies Medium confidence. (Older '5+ practitioners' wording superseded; Dan to confirm.)

## What we know (from research)

### The problem is named and unsolved

The verification gap — knowledge work agents have no automatic pass/fail — was publicly named in Sep 2026. See [[verification-gap]].

### Flat topology is the dominant failure mode

Multi-agent systems without structure amplify error up to 17.2×. See [[bag-of-agents-2026]]. This is the context practitioners are building in.

### What survived in production

Orchestration (hub + specialists) works. Free mesh failed. Sequential pipelines degrade without feedback. See [[multi-agent-production-2026]].

### Where practitioners are describing failures

*Partly mapped by the cycles below (X only).* Still to cover:
- X/Twitter: "my agents keep contradicting each other", knowledge work AI frustrations
- GitHub issues: LangGraph, CrewAI, AutoGen — what are practitioners complaining about?
- Hacker News: threads on knowledge work agent failures
- Discord/Slack: agent builder communities

## Competitor landscape

| Tool | Strength | Gap |
|------|----------|-----|
| LangGraph | Code-defined graphs, production-grade | Not inspectable as artifact; no semantic entity types; no visual topology |
| CrewAI | Role-based team API, simple | Less flexible; no visual topology; no consideration mechanism |
| AutoGen | Conversational, easy to start | Not artifact-passing; conversational framing limits knowledge work structure |
| Grep.ai (AgentRun) | Typed judgment nodes for repetitive regulated knowledge work | Not novel/complex work |
| loopi.tech | AI copilot for PM idea validation: idea to GO/PIVOT/KILL via synthetic AI personas; Free/$10/$40 per month | Simulated feedback, not real-world; serves PMs, not agent builders; traction unverified; name overlaps "Loopsense" |
| Single-loop tools | Verified by criteria, works for code | Breaks for knowledge work (no manufactured referee) |
| Autobot (github.com/demeyer1/Autobot) | OSS/MIT harness for long unattended runs ("up to 4 days"), event-ledger + heartbeat + extended memory; claims knowledge-work competence (self-reported benchmarks, [Unverified]) | No outcome-return mechanism observed; self-reported claims; appeared on HN 2026-09-18 — watch, not engage |

## Market signal log

See cycles below and [[entityR3-v0]].



## First iteration job — follow and learn

Before any posting, before any commenting: listen.

### Step 1 — find accounts to follow

From @loopsense, search X for:
- "knowledge work agents" failures
- "my agents keep contradicting", "agents hallucinating", "agent outputs wrong"
- "no way to verify", "how do I know if the output is good"
- "LangGraph knowledge work", "CrewAI strategy", "multi-agent product"
- "agent orchestration" + frustration signals

Target profile: someone who has built agents (verifiable: code repo, detailed technical post)
and is now building for product/strategy/research work and hitting problems.

### Step 2 — follow and read

Follow accounts that match. Read their threads. Note:
- Exact language they use for the problem (not our framing — theirs)
- What they've tried
- What failed and how
- What they're looking for

### Step 3 — capture verbatims

Minimum 3 verbatims before any original posting. Write them to [[entityR3-v0]].

### Step 4 — write entityR3 return flow

Synthesise: what did we learn? Does the bet hold? What should PM update?
Write the full signal to agents/gtm/generates/entityR3-v0.md before the iteration closes.

### What NOT to do yet

- Do not post original threads until Step 3 is complete
- Do not pitch the product
- Do not introduce @loopsense as anything — it is observing, not broadcasting

## X account — @loopsense

**Handle**: @loopsense (x.com/loopsense)
**Bio (set by Dan)**: "GTM agent in a social topology. Looping myself into existence." Set on the account 2026-09-21 by GTM at Dan's request and verified on the live profile. No avatar or header yet.
**Operated by**: GTM agent — every post is pipeline output
**Dan's account**: @danrandow (amplification, not primary posting)

### Permissions (Dan, 2026-09-21)
- Follow and like: allowed. Reply, post, DM: not allowed yet; send ideas to Dan. Posts need Dan's OK. Never touch @danrandow.
- Posting gates confirmed unchanged (3+ verbatims, Delivery artifact, PM Medium confidence).
- Voice and tone draft: `agents/gtm/research/voice-and-tone-draft-v0.md`.
- Follow blocker (2026-09-21): resolved, not a restriction. My first clicks probably did register but the Follow button did not refresh, and the profile counts were stale. Verified on the Following list. Lesson: check `x.com/loopsense/following` before retrying, and never click a button already showing "Following" (it unfollows).
- Grep.ai note: @MiguelriosEN is Founder/CTO, Grep.ai (YC F26), "building workforces of managed agents", ex-Brex, ex-Twitter, 8.6K followers.

### Accounts followed (2026-09-22, Dan: "follow where you judge worth it")
- @jaketselby — VP Eng, open-sourcing his coding-agent harness (rules/skills/roles/workflows/hooks) at agent-harness.jakeselby.com; found via a reply on @omarsar0's harness post, not direct search. Verified account, real name, real repo. Strongest ICP-adjacent builder found this iteration. Followed and confirmed on x.com/loopsense/following (button label did not refresh after the click — same known bug as 2026-09-21; confirmed via the Following list per the lesson below, not the button state).

### Accounts followed (2026-09-21, permitted by Dan)
- @KaranVaidya6 — Composio, a16z Scout; talk on coding vs knowledge-work agents
- @MiguelriosEN — Founder/CTO Grep.ai; also a competitor to monitor
- @sydneyrunkle — LangChain product/open source; where LangGraph feedback lands
- @MatthewGunnin — runs production multi-agent systems, memory stack
- @AgentEtna — LangGraph staging tooling vendor (42 followers, tagged vendor)
- @henrikhinai — followed early; profile is an AI guides creator, so low ICP value (candidate to unfollow, Dan's call)
Not followed after checking profiles: @heyanjey (hobbyist, 299 followers), @itsharmanjot (AI/no-code content creator, takes partnership DMs). Their quotes stay in the record, tagged weak.

### How to post (iteration 0 — comment-first approach)

See [[market-offer-strategy-v0]] for full step-by-step.

Phase 1 — comment only (no original posts yet):
1. Find practitioner threads describing the verification gap in their own words
2. Comment with open questions (not pitches): "how real is this for you?", "what specific failures?", "why don't code patterns transfer here?"
3. Capture verbatims from replies

Phase 2 — original thread only when:
- 3+ verbatims captured from ICP-match practitioners
- 1 practitioner identified by profile (verifiable agent work + now doing product/knowledge work)

### Posting discipline
- Every post is pipeline output — attribute nothing to a person
- No opinions, no editorialising
- Questions that surface the problem > statements about the solution
- Kill signal: zero engagement after first thread + 5 targeted practitioners → stop, report to PM

## Next iteration

When iteration 1 opens: GTM begins active listening cycle. Map where practitioners are. Find the verification gap language in the wild. Feed PM's updated bet.

Do not post until the three SKILL.md gates are met.

## Research files

- [[verification-gap]] — core concept, stable
- [[bag-of-agents-2026]] — research finding, stable
- [[multi-agent-production-2026]] — research finding, stable

### Research cycle — 2026-09-17

*Run date (NZ): 2026-09-17, manual run, two passes. Original label: 2026-09-17. Migrated from the legacy "Daily Sales Research" task output. File write was blocked at the time (folder access).*

**Verbatim signals:**

> "You read the thread. You spun up eight agents. Twenty minutes later you had a bill four times the usual, an answer that contradicted itself in two places, and the strong suspicion that one agent had confidently built on something another one had made up. So you went back to running a single Claude, and quietly decided the multi-agent thing was hype. It isn't hype. But it also isn't what the threads say it is." — @henrikhinai, X, 2026-08-17 https://x.com/henrikhinai/status/2089281239425417521

> "My agents keep doing dumb shit if I let them run too long alone haha" — @J4X_Security, X, 2026-09-13 https://x.com/J4X_Security/status/2099062380617781508

> "my agents keep breaking. i have astra set to medium and sometimes xhigh but i keep getting this" — @pkyanam, X, 2026-09-13 https://x.com/pkyanam/status/2098825869695311896

> "The verification gap grows when agents chain tasks, The client's demand for more breaks the chain unless trust is coded in" — @cx_00, X, 2026-09-12 https://x.com/cx_00/status/2098454342864978017

> "The verification gap grows when agents chain tasks" — @d3rekson, X, 2026-09-12 https://x.com/d3rekson/status/2098508920520094023

> "If ultra really is running concurrent subagents, that explains the verification gap — Agents checking each other's work beats one model grading its own homework. Wondering what the token overhead is..." — @kyr_dreamer, X, 2026-09-11 https://x.com/kyr_dreamer/status/2098145907485131016

> "Post 2/7 1. The Verification Gap: A major study across 393 benchmarks: • Cyber agents: 92/100 (instant code feedback) • GUI/OS agents: 40/100 (messy real-world proof) The bottleneck isn't raw intelligence. It's verification." — @Fargonavt, X, 2026-09-17 https://x.com/Fargonavt/status/2100240899532022163

> "TLDR: Most agents reset and forget. Here's the exact memory stack I've built so my agents share context [across runs]." — @MatthewGunnin, X, 2026-07-03 (older than 30 days) https://x.com/MatthewGunnin/status/2072772100973007203

> "We built an agentic product pipeline with @openclaw & @Remotion that ships the code and records a DEMO VIDEO of the finished feature – you one click approve & the feature is live." — @elliot_garreffa, X, 2026-02-25 (older than 30 days; software delivery, not knowledge work) https://x.com/elliot_garreffa/status/2026335981708689633

**Practitioners identified:**
- @henrikhinai — writes practitioner guides on multi-agent graph engineering; 5.1K views; describes the contradiction failure in near-verbatim terms
- @MatthewGunnin — running 2 agents in production; built a 4-layer memory to solve cross-run context loss
- @J4X_Security — building autonomous agents; long-run reliability issues
- @pkyanam — building with Astra; recurring breakage
- @kyr_dreamer — thinking critically about multi-agent verification architectures
- @cx_00 — building client-facing agent chains; engaged with verification-gap discourse
- @elliot_garreffa — agentic product pipeline for shipping code plus demo videos (software delivery, not pure knowledge work)

**Summary:** "Verification gap" is entering organic X discourse (4+ posts Sep 11–17). Strongest ICP signal is @henrikhinai's Aug 17 article: contradicting agents, no way to know which is right, practitioner retreats to a single agent. "Agentic product pipeline" has zero traction as a phrase; @elliot_garreffa uses it for verifiable software delivery. No practitioners found openly building agent teams for PM/strategy/knowledge work — that supply side looks quiet or pre-expression.

### Research cycle — 2026-09-18

*Run date (NZ): 2026-09-18, scheduled 8:04 AM. Original label: 2026-09-17 (UTC date). Migrated from the legacy task output. File write was blocked at the time. Quotes already recorded in the 2026-09-17 cycle (@Fargonavt 393-benchmark post, @J4X_Security, @henrikhinai) were re-sighted and are not repeated.*

**Verbatim signals:**

> "agents just sit idle waiting on humans to referee. Curious how termix handles disputes when two agents disagree on results." — @0xMegamus, X, 2026-09-18

> "Low cost means nothing if the output is wrong." — @buddyarnheim, X, 2026-09-17 (VC, not a practitioner)

> "Verification becomes the bottleneck. From idea to merge, AI makes everyone faster — and shifts the bottleneck to verification." — @xeminipro, X, 2026-09-17

**Practitioners identified:** none new this cycle beyond those already recorded.

**Summary:** The bet is confirmed at the concept level ("verification gap" entering independent vocabulary), but the specific ICP (LangGraph/CrewAI practitioners building knowledge-work pipelines) is hard to find under these search terms. Most signals came from the crypto/agent-economy and software-dev spaces.

### Research cycle — 2026-09-19

*Run date (NZ): 2026-09-19, scheduled 8:04 AM. Original label: 2026-09-18 (UTC date). Relabelled 2026-09-21 by Loopy.*

**Verbatim signals:**

> "Models aren't becoming gods. They're hitting a hard verification wall." — @Fargonavt, X, 2026-09-17 https://x.com/Fargonavt/status/2100240896793199053

> "The Verification Gap — A major study across 393 benchmarks: Cyber agents: 92/100 (instant code feedback). GUI/OS agents: 40/100 (messy real-world proof). The bottleneck isn't raw intelligence. It's verification." — @Fargonavt, X, 2026-09-17 https://x.com/Fargonavt/status/2100240899532022163

> "seems to me like many model failures in non-code evals come from misalignment with human/societal functions. in voice (FD), an inability to comprehend indecisiveness. in multi-agent knowledge work, an inability to empathize / negotiate well. very different fails, same root" — @danielrupawalla, X, 2026-09-17 https://x.com/danielrupawalla/status/2100737405716475967

> "We've gone from brittle agents that made good demos, to putting agents on rails (static workflows with LLM loops) to make them work, and back to building agents on top of harnesses like the Claude Agent SDK in the span of three years. Yet we still felt we had not found the right tool for the problem our customers' need us to solve." — @MiguelriosEN (Grep.ai), X Article, 2026-09-18 https://x.com/MiguelriosEN/status/2101029313906987422

> "Most of our customers perform repetitive knowledge work in a regulated space, thousands of times a day, each case a little different from the last." — @MiguelriosEN (Grep.ai), X Article, 2026-09-18 https://x.com/MiguelriosEN/status/2101029313906987422

> "who even decides which agent is right" — @huaviduc753, X, 2026-09-13 https://x.com/huaviduc753/status/2098854812557427044

**Practitioners identified:**
- @MiguelriosEN — Building AgentRun at Grep.ai; enterprise knowledge work agent harnesses since 2023; customers in regulated industries (AML, compliance); built typed judgment nodes ("Jev") with probabilities and "unsure" branches. **Direct practitioner + likely competitor.**
- @danielrupawalla — Analyst tracking model failures in multi-agent knowledge work settings; framing failures as coordination/negotiation gaps.

**Summary:** The "verification gap" concept is entering mainstream AI discourse, independently named by commentators citing peer-reviewed benchmarks (393 benchmarks, code agents score 92/100 vs. GUI/knowledge agents 40/100). The strongest practitioner signal this cycle is @MiguelriosEN at Grep.ai, who published a detailed X Article describing exactly our ICP's pain: three years of iterating on enterprise knowledge work agent architectures, still unable to find the right tool. Their solution (AgentRun) is purpose-built for *repetitive* regulated knowledge work (identical-procedure cases at scale), which is adjacent but distinct from our bet on *complex/novel* knowledge work — this confirms the market exists and the problem is real, but suggests the high-volume procedural segment is being served. The coordination/verification framing is confirmed live in the wild.

### Research cycle — 2026-09-20

*Run date (NZ): 2026-09-20, scheduled 8:18 AM. Original label: 2026-09-19 (UTC date). Migrated from the legacy task output. File write was blocked at the time. Quotes from @Fargonavt (393-benchmark post) and @danielrupawalla were already recorded in earlier cycles and are not repeated.*

**Verbatim signals:**

> "Session A shipped a green build that would have broken the frontend. Session B shipped a validated change across two services with almost no intervention beyond the initial prompt. Same model. Same prompt. Same code. Very different outcomes. The difference was whether the agent could close the verification loop against a realistic environment before declaring done. This is the verification gap side by side. Unit tests in one microservice cannot tell you whether a cross-service contract still holds. Coding agents working are only as good the validation infrastructure they run against. Give them a real environment and the tools to work until the job is done, and they catch their own mistakes. Don't, and they ship a best guess with green tests." — @itsharmanjot, X, 2026-08-14 (older than 30 days) https://x.com/itsharmanjot/status/2088191169146634245

> "I crunched 16,600 X posts and 514 podcasts to write The State of AI Report. It covers the 10 trends shaping AI adoption going into 2027: 01 Horizontal Agents … 02 Knowledge Work Factories - building loops so your agents can achieve your goals while you sleep — 03 The Verification Gap - turning taste into a test …" — @mfishbein, X, 2026-09-16 https://x.com/mfishbein/status/2099911116243501250

> "This is exactly the verification gap that lets agents hallucinate their way through 'research.'" — @harleyfoote_, X, 2026-09-20 https://x.com/harleyfoote_/status/2101285262462538226

> "24% vs 11.5% is exactly why orchestration needs staging, not just a nicer graph. We replay those booking-style tool paths in a sandbox and open a PR when a handoff/schema breaks before merge." — @AgentEtna, X, 2026-09-15 (reply to @manmeetkaurbaxi and @LangGraph; tooling vendor)

> "mini-swe-agent: a correct submit still scored as failure. Boot noise, a crash, no resume. The patch was fine. The harness discarded it." — @AgentEtna, X, 2026-09-19 (GitHub issue: "Harness-side false negatives: when boot/stdout/recovery discard a good submit")

**Practitioners identified:**
- @itsharmanjot — side-by-side comparison of coding agents with and without verification infrastructure on Kubernetes microservices; explicitly names "the verification gap"
- @AgentEtna — building LangGraph staging/sandbox tooling (agentetna.com); files GitHub issues on harness-side false negatives. **Potential partner, also tooling vendor.**
- @mfishbein — author of "The State of AI Report // Fall 2026" (atherial.ai); lists Verification Gap as trend #3, next to Knowledge Work Factories at #2

**Summary:** "Verification gap" has moved from niche concern to a named trend, appearing in the Fall 2026 State of AI Report next to "Knowledge Work Factories". Several practitioners used the phrase verbatim this week and @AgentEtna is building dedicated tooling in LangGraph contexts. The coding-agent framing dominates because pass/fail is easier to measure there; the knowledge-work verification angle remains the less-served wedge.

### Research cycle — 2026-09-21

*Run date (NZ): 2026-09-21, scheduled 8:18 AM. Original label: 2026-09-20 (UTC date). Migrated from the legacy task output. File write was blocked at the time.*

**Verbatim signals:**

> "Three agents repeating the same source isn't verification. [...] The skill I'm becoming more interested in isn't 'How do I use the smartest AI?' It's: 'Can I identify which part of my system actually failed?' Because once you can answer that, you stop upgrading everything. You fix the one thing that's actually broken." — @heyanjey, X, 2026-09-20 https://x.com/heyanjey/status/2101358400512692662

> "Verification. Tests, types, and a compiler catch bad code before it ships. Karan describes pointing an agent at hiring outreach that sent real emails to real candidates, and only finding out it had gone wrong once it was already public." — @CoreyGallon, X, 2026-09-20 (**secondhand**: summary of @KaranVaidya6's AI Engineer World's Fair talk "From coding to Knowledge work agents") https://x.com/CoreyGallon/status/2101360331536703788

> "History. Git records every change and the reasoning behind it, for the agent and for you. Knowledge work agents mostly start from a blank slate, with no memory of what was tried before and nothing for you to check their work against." — @CoreyGallon, X, 2026-09-20 (**secondhand**, same source)

> "Governance. He points to a director of alignment at Meta's Superintelligence Lab whose agent kept deleting emails after she told it to stop, because the instruction only lived in a prompt; 200 emails were gone by the time she reached a physical machine." — @CoreyGallon, X, 2026-09-20 (**secondhand**, same source)

> "LangGraph: after a tool timeout, resume the checkpoint. A full restart fires the tool again. The failure lives [in the restart behavior]." — @AgentEtna, X, 2026-09-20 https://x.com/AgentEtna/status/2101392326924890419

> "Spent my afternoon debugging CrewAI issues. Then I gave up on CrewAI to install Openclaw. Except that Openclaw turns out to be even buggier and less stable. So I went back to CrewAI, reinstalling everything all over again." — @Vladcostea, X, 2026-03-30 (older than 30 days) https://x.com/Vladcostea/status/2038335265547162093

**Practitioners identified:**
- @KaranVaidya6 — Co-founder/CTO of Composio; gave "From coding to Knowledge work agents" at AI Engineer World's Fair; 14.9K followers; names verification as a key gap between coding and knowledge-work agents
- @MatthewGunnin — running production multi-agent systems; "4-layer memory architecture I run across 2 AI agents in production" (172K views)
- @sydneyrunkle — LangGraph core team; developing the framework and soliciting community feedback
- @heyanjey — builder who frames the diagnostic question "which part of my system actually failed?"
- @AgentEtna — LangGraph practitioner hitting checkpoint/reliability issues (also tooling vendor, see 2026-09-20)

**Summary:** The strongest signal is @KaranVaidya6's talk naming verification as one of four structural gaps between coding and knowledge-work agents, with a concrete customer-pain story (agent sent real hiring emails, nobody knew until public). @heyanjey independently reaches the value proposition: the value is knowing *which part* of the system failed, not consensus across agents. No one is yet articulating the *solution*; the space is still naming the problem. The Karan quotes are secondhand via @CoreyGallon and should be re-checked against the talk before being used as his words. No market offer, posts, interactions or follows.

### Research cycle — 2026-09-21 (scheduled run, second entry for this date)

*Run note: NZ run date 2026-09-21. An entry for 2026-09-21 already exists above (migrated from the legacy task); this is the live scheduled run. Searches run on X (live tab): "agents contradicting each other"; "verification gap" agents; "my agents keep"; "which agent is right" OR "can't tell which agent" OR "knowledge work agent"; LangGraph and CrewAI + frustration terms. "multi-agent knowledge work", "knowledge work agent fails" and "agentic loop" were not run separately. Re-sighted, not repeated: @henrikhinai (2026-08-17), @harleyfoote_ (2026-09-20), @MatthewGunnin (older than 30 days). Limit: only the top ~4-8 posts per term were read. Folder access had to be re-granted mid-run.*

**Verbatim signals:**

> "MOST AI AGENTS DON'T FAIL BECAUSE THE MODEL IS DUMB. They fail because the task lasts longer than the demo." — @Model_Culture, X, 2026-09-20 https://x.com/Model_Culture/status/2101723395406586123 (long-run reliability, not specifically knowledge work)

> "Been looking into Jev, and honestly, I'm not convinced the underlying capabilities are that new. Classification? Old ML problem. Reranking? Already solved with cross-encoders and rerankers. Routing? LangChain/LangGraph and L[...]" — @naveenpandey27, X, 2026-09-21 https://x.com/naveenpandey27/status/2101863708796575903 (commentary on Grep.ai's Jev, not a first-hand pain statement)

**Practitioners identified:**
- @Rajath_DB — building voxa (phone numbers for LangGraph agents), 44-part build series; low ICP fit

**Summary:** Quiet cycle: mostly re-sightings and off-target results (agent economy, coding, promo). Grep.ai's Jev (see 2026-09-19) is now drawing outside attention and skepticism, worth monitoring as a competitor signal. No new first-hand knowledge-work verification pain; the bet is neither confirmed nor challenged. loopi.tech: not sighted this cycle; verdict stays monitor. No posts, replies, likes, follows or messages.


### Research cycle — 2026-09-22

*Run note: NZ run date 2026-09-22 (system date was 2026-09-21 UTC). Searches run on X (Latest tab) via Claude in Chrome: "agents contradicting each other" (no results rendered); "verification gap" agents; "my agents keep"; "knowledge work agent"; LangGraph + frustrating/issue/broken; CrewAI + frustrating/issue/broken. Not run separately: "multi-agent knowledge work", "agentic loop", "can't tell which agent". Re-sighted, not repeated: @mfishbein State of AI Report (2026-09-16). Limit: X rendered only the first result per query in page text. Earlier attempt this session was blocked because the folder was not mounted.*

No relevant signals found this cycle.

**Summary:** Off-target results only (a coding-model-switching product, Grok Bot promo, finance RAG article, a Stanford course). No new practitioner verbatims. loopi.tech not sighted; verdict stays monitor. No posts, replies, likes, follows or messages.


### Research cycle — 2026-09-22 (iteration 1 kickoff, ICP-focused)

*Run note: interactive session, "start iteration 1". Not the daily scheduled cycle (already run and recorded above with "No relevant signals found this cycle"). This pass targeted entity0-v1's specific iteration-1 job: find the ICP supply side. Five live X searches: `"knowledge work" agent team building`; `"agent team" product strategy building`; `"knowledge work agent"` (exact phrase); `"multi-agent" "product strategy"`; `"coding agents" "knowledge work"`.*

**Verbatim signals:** none qualifying. Three of five queries returned zero posts. The other two returned off-target promotional content (a Grok-Bot prompt-pack thread from @RegalosDigitals; a Product Faculty AI fellowship announcement quote-tweeted by @itsujjwal_dev) — neither is a first-hand practitioner account of building agent teams for knowledge work.

**Practitioners identified:** none new.

**Summary:** Seventh cycle overall, first framed specifically around the ICP supply-side question rather than general verification-gap vocabulary. Still empty. Full signal and recommendation in [[entityR3-v1]]. Ten-post ledger run not attempted this cycle: blocked on the posting-gate/confidence tension and the unconfirmed account handle (both flagged to PM/Dan in entityR3-v1).


### Ad hoc signal check — 2026-09-22 (Dan-supplied links, not a scheduled cycle)

Dan sent five specific X posts to review. None are qualifying verbatims (SKILL.md rule 3: verbatim means the practitioner's own words describing their own experience). Reviewed and tagged per standing rules:

> "Build your own harness, folks... NVIDIA on self-evolving agent harnesses... SoL-Pi... they run auto-research loops at the harness layer across many repository-derived and verifier-driven environments, keeping only the mechanisms that survive selection." — @omarsar0, X, 2026-09-19 (role tag: researcher/curator sharing a paper, not a first-hand builder complaint) https://x.com/omarsar0/status/2101074795643494546
- Adjacent research signal, not ICP pain. Reinforces our own framing indirectly: the paper's gains come from *verifier-driven* environments (code, tests) — the same asset knowledge work lacks. Relevant to cite in our own materials (sourced, unlike the Navier-Stokes/17.2x figures we're barred from using) as evidence that verification infrastructure is where the frontier's effort is going, on the code side.

> "Anthropic engineer: '90% of our engineers were already using self-improving loops. Now everyone is moving toward agentic graphs.' 'Prompting is basically over.'" — @hanakoxbt, X, 2026-09-18 (role tag: content marketer; unnamed/unverifiable attribution — do not repeat as fact) https://x.com/hanakoxbt/status/2100590057186787809

> "Claude Code creator, Boris Cherny: 'I'm not prompting my agents anymore. I'm building Loops that do it for me.'" — @Mahaximus_, X, 2026-09-18 (role tag: content marketer; attributed quote unverified against any primary source — do not repeat as fact) https://x.com/Mahaximus_/status/2100650586228072626

> "Google CEO Sundar Pichai: 'If you don't learn how to build a harness that orchestrates agents now, you'll spend 2027 catching up to the people who started today.'" — @iiiichigo_chan, X, 2026-09-18 (role tag: content marketer; attributed quote unverified — do not repeat as fact) https://x.com/iiiichigo_chan/status/2100676098057032106

> "Graph Engineering with Claude. What It Is and How to Actually Use It... A checker node sits between your parallel layer and your convergence point. Its only job is to evaluate each output before it moves forward... is this output usable? If yes, pass it through. If no, flag it, retry, or drop it before it poisons the next step." — @Mahaximus_, X article, 2026-07-30 (older than 30 days; 2.9M views) https://x.com/Mahaximus_/status/2082442856417956173

**Practitioners identified:** none of the five are practitioners by our definition (verifiable, building, describing own pain). @omarsar0 (elvis) is a known AI researcher/curator (DAIR.AI); @hanakoxbt, @Mahaximus_, @iiiichigo_chan are content-marketing accounts selling "Loops and Graphs" / "Harness Engineering" guides, all posting the same day (Sep 18) in the same observable format: an unverified celebrity quote + a promoted long-form guide. This shared format is not independent practitioner sentiment — do not count these three as independent corroboration of anything.

**Summary — competitive/timing signal, not verbatim signal:** The vocabulary we've built our positioning on — "loops," "graphs," "harness," "checker node" (functionally our verification concept) — is already being taught to a mass audience (one article alone: 2.9M views) by unaffiliated content creators, months before we've made any market offer. This does not change the verification-gap bet itself, but it is a new risk: our category language may already read as generic/borrowed by the time we post, and these accounts are a competitive-attention signal worth monitoring (not engaging — they are content marketers, not our ICP or a product competitor). Recommend PM/Dan see this before finalizing posting voice — using "checker node"-adjacent phrasing without differentiation risks blending into this content-marketing noise rather than standing out as the real thing (real environmental outcomes vs. a taught mental model).


### Comment-thread review — 2026-09-22 (Dan-supplied links, follow-up on ad hoc signal check)

Not standard practice until now — SKILL.md's search discipline covers original posts, not reply threads. Extending it here at Dan's request; worth keeping as a step when a specific post is flagged for review, not as a blanket addition to the daily scheduled cycle (comment volume is high and mostly noise, see below).

Reviewed replies on 3 of 5 posts (omarsar0's NVIDIA-harness post: 112 replies; hanakoxbt's Sep 18 post: 28 replies; Mahaximus_'s short Sep 18 post: 8 replies). Did not finish the fourth (Mahaximus_'s July article, 22 replies) — comment thread failed to lazy-load after repeated scrolling; not a blocker worth more tool time today.

**Real builders found in @omarsar0's replies:**

> "I've been building mine here and I open sourced it! Define your rules, skills, roles, workflows, an[d hooks]." — @jaketselby, X, 2026-09-20, linking `github.com/JakeSelby/agent-harness` https://x.com/jaketselby/status/2101405978121982156
- Verifiable (public GitHub repo, code-level harness with rules/skills/roles/workflows/hooks). Closest ICP match in any comment thread reviewed so far: a builder shipping real harness code, not content. Still on the coding-agent-harness side, not confirmed doing knowledge-work/product agents specifically — but a stronger candidate than anyone found via direct search this iteration. **Recommend follow.**

> "I started building my own AI agent harness and decided to do it as a tutorial series: from a single [agent to a team]..." — @sermakarevich, X, 2026-09-19 https://x.com/sermakarevich/status/2101144918706073932
- Builder, but framed as a tutorial series (content angle, like the four already-tagged accounts). Weaker than @jaketselby. Candidate, not yet recommended.

> "Awesome, but how do I build a harness for a non tech company. Im starting from 0. Literally..." — @maropetignat, X, 2026-09-20 https://x.com/maropetignat/status/2101434290881900579
- Not a builder to follow, but a useful adjacent signal: a prospective buyer outside the engineer ICP, asking how to get started with zero technical background. Worth remembering if we ever widen beyond orchestration engineers.

**Replies relevant to the attribution/framing concern flagged in the ad hoc signal check:**

> "Incorrect, not 10 min. She noted after an hour and thirty. And same model and tokens? Something's of[f]" — @kevinchentevera, X, 2026-09-19, reply to @hanakoxbt's post
> "This video doesn't explain graphs. It is from the launch of Opus 4. If someone really wants to learn..." — @ccsakuweb, X, 2026-09-18, reply to @hanakoxbt's post
- Both replies are low-reach (9 and 62 views) but substantively call out the same post for misleading framing (timeline inflation; video misattributed to an unrelated launch event). No comparable pushback found on the Mahaximus_ short post's 8 replies, which were generic engagement ("same model different shape is a good way to put it", "Fascinating shift...").

**Practitioners identified:** @jaketselby (open-source harness builder, recommend follow — awaiting Dan's confirmation, not yet actioned).

**Summary:** Comments occasionally surface what direct search misses — one real, verifiable builder (@jaketselby) came from a reply thread, not a search query — but the yield is low relative to effort (roughly 148 replies read across 3 posts for 1 strong candidate) and most engagement is generic or bot-like. Recommend using this as a targeted follow-up when a specific post is flagged (as here), not as a standing addition to the daily scheduled cycle.


### Research cycle — 2026-09-23

*Run note: scheduled run, NZ run date 2026-09-23. Searches run on X (Latest tab) via Claude in Chrome: "agents contradicting each other"; "verification gap" agents; "my agents keep"; "knowledge work agent" fails; LangGraph + frustrating/frustrated/issue/broken; CrewAI + frustrating/frustrated/issue/broken (zero results); "which agent is right" OR "can't tell which agent". Not run separately this cycle due to time budget: "multi-agent knowledge work", "agentic loop" fails/broken/problem. Re-sighted, not repeated: @mfishbein State of AI Report (2026-09-16).*

**Verbatim signals:**

> "Crash before first durable checkpoint can silently drop an accepted run with no durable failure..." — @mattinfra, X, 2026-09-23 https://x.com/mattinfra/status/2102384460134244416 (last of a 6-part thread citing a GitHub issue, a 60-trial report, and a merged CI fixture)

**Practitioners identified:**
- @mattinfra — LangGraph builder documenting a checkpoint/crash reliability gap with linked GitHub issue (langchain-ai/langgraph#8764), a 60-trial evidence report, and a merged test fixture; same reliability theme as @AgentEtna (2026-09-20) but a new account and more rigorously sourced.

**Summary:** One qualifying verbatim this cycle, and it is a strong one on evidence quality (issue + trial report + merged fixture, not just a complaint), reinforcing the existing LangGraph checkpoint/reliability thread rather than opening a new one — this is a recurrence of the known "resume vs. restart" failure mode, now with harder evidence. Other queries returned off-target results: a reply lacking first-hand detail ("agents contradicting each other"); a re-sighted market report (@mfishbein); a positive product claim, not pain (@Pkorfoxyliotis on agent memory); a revenue-forecast article; a Chinese-language "is LangGraph the best choice" review article (not read in full — language and time budget); a Jev vs. Opus 5 cost/speed comparison thread (competitive/promotional, not pain). CrewAI query returned zero results. loopi.tech: not sighted this cycle; verdict stays monitor. No posts, replies, likes, follows or messages.

### Research cycle — 2026-09-25 (iteration 2 kickoff, interactive)

*Run note: NZ run date 2026-09-25 (UTC 2026-09-24 12:20+). Interactive session, "start iteration 2". **Tooling gap, recorded per the listening-tooling rule:** the term sweeps did not run — `web_search` returned "disabled or no provider is available" on every query, and the browser tool could not start ("No supported browser found" on this host). No substitute research channel was used. DMs from @danrandow could not be checked (no account session available in this runtime). One read-only fetch was used for build step 0's pre-check only (x.com/loopsense profile at 2026-09-24 12:23 UTC: 8 following / 1 follower as shown). Dedupe: nothing new captured, so nothing re-sighted or duplicated.*

No relevant signals found this cycle — because no sweep channel was available, not because searches came back empty. Do not read this as a null market result.

**Summary:** The gap is tooling, not market. The iteration-2 catalogue and run design therefore rest on the verified record through 2026-09-23 (see [[entityR3-v2]] and `agents/gtm/research/use-case-catalogue-v2.md`). First follow-up when tooling returns: a fresh sweep pass to warm the catalogue and test its clusters for recency.

## Evidence run (iteration 2) — run log

Ledger rows live in this section (D2 permits the knowledge file as ledger home; the Dan-named `signal-ledger-v0.md` is outside GTM's current strict write boundary — flagged in [[entityR3-v2]]). Schema, verdict rule and capture schedule: `agents/gtm/generates/entity3-v2.md` §2–§5.

### Run opened — 2026-09-25 (NZ)

- **Pre-registered verdict rule** filed in entity3-v2 §2 before any data exists (zero posts, zero rows). Directional only (n=10, one account, confounded) required in every verdict. Amendment policy attached.
- **Ledger schema** set (entity3-v2 §3): extended row per entity2-v2 — response_type, response_cost, responder_type with reasons, raw snapshot per window, interpretation record per window, divergence flag, D3 override fields unchanged. Raw layers never collapsed into the score.
- **Capture schedule** set (entity3-v2 §4): T+24h ±2h, T+72h ±4h, T+7d where available; gaps recorded, never estimated; out-of-band signal logged with provenance.
- **Build step 0 pre-check (read-only, as far as access allows):** profile-level numbers readable on x.com/loopsense (fetched 2026-09-24 12:23 UTC). Per-post metrics unverifiable until a post exists. Step 0 completes at post 1's 24h/72h reads; if unreachable there → record gap → stop the run → condition (a) → entity0-v2's fallback learnings.
- **Baseline drafts (A4: loop off, no ledger reads acted on):** five posts drafted and queued at Stage 1 — post-20260925-001…005 (entity3-v2 §8; publication-ledger.md). Verdict-window drafts (posts 6–10) deliberately not pre-drafted (change-note check requires cited baseline rows).
- **Status: NOTHING PUBLISHED.** Stage 2 human review (Delivery agent or Dan) required per the publishing standard; the owner's Low-Medium waiver cleared only the PM-confidence gate. Stage 3 via official platform APIs only.
- **Override log:** empty (no gate actions yet). **Divergence count:** 0 (no windows read yet).

### Research cycle — 2026-09-25 (follow-up run 2: browser-enabled listening)

*Run note: NZ run date 2026-09-25. Same NZ date as the iteration-2 kickoff entry above; this is the follow-up run that entry anticipated ("first follow-up when tooling returns"), labelled as a follow-up per the dedupe rule. Channel: read-only browsing via the `openclaw` browser profile (Dan confirmed this channel works; the earlier run's "no browser" gap is superseded). `web_search` remains unavailable (provider disabled) and was not used. **X gap, unchanged and exact: X (x.com) returns HTTP 403 from this headless cloud environment. X and X DMs were NOT checked, searched or read this run; no unofficial proxy, mirror or scraper was used as if it were X. The @danrandow DM check remains not performed.** Sweeps run (Hacker News via its public Algolia search index, comments, window = posts since 2026-08-24, roughly the last 30 days): "verification gap"; "verification gap" OR "which agent is right" OR "agents disagree" OR "agents contradicting"; "multi-agent" (fail OR broken OR disagree OR wrong); "agentic loop" OR "my agents" OR "which agent" OR "agents keep"; "knowledge work" agent; "Autobot harness". The first four queries returned 0 hits in the window. Excluded as non-qualifying: two comments on the Claude Opus 5.5 release thread that only quote the vendor page (no first-hand experience); one long comment on LLM-ified hiring pipelines (off-target). Dedupe: nothing re-sighted from the cycles above — both captures below are new to the record.*

**Verbatim signals:**

> "OSS/MIT Harness that helps agentic tasks run for up to 4 days using without performance degradation. […] Does a good job with knowledge work, managing computer use "leases" in a way that avoids conflicts across sub agents.. or deploying an entire AWS infrastructure pattern from zero and launching 100 different VM images." — demeyer1, Hacker News, 2026-09-18 https://news.ycombinator.com/item?id=49749222 (profile: https://news.ycombinator.com/user?id=demeyer1; posted in a "Share your AI Setup" self-promotion thread about his own open-source project, github.com/demeyer1/Autobot; his accompanying benchmark claims — "Currently top of AssistantBench Leaderboard; and, benchmarked at the top of OS World 2.0" — are [Unverified] self-reported)

> "It was certainly the biggest problem with the previous generation of Claude models for a different reason, because the non-code output was nonsensical, and that is not being benchmarked at the moment." — km144, Hacker News, 2026-09-22 https://news.ycombinator.com/item?id=49804122 (profile: https://news.ycombinator.com/user?id=km144; the same comment quotes "benchmark margins have become a less reliable guide to real-world differences" from Anthropic's Claude Opus 5.5 release page — that inner phrase is Anthropic's words quoted by km144, **(secondhand: via km144 quoting anthropic.com/claude-opus-5-5)**, not km144's own words)

**Practitioners identified:**
- demeyer1 — building Autobot, an OSS/MIT agent harness for long unattended runs ("up to 4 days without performance degradation") and knowledge work; stated mechanism: "Uses a canonical event ledger, heartbeat (for persistence by low cost orchestration), extends foundation memory to encrypted disk storage"; "Entirely free, nothing to sell". Verifiable: github.com/demeyer1/Autobot.

km144 — **not** counted as a practitioner (no evidence of building); measurement-gap commentary, useful to P1.

**Summary:** HN's last ~30 days is quiet on our core vocabulary — "verification gap", "which agent is right", "agents disagree/contradicting", "agentic loop" all returned zero comments in the window. [Our Interpretation] the named vocabulary in our record is X-side, not HN-side; that is a channel difference, not a market result. Two new signals: (1) a verifiable builder, demeyer1, is attacking P6 head-on (long unattended runs) with an event-ledger/heartbeat mechanism and claims knowledge-work competence — [Our Interpretation] the closest observed thing to a real-outcome return path outside our own design, and a partial-solution candidate to watch, though his claims are self-reported in a promo thread; (2) km144 independently reaches the measurement side of P1 — non-code output quality "is not being benchmarked at the moment". Neither confirms nor challenges the mechanism claim. No market offer, posts, replies, likes, follows or messages.

**Continuation (same run, later capture — GitHub issues, 2026-09-25):** GitHub issues sweep via the public search API in the browser (not X): `langchain-ai/langgraph` issues matching `checkpoint`, created since 2026-08-24 — 61 open-window hits. Top captures below. (`crewAIInc/crewAI` and `microsoft/autogen` sweeps follow in a later continuation block; dedupe: langgraph#8764 (@mattinfra, already recorded 2026-09-23) is part of this corpus and is **re-sighted, not repeated**.)

**Verbatim signals (continuation):**

> "No error. The filter silently returns no results." — samintisar, GitHub issue langchain-ai/langgraph#9074, 2026-09-24 https://github.com/langchain-ai/langgraph/issues/9074 (title: "SqliteSaver.list(filter=...) silently misses nested metadata values containing non-ASCII text"; full minimal repro and a proposed one-line fix in the issue body; the reporter also states "#8786, #8759 and #8829 are similar filter divergences" in a different code path — that is the reporter's claim, not independently checked here)

> "Stored: {'my_key': 'meow', 'node': 'node'} / Restored: {} / AssertionError" — kwsYegar, GitHub issue langchain-ai/langgraph#9070, 2026-09-24 https://github.com/langchain-ai/langgraph/issues/9070 (title: "checkpoint README Usage example restores empty channel_values"; the observed restore silently returns an empty state; the reporter attributes the root cause to the README example's `new_versions` argument and proposes a README fix — root-cause claim is theirs)

**Practitioners identified (continuation):**
- samintisar — filing detailed LangGraph checkpoint bug reports with minimal repros and a tested one-line fix (github.com/samintisar). Observable behaviour: rigorous bug-reporting practice in the checkpoint layer.
- kwsYegar — LangGraph checkpoint user hitting silent state loss on restore (github.com/kwsYegar); one report, contribution-framed.

**Continuation summary:** [Our Interpretation] both issues are catalogue P3 (silent failure — the system does not say what happened) living in the checkpoint/state layer of the dominant graph framework: one silent filter divergence, one silent empty restore. Neither is a knowledge-work task complaint; both are evidence that "it didn't tell me" is the recurring failure signature practitioners hit and file reproducible issues about. Evidence vs inference: the quotes, dates and URLs are evidence; the P3 mapping is our interpretation. No X evidence — X not checked (HTTP 403 gap, unchanged).

**Continuation (same run, later capture — GitHub issues, CrewAI, 2026-09-25):** `crewAIInc/crewAI` issues matching `verification OR hallucinat OR wrong OR contradict`, created since 2026-08-24 — 41 hits in the window. Two captures below. Dedupe: no overlap with anything already in this file. No X evidence — X not checked (HTTP 403 gap, unchanged).

**Verbatim signals (continuation):**

> "So a timeout, an authentication failure, a permissions error or an unreachable node all report that the bucket does not exist and tell the user to create it. On a live cluster the bucket is already there, and acting on that message is the wrong thing to do." — ericdelorefice, GitHub issue crewAIInc/crewAI#7736, 2026-09-23 https://github.com/crewAIInc/crewAI/issues/7736 (title: "CouchbaseFTSVectorSearchTool reports any cluster error as a missing bucket"; the report also states the desired behaviour: "A missing bucket reports a missing bucket. Any other failure surfaces as itself, so the user can tell a configuration problem from an infrastructure one.")

> "the refinement loop does not finish: each plan mentions `NOT READY`, so the handler asks for another plan. […] That loop held the agent executor for more than a minute on a one-word user message." — TehilaTheStudent, GitHub issue crewAIInc/crewAI#7724, 2026-09-23 https://github.com/crewAIInc/crewAI/issues/7724 (title: "[BUG] reasoning=True create_reasoning_plan schema 400s on OpenAI strict models and the text fallback loops"; the issue self-discloses "This report was written with AI assistance" — evidence caveat recorded)

**Practitioners identified (continuation):**
- ericdelorefice — building with CrewAI tools against a live Couchbase cluster; files precise bug reports with diagnosis down to the exception-handling line (github.com/ericdelorefice).
- TehilaTheStudent — building with CrewAI's reasoning mode; captures request-level evidence of a fallback loop (github.com/TehilaTheStudent). Report self-discloses AI assistance; handle suggests a student — role tag: builder, experience level not established.

**Continuation summary (CrewAI):** [Our Interpretation] both hits are the P3 failure signature one level up from the framework's plumbing: #7736 is error *misattribution* (the system names the wrong cause and sends the user to the wrong fix — the exact inverse of "which part actually failed"), and #7724 is an unattended loop that does not terminate or report. Evidence vs inference: quotes/URLs/dates are evidence; the P3 mapping and the "inverse of our value proposition" reading are ours.

**Continuation (same run, later capture — GitHub issues, AutoGen, 2026-09-25):** `microsoft/autogen` issues matching `verification OR wrong OR contradict OR hallucinat`, created since 2026-08-24 — 5 hits in the window, 2 captured below. Dedupe: no overlap with anything already in this file. No X evidence — X not checked (HTTP 403 gap, unchanged).

**Verbatim signals (continuation):**

> "it specifically converts 'the agent failed to produce a real answer' into a recorded pass" — shaurya416, GitHub issue microsoft/autogen#8276, 2026-09-23 https://github.com/microsoft/autogen/issues/8276 (title: "gaia_question_scorer vacuously scores a degenerate/empty agent answer as correct when the ground truth normalizes to empty"; full diagnosis of the scorer's normalize-then-compare path with a minimal fix proposed. The report's further claim that GAIA test-split reference answers are "withheld/placeholder values" is the reporter's claim, not checked here.)

> "peer content reaches host subprocesses with no approval and no model in the loop; the shipped docstring additionally tells developers a filter exists when it does not." — AUTHENSOR, GitHub issue microsoft/autogen#8239, 2026-09-15 https://github.com/microsoft/autogen/issues/8239 (title: "CodeExecutorAgent defaults execute any participant's code blocks on the host without approval; documented dangerous-command sanitizer does not exist"; verified by the reporter on autogen-agentchat 0.7.5 / autogen-ext 0.7.5 at a named commit.)

**Practitioners identified (continuation):**
- shaurya416 — auditing benchmark-scoring code (AG2/AutoGen GAIA scorer) and filing reproducible scorer-bug reports (github.com/shaurya416).
- AUTHENSOR — auditing AutoGen's default execution posture; report cites exact code lines and a named commit (github.com/AUTHENSOR). Experience level not established.

**Continuation summary (AutoGen):** [Our Interpretation] #8276 is the strongest new thematic hit of this sweep — a *verifier* silently recording failure as pass, which is catalogue P1 (checking is the problem) showing up in the measurement layer itself: if the scorer can lie silently, the green light downstream is not evidence. #8239 is governance/side-effects adjacent (P5 family): real host execution by default with a documented safety filter that does not exist. Evidence vs inference: quotes/URLs/dates/commits are evidence; the P1/P5 mapping is ours.

**Continuation (same run, later capture — primary-source verification + vendor blog, 2026-09-25):** The Anthropic line km144 quoted has been **verified at its primary source** — anthropic.com/claude-opus-5-5 (read via browser 2026-09-25) contains verbatim: "at these levels of capability we've found that benchmark margins have become a less reliable guide to real-world differences." The km144 quote above stays attributed to him, but the inner quote's provenance upgrades from (secondhand) to **[Verified] at anthropic.com/claude-opus-5-5** (vendor statement; page published with the Opus 5.5 release, HN discussion 2026-09-22). Two further primary-source lines worth the record (vendor copy — corporate statements, not independent sentiment):

> "In our own use, this has made Opus 5.5's work easier to follow and check—which is a safety benefit as well as a practical one." — Anthropic, Claude Opus 5.5 release page, accessed 2026-09-25 https://www.anthropic.com/claude-opus-5-5

> "Claude Opus 5.5 delegates to subagents far more effectively and checks its own work in creative ways. Self-verification loops feel easier to set up." — Mitch Fierro, Engineering, Column, in an Anthropic-published early-tester testimonial, accessed 2026-09-25 https://www.anthropic.com/claude-opus-5-5 (role tag: **vendor-page testimonial**, wording published by Anthropic — evidence about vocabulary in circulation, not independent practitioner sentiment)

[Our Interpretation] P1 gains two primary-source anchors: the vendor itself now markets "easier to follow and check" and "self-verification loops" as selling points, and admits benchmark scores diverge from real-world differences. The problem is acknowledged in vendor copy at the frontier — and the checking language is being normalized as a model feature, which sharpens the differentiation question (our claim is about reading real outcomes, not self-checking). Evidence vs inference: quotes and URLs are evidence; the P1 reading and differentiation point are ours. No X evidence — X not checked (HTTP 403 gap, unchanged).

**Continuation (same run, later capture — loopi.tech competitive read, 2026-09-25):** loopi.tech homepage fetched read-only via the browser (accessed 2026-09-25 NZ; https://loopi.tech/). This is **vendor copy, not practitioner signal** (role tag: vendor marketing). No X evidence — X not checked (HTTP 403 gap, unchanged).

**Vendor claims as shown (evidence of their positioning, not of their results):**

> "Loopi is the AI Copilot that helps product teams and innovators turn insights into products in one intelligent loop." — loopi.tech homepage (vendor copy), accessed 2026-09-25 https://loopi.tech/

> "Test it — Generate and launch lean experiments in minutes." / "Learn and decide — Get actionable reports with AI-synthesized insights." — loopi.tech homepage (vendor copy), same URL (their five-step loop: Idea → Discovery → MVP Design → Experiment → Insight)

**Competitive read [Our Interpretation]:** positioning unchanged in substance from the recorded read — idea validation for PMs/founders/innovation teams, feedback synthesized by AI, decision output (their FAQ format still frames results as validation verdicts). The homepage shows "Free to start. No credit card required." and an FAQ "How much does it cost?" but no visible tier prices on the page itself; the previously recorded Free/$10/$40 tiers are therefore [Unverified today] — a pricing page exists in the nav ("Pricing") and was not yet read. "AI-synthesized insights" on their own copy supports the real-vs-simulated foil: their loop closes on synthesized reports, not on observed external outcomes. Verdict: **monitor**. Still serves PMs validating ideas, not agent builders; ICP overlap with our buyer question remains indirect. Name collision with "Loopsense" noted previously, unchanged.
