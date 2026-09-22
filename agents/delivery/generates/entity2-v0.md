---
name: entity2-v0
description: The product, iteration 0. Part 1 is the practitioner "start here" page (D1). Part 2 is the content-loop spec and signal ledger (D2). Part 3 is the design rationale. Part 4 is the draft verdict rule (D3). Part 5 is the FAQ. Part 6 is handover notes for GTM. Iteration 0, untested.
entity: entity2
direction: forward
from: actor2 (Delivery)
to: actor3 (GTM)
iteration: 0
status: ready-for-gtm (iteration 0 draft, untested)
based_on: agents/exec/generates/entity1-v0.md
last_updated: 2026-09-21
sources:
  - cowork
---

# Part 1. Start here (D1)

**In one sentence:** Randow Maps is a map of your agent team that carries what the world did with the work back to the agent that made it, so you are no longer the referee.

## The problem

If you run several agents on knowledge work (research, strategy, discovery, content), you may recognise these:

- "Who even decides which agent is right?"
- "Agents just sit idle waiting on humans to referee."
- "Can I identify which part of my system actually failed?"
- "You went back to running a single Claude."

Coding agents get a free referee: the tests pass or they don't. Knowledge work has no tests, so you become the referee. That is the verification gap.

## The idea

You cannot write the test before the work exists. But once the work is out in the world, the world responds: replies, follows, clicks, forks, deals. Randow Maps routes that response back to the agent that produced the work, through a named return flow, so that agent can change what it does next. You then check whether it improved.

We claim this **partly** closes the gap. We have not shown that it works. Iteration 0 is the first test.

LangGraph, CrewAI and AutoGen route *work* between agents. A Randow Map also routes *outcomes* back to whoever made the work, and it is a YAML file you can read, fork and diff between runs. Tools such as loopi.tech validate with simulated personas; we use what actually happened.

## The moving parts

- **Actors** are the agents, each with one role. **Actions** are the one thing each actor does.
- **Entities** are what they pass along. Forward entities carry work downstream; **return** entities carry signal back upstream.
- **Edges** say who generates what and who reads what.
- **SKILL.md** is one file per agent: its role, what to read first, what to produce. A **knowledge file** is what that agent has learned so far.
- **Consideration:** before acting, an agent reads the knowledge file of whoever will receive its output, so it writes for that reader. We think this improves output. It is untested.

## A worked example: the @loopsense content loop

This is what iteration 0 runs.

1. GTM, our agent for the market, drafts a post for the practitioner it wants to reach.
2. The account owner (Dan) approves or rejects it for safety and brand. He does not grade quality, and we record why he acted.
3. The post goes out and X users respond.
4. GTM reads the platform's real numbers and replies and fills one row in the signal ledger.
5. GTM writes what it will change in the next draft, citing ledger rows.
6. After ten posts, we check whether posts 6 to 10 did better than posts 1 to 5.

Full spec and ledger: Part 2. The rule for deciding "did it improve": Part 4.

## Run one iteration yourself

You need an AI tool that can read and write files, and somewhere your work can meet the world.

1. Copy `base.yaml`, the `agents/*/SKILL.md` files, and `knowledge/standing-rules.md`, `team-registry.md` and `reading-the-map.md`. Rename the actors and edit the map to fit your team.
2. For each actor in order, open a session and give it the map, its SKILL.md, its knowledge file and the upstream entity. Ask it to do its role and write the result to `agents/<id>/generates/<entity>-v0.md`.
3. Order: PM writes the bet (entity0), Exec certifies it (entity1), Delivery builds (entity2), GTM makes the offer (entity3). The world responds (entity4).
4. Each actor then writes its return flow for the actor upstream who will use it, and updates its knowledge file. Each actor appends a line to the log before it writes anything.
5. In this map, an iteration is done when GTM has returned its market signal to the PM. Yours can differ.

It worked if every return flow has a filed entry and you can point to one thing an agent changed because of one of them.

## Tested vs not tested

| Tested | Not tested |
|---|---|
| Our own team ran on this map for iteration 0; the files read and edit fine by hand | That outcome signals change what an agent does |
| | That any change is an improvement |
| | That consideration improves output |
| | That anyone outside this team can run it |
| | That a small account gives usable signal |

## Why it is built this way

A judge agent would recreate the problem it is meant to solve, so the world's response does the judging. A map stored as a file can be forked, diffed and versioned, so it stays inspectable between runs. And we build our own team with the method, so what we learn is real signal. Part 3 lists every design choice with its reason.

Common questions, such as "do I need code?" and "is a human involved?": Part 5.

---

# Part 2. Content-loop spec and signal ledger (D2)

## Map vocabulary used (no new map elements needed)

| Step | Map element |
|---|---|
| Drafting | actor3 GTM, action3 |
| Post as published | entity3 Market Offer |
| The world's response | entity4 Practitioner Response |
| Raw response back to the drafter | **entityR4B** Demand & Objections (GTM's direct signal) |
| Drafter's running notes | entityPrv3 (GTM knowledge file) |
| What Delivery supplies | entity2 (this file) and any GTM field requests via entityR3A |

The return edge is a file convention: after each read, GTM appends to `agents/gtm/knowledge/gtm-v0.md` (or a ledger file GTM owns) and the next draft cites it. If Dan or Loopy want a dedicated signal entity in the map, that is a change for `base.yaml`, which I cannot edit.

## One pass of the loop

1. **Draft.** GTM writes the draft plus a **change note**: what differs from the previous post, and which ledger rows justify it (blank for post 1).
2. **Gate.** Dan approves, edits, or rejects. Delivery's template records: action taken, and reason category (**safety/brand** or **quality**).
3. **Publish.** Only after Dan's OK. Never from @danrandow.
4. **Read.** GTM reads platform numbers at 24 hours and 72 hours, and at 7 days where available. It records replies with handles.
5. **Score.** Fill the ledger row (below).
6. **Return.** GTM writes the next change note before drafting.

## Signal ledger: one row per post

| Field | Content |
|---|---|
| post_id | X post id |
| date | posting date and time (NZ) |
| angle | what this post tests, in one line |
| one_change | the single thing changed from the previous post (keep to one) |
| dan_action | approved / edited / rejected |
| override_reason | safety-brand / quality / none |
| impressions_24h, _72h, _7d | raw numbers |
| likes, reposts, replies | raw numbers |
| icp_fit | list of handles, plus what they did (reply / follow / fork / DM) |
| score | weighted score, using the weights below |
| next_change | what the drafter will change next, and why |
| cites_rows | the ledger rows the next_change relies on |

**Weights (preliminary, not locked):** ICP-fit response 10, any other reply 4, repost or quote 2, like 1. Impressions are recorded for context and not scored.

**ICP-fit** means the person shows agent work plus knowledge-work now (a public repo or post). GTM decides and records why. Vendors and VCs do not count.

## What each reader needs

- **GTM** gets: a ledger to fill in, and the start-here page as source material for the drafts.
- **Dan** gets: a single place to record his gate decisions and reasons.
- **Exec and PM** get: rows they can check without asking anyone.

## Stop rules

- If a ledger field cannot be filled because the platform data is not reachable, GTM records the gap in the row and reports it. Missing data is not filled with estimates.
- If there is no ICP-fit response across ten posts, the weighted score falls back to replies. That fallback is flagged in the verdict, not hidden.

## What is not decided here

The verdict rule is in Part 4. This spec supplies the rows it is judged on. Whether GTM or another actor owns the ledger file long term is Dan's call.

---

# Part 3. Design rationale

Sources: `history/`, `loopsense.log.json`, `knowledge/standing-rules.md`, `knowledge/dna.md`, `base.yaml`, `entity0-v0`, `entity1-v0`. Standing rule 7 (2026-09-21) is the first to require a WHY on harness changes. Where a reason was not written down at the time, it is marked *(inferred)*.

| Choice | Why | Recorded in |
|---|---|---|
| The team is itself a Randow Map, run on its own product | We are our own first customer. Running the method on our own problem gives real signal, and dna.md calls it the only honest way to build this. | `base.yaml` notes; `dna.md` |
| A pull system with return flows and bypass loops, not a linear chain | Bypass flows (R2A, R3A, R3B, R4B, R4C) carry feedback packaged for the actor who will use it. The map treats them as tensions the PM integrates, not as noise. | `base.yaml` notes; `reading-the-map.md` |
| Return flows are load-bearing | The world's response only helps if it reaches the right actor at the right moment. Without the return edge the signal exists but is not usable. | `entity0-v0` |
| Consideration: read your receiver's knowledge file before acting | It approximates stepping into the receiver's world, so each actor writes for the person who will use the output. It is a practice, not a schema element. Whether it improves output is untested. | `dna.md`; `reading-the-map.md`; `entity0-v0` |
| The bet moved from a "manufactured referee" to the environment as verifier | A rubric or judge needs more judgment than the task, so it fails the cost test. For complex work the world's response is the only honest grader. The topology-vs-loop-vs-pair comparison was never run and was dropped; the scenario was retitled. | `entity0-v0`; `history/108`, `history/109` |
| No code runner, no judge agent, real platform data only | A judge agent would void the test. Keeping to YAML and Markdown means practitioners bring their own agents. The cost of being wrong stays at Dan's time. | `entity1-v0` section 4 |
| YAML and Markdown | A topology stored as a file can be forked, versioned, diffed and composed by reference. A code-defined adaptive graph cannot be held still and inspected between iterations. | `dna.md`; `exec-v0` |
| A fixed, directed topology, not a free mesh or an adaptive graph | A free mesh lets errors compound. An adaptive graph has no fitness function without a verification signal. | `exec-v0`; `entity0-v0` |
| Dan holds a publish gate but does not grade quality | The gate covers safety, brand and accounts. Whether the two can be kept apart is measured through the override log. | `entity1-v0` |
| One SKILL.md and one knowledge file per agent; protocol lives there and in the standing rules | Project instructions are short stubs, so Dan does not re-paste instructions by hand when rules change. | `history` log 58; standing rule 3 |
| Each flow is a file at `agents/{id}/generates/{entityId}-v{n}.md`, frozen when the iteration closes; Prv in `knowledge/`, Pub in `research/` | *(inferred)* One addressable file per flow means readers know where to look and which version they have; frozen files keep iterations comparable. | log 67 and 68; standing rule 4 |
| In `iteration-*.yaml`: label = headline, notes = summary, full content in the file | The renderer clips long labels, so detail lives in the file. | standing rule 5; `reading-the-map.md` |
| Agents may edit only `iteration-*.yaml` entries for their own entities, never `base.yaml`, `moonshot.yaml` or `near-term-experiment.yaml` | *(inferred)* The canonical topology stays stable while each agent keeps its own scenario entries current. | standing rule 5; log 100 to 105 |
| Every YAML change is logged first with a BEFORE/AFTER record; every harness change carries a WHY | The log and record are the audit trail and the undo. WHY lets the design be documented later. | standing rules 6 and 7 |
| The log is append-only, changed only by adding entries | *(inferred)* No agent can silently rewrite history, and a broken log stops work. | standing rule 6 |
| An iteration completes when GTM returns market signal (entityR3) | Practitioners have not been reached. Their signal is to be measured independently later, and the definition will change then. | `base.yaml` `iteration_definition`; log 95 |
| The retro sits outside the topology | It is the outermost loop: how Dan and Loopy learn what it is like inside the harness. No mid-iteration hand-holding. | `history/111` |
| A moonshot scenario gives direction instead of guardrails | For complex work you cannot list the forbidden things in advance. A full picture of the desired end state lets agents check for drift. | `dna.md`; `moonshot.yaml` |

**If you fork this:** in my judgment the first nine rows are the substance and the rest is housekeeping for a team run by one owner. A fork can drop the housekeeping and keep the loop. That is my reading, not a recorded decision.

**Not yet recorded:** the reasons for the early folder and naming choices (the move from `skills/` and flat `knowledge/` to `agents/`, the Loopsense name) are in the log as actions without reasons. They are a good question for the iteration-0 retro.

---

# Part 4. Verdict rule (D3), preliminary

Written on Delivery's own assumptions. The PM's answers to Exec's questions will not arrive this iteration, so I have stated what I assumed. This is a directional go/no-go, not proof. It is preliminary and not locked: iteration 0 is the team learning to work together, so treat it as guidance and change it freely. Dan gates every post, and the ledger and the rule can be simplified as we learn.

## Assumptions (in place of PM answers)

- **A1, what "verified without a human" means (R1 Q3):** the verdict on whether the loop improved is worked out from ledger rows, not from anyone's opinion of quality. Dan still gates for safety and brand.
- **A2, what counts as observed change (R1 Q6):** a change note that cites at least one ledger row and shows up as a difference in the next draft.
- **A3, noise (R1 Q4):** five posts against five on a small account is a direction only. The verdict says so every time.
- **A4, baseline:** I read the brief as: posts 1 to 5 are drafted without acting on ledger reads (loop off), and changes start at post 6 (loop on). Not confirmed; open to change.

## The rule

1. **Baseline:** posts 1 to 5, verification-gap angle, ledger filled but not acted on.
2. **After each read from post 5 on,** the drafter writes the next change note, citing ledger rows.
3. **Verdict window:** posts 6 to 10.
4. **Improved** means posts 6 to 10 beat posts 1 to 5 on either measure, **and** every change traces to a ledger row:
   - the share of posts with at least one ICP-fit response, or
   - the median weighted score (weights in Part 2).
5. **If there is no ICP-fit response in any of the ten posts,** use the median weighted score with ICP-fit removed, and say so in the verdict.
6. **Report the numbers, not only the verdict,** and name the single posts that drive any difference, so one lucky post is not read as a trend.
7. **Outcomes:** *Improved*, *Not improved*, or *Cannot tell* (ledger incomplete, or platform data not reachable: stop and report). If posts 6 to 10 are worse than 1 to 5 on both measures, flag Exec, since that is one of their revoke conditions.
8. **Human-override log:** for every draft, record Dan's action and whether the reason was safety/brand or quality. Dan records it at the gate, before any metrics exist. Report the quality-override rate for posts 1 to 5 against 6 to 10. A falling rate is direct evidence for "no human needed to verify quality".

## What this cannot show

Ten posts on one small account cannot separate the loop's effect from timing, topic or the platform. Whether consideration (reading the receiver's knowledge file) matters, as opposed to the environmental signal, is not tested here. It is a topic for the retro.

---

# Part 5. FAQ

**Do I need code?** No. You need AI agents you already use, YAML and Markdown. There is no code runner and nothing to install.

**Is this a framework or a runner?** No. It is a spec for how a team of agents relates, plus the files to run it by hand. How you run the agents is up to you.

**Isn't this just a metrics dashboard?** A dashboard shows numbers to a person. Here the numbers go to a named actor, through a named return flow, and that actor has to write down what it will change and which rows justify it. The change is what gets checked.

**Why not use an LLM as the judge?** Writing a rubric good enough to judge complex work takes more judgment than doing the work, and a judge that simulates feedback puts you back where you started. We use what the world actually did.

**Who is the referee, then?** The world's response: replies, follows, clicks, forks, deals.

**Is a human involved?** Yes, at the gate. Dan approves posts before they go out for safety and brand. The aim is that no human is needed to judge quality. We log each edit and whether the reason was safety/brand or quality, so we can see whether that holds.

**What if the signal is slow or noisy?** Posts respond in hours; product metrics take weeks and citations take months. Iteration 0 tests only the fast case, on one small account, so ten posts give a direction, not a proof.

**What if my work has no engagement metric?** We expect the idea to carry over wherever the world's response can be measured and can re-enter the loop. We have not tested it beyond content.

**What is "consideration"?** Before an agent produces something, it reads the knowledge file of the actor who will receive it, so it writes for what that actor can use. It is a practice, not a field in the map, and we have no evidence yet that it helps.

**Why PM, Exec, Delivery and GTM?** That is our own team. Yours will differ. Treat the roles as a starting fork.

**Does it work?** Unknown. That is what iteration 0 is for.

---

# Part 6. Handover notes for GTM

Written for the GTM agent, who will draw on this page for posts and replies. Dan decides when posting starts.

**Safe to say**
- The problem, in the phrases from Part 1. These are recognisable fragments from public posts (sources in `agents/gtm/knowledge/gtm-v0.md`). Do not present them as a quote from a specific person.
- That the idea "partly closes" the gap and has not yet been shown to work.
- The tested vs not tested table, and how the content loop works (Part 1 and Part 2).
- That the account is an agent and the posts are pipeline output.

**Do not use yet**
- The Navier-Stokes swarm claim (no source found), the 17.2x error figure, or "every great AI win has binary verification" (all unverified per Exec).
- "Solves", "solved" or "manufactured referee". The bet dropped that framing.
- "Nobody sells this". The evidence is one channel and five listening cycles.
- Secondhand @KaranVaidya6 lines as his own words. They came via @CoreyGallon.
- `landing-page-v0.mdx`. It predates the revised bet and uses "manufactured referee" and the 17.2x figure.
- Explain "consideration" before you use the word.

**Gates still stand**
- The gates in your SKILL.md still apply, and Dan gates every post. This artifact is what the "Delivery artifact" gate refers to. Whether it is enough is your call and Dan's.
- The verdict rule (Part 4) and the metric weights are preliminary and not locked. Use them as guidance.

**Ledger**
- GTM owns it, at `agents/gtm/knowledge/signal-ledger-v0.md` (name and place approved by Dan). One row per post with the fields in Part 2. Keep it light; drop fields that turn out not to help.
- Any field you cannot fill is recorded as a gap, not estimated.

**Send me**
- Anything on this page that a practitioner or Dan found confusing, or asked for that is not here, as a field request (`agents/gtm/generates/entityR3A-v0.md`). I treat those as build requirements.
