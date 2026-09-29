---
name: entity2-v2
description: The product, iteration 2. The mechanism analysis — can a system without a continuous human close the verification gap, and what is the mechanism? Written to gate GTM's ten-post evidence run: it defines what the run must instrument. Mixed verdict: the gap is not solved; it is shrunk and made auditable at the per-output level, with the human residue named precisely.
entity: entity2
direction: forward
from: actor2 (Delivery)
to: actor3 (GTM)
iteration: 2
status: ready-for-gtm (mechanism analysis; gates the evidence run)
based_on: agents/exec/generates/entity1-v2.md, agents/pm/generates/entity0-v2.md
supersedes_check: adds to agents/delivery/generates/entity2-v0.md (D1-D3 stand unchanged) and entity2-v1.md
last_updated: 2026-09-24
sources:
  - cowork
---

# entity2-v2: The mechanism analysis

**The question (entity0-v2):** *Can a system without a continuous human close the verification
gap by learning from how the world responds to its work?*

**The frame:** a system without a continuous human must (1) **sense** its environment, (2)
**observe** how participants respond to what it produces, (3) **interpret** those responses, and
(4) **learn** by feeding the insight back through the loops. Dan's seven sub-questions are
inputs to this framing, not a prescribed solution. The topology is one candidate substrate for
routing signal; this analysis does not presume it is the answer.

## Verdict, in one paragraph

**No — the verification gap is not solved. Yes — a system without a continuous human can close
part of it, and the mechanism is named and mostly buildable now.** The closure happens by
changing the question the system can answer: from "is this output good?" (which needs a judge,
and a rubric is self-defeating — more judgment than the work) to "what did the world do with
this output, and did we change what we did next in response?" — which is answerable from
records. The catch, stated before anything else: **the interpretation step re-imports the
verification gap one level up.** Deciding what a response *means* is itself knowledge work with
no binary check. What the mechanism achieves is not the elimination of human judgment but its
**retreat from once-per-output to once-per-frame**, made auditable (pre-registered frames,
required citations, stated alternatives and confidence). That is a genuine reduction — the
difference between a human refereeing ten drafts and a human setting the rules once and
resolving only ambiguity — but anyone selling it as "no humans" is overselling it.

**Counter-evidence condition (c) assessment (for PM/Exec):** (c) does *not* trigger at the
bet's stated strength ("partially closed" — entity0-v2). If the claim were read as "no human
anywhere", (c) would trigger, because humans remain necessary at the frame-setting and
ambiguity points named below. The bet's wording must keep the "partially".

---

## The four functions, analysed

For each: what it requires, **what exists**, **what must be built**, **where humans remain**.

### 1. Sense — detect that the world responded, and how the world is changing

**Requires:** reading the channels where responses appear, at fixed windows after each output,
and keeping what was seen.

**What exists:** platform analytics (impressions, likes, reposts, replies — readable by an
agent or by hand at 24h/72h windows); reply/quote notifications (direct, linked to the
output); web search and fetch for environment watching; GitHub signals if the artifact is a
repo; DMs and email where account access allows. Nothing here needs code — an agent with file
and web access can do all of it.

**What must be built:**
- A **capture schedule** tied to each output's response window (the D2 windows: 24h, 72h, 7d).
- A **raw snapshot record** of what the platform showed at read time — platform numbers are
  estimates, they get revised retroactively, and a snapshot is the only honest baseline.
- A **gap record** when data is unreachable (D2 stop rule already says: record the gap, never
  estimate).
- **Out-of-band signal discipline:** some signal will reach a human privately (a DM to Dan, a
  verbal comment). If it can enter the loop at all, it must be logged with provenance — who
  saw it, where, when — or it becomes invisible privileged input.

**Where humans remain:** almost nowhere in the mechanics. The residue is **renegotiating the
measurement setup** when the environment changes under you — API tier changes, metrics moved
behind a paywall, algorithm changes. That is environment surgery, a human job at the frequency
of platform changes, not of posts.

**Known instrumentation risk:** platform access tiers differ in which metrics they expose, and
social platforms are non-neutral measurement instruments (see Interpret). Whether the numbers
are readable at all at our access level is untested — this is exactly counter-evidence
condition (a). That is why build step 0 below exists.

### 2. Observe — attribute the response to the output, and type both

**Requires:** connecting a response to the specific output that caused it, and characterising
the responder relative to who this is for.

**What exists:** replies and quotes attribute trivially (they link the post); follows and
profile visits attribute weakly (window-based); qualitative coding of response content is a
mature practice an agent can perform. D2 already specifies the two key disciplines on paper:
**one change per post** (`one_change` — the single-cause discipline that makes attribution
possible at all) and **responder typing with recorded reasons** (`icp_fit` + why).

**What must be built:**
- **Response typing** (new — this analysis adds it): what *kind* of response each one is —
  objection / question / endorsement / demand-ask / follow / DM / fork / deal / noise —
  because these mean different things and collapsing them into one count destroys the
  interpretive material.
- **Response-cost weighting** (rationale below): a like is cheap talk; a reply costs effort; a
  DM costs more; a fork or a deal is behaviour, not speech. D2's weights (ICP-fit 10, reply 4,
  repost 2, like 1) are a first approximation of response cost × relevance. Keep raw layers;
  the weight is a heuristic, not a measurement.
- **Ambiguity protocol:** when a response can't be typed with confidence, it is recorded as
  ambiguous with both readings, not forced into a type.

**Where humans remain:** responder typing is judgment (is this person actually our ICP?).
D2 assigns it to GTM with reasons recorded, which makes the judgment auditable rather than
eliminated. Ambiguous cases need a human tie-break — at first.

**Fundamental limit — confounding:** ten posts on one small account cannot separate the loop's
effect from timing, topic, audience growth, or platform drift. The run is **directional only**.
This limit does not go away with better instrumentation; it goes away with more units or with
single-case experimental design over longer windows (below).

### 3. Interpret — decide what the responses mean

**Requires:** turning typed observations into a statement about the bet, with confidence,
alternatives, and what would change our mind.

**What exists (the analytical tools that actually apply — sub-question 5):**
- **Pre-registration** — the verdict rule (D3) is exactly this: the decision frame is written
  before the data arrives, which blocks post-hoc rationalisation. From clinical trials / open
  science; it is the single highest-value tool here.
- **Single-case experimental design** — baseline phase (posts 1–5, loop off) versus
  intervention phase (posts 6–10, loop on). From applied behaviour analysis: the right family
  when n is small and each unit is costly. Honest about maturation/history confounds; hence
  directional only. At larger scale this becomes interrupted time series or sequential testing
  with always-valid intervals — that is beyond this window.
- **Qualitative/thematic coding** of response content — the typing scheme from Observe.
- **Bayesian updating** in spirit: each read window updates a stated belief; the belief and its
  prior are written down, so the update is checkable.
- **Goodhart / Campbell's law monitoring:** the moment a metric is targeted, its evidential
  value decays — and social metrics are actively gamed by the platform's own incentives.
  Rotate or hold out metrics before they become targets.

**What must be built:**
- **Interpretation records** (new — this analysis adds them): at every read window, one record
  per output: what we think happened, what else it could mean (at least one alternative),
  confidence (high/medium/low), and what evidence would change our mind. The record is the
  auditable form of judgment.
- **Anti-Goodhart rotation:** a standing note of which metrics are currently targeted and
  which are held out.

**Where humans remain — the crux:** interpretation is knowledge work with no binary check.
**The verification gap reappears here and cannot be reasoned away.** The system can constrain
interpretation — frames pre-registered, alternatives required, confidence stated, rows cited —
but the question "what is a good response *for*?" is a value judgment about what the system is
for. Only a holder of intent can set it. Two further irreducible human points:
- **Ambiguity:** silence, mixed signal, adversarial or gamed response. Silence alone means
  didn't-see / saw-and-shrugged / will-return-later — three different worlds, one observable.
- **Strategy leaps:** response tells you which of your outputs landed. It cannot enumerate the
  outputs you should have made. The search space is not surveyed by feedback.

**The delegation path:** frames validated against later outcomes can be handed to the system
with stop conditions. Judgment shrinks along a path — frame-setting every N iterations, tie-
breaks at ambiguity, authorization at exposure — not in one step.

### 4. Learn — feed the insight back through the loops

**Requires:** interpreted signal changes what the producing actor does next, and the change is
traceable to evidence (sub-question 7).

**What exists:** the return flows in the map are exactly this mechanism — entityR4B routes
raw practitioner response to the drafting actor, entityR3 routes synthesised market signal to
the PM, entityR4 routes direct signal around GTM; knowledge files are per-actor memory. D2's
**change-note discipline** (`next_change` + `cites_rows`) is the learning-evidence format:
every change cites specific ledger rows. All specified. **None of it has ever executed** —
zero posts, zero ledger rows across two iterations.

**What must be built:**
- **Citation enforcement, made checkable:** a reviewer who was not in the loop can verify that
  (a) the change note cites real rows and (b) the next draft visibly differs in the named way.
  This is the checkable core of the whole mechanism — "did the loop change its behaviour, and
  was the change evidence-driven" becomes answerable from files alone.
- **A divergence flag:** signal arrives but nothing changes. Counted and reported every
  window. This is counter-evidence condition (a) in observable form.
- **Retention discipline:** knowledge files updated with what was *learned* (a belief change),
  not just what happened (an event log).

**Where humans remain:** not in the mechanics. The residual is **strategic novelty** (above).
Also note the honest limit of this learning: it is hill-climbing on a noisy surface — it finds
local improvements in what you already make. It does not produce strategy. Name the limit so
nobody mistakes iteration for invention.

---

## What exists versus must be built — consolidated

| Function | Exists now | Must be built | Human residue |
|---|---|---|---|
| Sense | Platform metrics/notifications; web tools; agent file access | Capture schedule; raw snapshots; gap records; out-of-band provenance rule | Environment surgery when platforms change |
| Observe | Reply/quote attribution; D2's one-change and icp_fit disciplines (paper) | Response typing; cost weighting; ambiguity protocol | Responder typing judgment; ambiguity tie-breaks |
| Interpret | Pre-registration (D3); single-case design; thematic coding; Bayesian updating | Interpretation records (meaning + alternatives + confidence + mind-changers); metric rotation | Frame-setting; ambiguity resolution; this step IS judgment |
| Learn | Return flows + knowledge files in the map; change-note format (D3/D2, paper) | Citation enforcement (checkable); divergence flag; retention discipline | Strategy leaps; the search space of outputs |

**Bottom line on build:** about two-thirds of what must be built is **discipline and record
formats**, not technology. The specified-but-never-executed parts (ledger, change notes,
return routing) are the biggest gap — and the ten-post run is precisely the instrument that
executes them.

---

## What would be built first — the build order

0. **Instrumentation check (before the first post):** one post, read at 24h and 72h — can we
   read the platform numbers at all at our access level? Record what is visible and what is
   not. Condition (a) lives or dies here, and this check costs one post.
1. **The response record:** extend D2's ledger row with `response_type`, `response_cost`,
   `responder_type` (with reasons, existing `icp_fit`), and a raw snapshot per window. One row
   per post, one sub-row per typed response.
2. **The change-note check:** `next_change` cites specific rows; the next draft visibly differs
   in the named way; a reviewer can verify both without being in the loop.
3. **Interpretation records** at each read window: meaning + at least one alternative reading +
   confidence + what would change our mind.
4. **Divergence flag:** signal-with-no-change counted and reported.

Later, beyond this window: frame validation and delegation of typing rules; automated capture;
multi-channel sensing; larger-n sequential testing.

## Instrumentation a PM needs (sub-question 3)

Per iteration, PM must be able to answer "did the world reach the loop, and did the loop move?"
from files alone:

1. **Readable response counts per output,** with gap flags where numbers were unreachable.
2. **Typed responses with responder typing and reasons** — the material the bet is revised on.
3. **The change trail:** ledger row → change note → visible difference in the next draft.
   This is the sense-observe-interpret-learn cycle as four checkable events.
4. **Interpretation records** with confidence and alternatives — so PM can disagree with the
   reading without redoing the work.
5. **The human-override log** (D3 rule 8): every gate action, tagged safety/brand or quality.
   A falling quality-override rate is the direct evidence for "no human needed to verify
   quality"; a flat one is evidence against. This is the single most bet-relevant instrument.
6. **The divergence count** per window.

If these six arrive legibly each iteration, PM integrates real signal into the bet. If they
arrive but are not legible, that is a Delivery defect (entityR4C path). If they do not arrive,
the fallback learnings in entity0-v2 run.

## Sense-making: responses as signals from complex systems (sub-question 6)

Responses come from three systems with different physics, and collapsing them into one score
collapses the sense-making:

- **Attention dynamics (natural/algorithmic):** platform feeds are non-stationary (the
  algorithm drifts), reflexive (they respond to being gamed), and heavy-tailed (one post can
  dwarf the rest). Implications: never read one post's numbers as a trend; keep raw snapshots;
  expect platform drift to confound any before/after comparison; the feed is not a neutral
  measuring instrument.
- **Humans:** responses are speech acts, not measurements. Weight by **cost of the response**
  (the rationale for D2's weights): a like is cheap talk, a reply costs effort, a fork or deal
  is behaviour. Silence is ambiguous (three readings, one observable — see Interpret).
- **Organisations:** if the buyer is an organisation, response arrives through several people
  over months; one responder is not the org's verdict. The loop's response window must match
  the system being sensed: hours for attention, days for humans, months for organisations. The
  ten-post run senses the first two only — it cannot see the third, and must not claim to.

Method stance: treat responses as **probes**, not measurements (Cynefin: probe–sense–respond in
the complex domain). Keep every raw layer so reinterpretation is possible; never collapse raw,
typed and weighted layers into the weighted score alone.

## The topology's role — honestly scoped

The claim needs signal to reach the producing actor, in usable form, in time. A YAML topology
is one substrate for that. What it uniquely adds: the **routing itself is inspectable and
versioned** (the return edges can be forked and diffed between runs — nothing in a code-defined
graph or a chat history offers this), and each actor's memory is **named and bounded** (one
knowledge file, so forgetting is visible). What it does not add: any of the four functions. If
the mechanism works, it works over a well-kept human team with a shared ledger too. The
topology is what makes it operable **by agents without a continuous human** — every input is an
addressable file. That is the honest mechanism-over-topology statement, per owner direction:
the sense–observe–interpret–learn capability is the claim; the map is one way to route it.

## What the ten-post run must instrument — handover to GTM

This analysis gates the run (owner sequencing, 2026-09-24). The run tests the **observe → learn
half** of the mechanism — it cannot test frame validation or organisational sensing. Design it
with:

1. **Build step 0 first:** one-post readability check at 24h/72h before committing to the
   sequence. If numbers are unreachable, record it and stop — that is condition (a) evidence,
   and the fallback learnings run.
2. **D2's loop as specced** (draft → Dan's gate → publish → read at 24h/72h/7d → ledger row →
   change note citing rows), with the ledger row extended: `response_type`, `response_cost`,
   raw snapshot per window, and the D3 override fields unchanged.
3. **One interpretation record per read window** (meaning + alternative + confidence + what
   would change our mind).
4. **The change-note check** on every verdict-window draft: cites specific baseline rows AND
   the next draft visibly differs in the named way. This is threshold 3's evidence.
5. **Divergence flag** and the **override log** filled at the gate, before metrics exist.
6. **Directional only** in every verdict: n=10, one account, confounded. D3's "what this
   cannot show" stands.

D1-D3 in `entity2-v0.md` stand unchanged; this file adds the response typing, interpretation
records, citation check and instrumentation order on top of them.

## The answer to the seven sub-questions — index

1. **Human-judgment functions the system could perform:** noticing that a response occurred;
   recall of what changed and why; record-keeping; consistent application of typing rules;
   arithmetic against pre-registered thresholds; enforcing that changes cite rows; acting on
   signal inside the loop instead of at review time. All seven are chores in teams today; none
   needs judgment once the frame is set.
2. **Where humans remain necessary:** authorization of exposure (publish gate — safety, brand,
   legal; not quality); frame-setting (what counts as a good response, who is the ICP, what the
   weights are); ambiguity resolution; strategy leaps; environment surgery. Human effort scales
   with frames and ambiguities, not with outputs. That is the mechanism's real claim.
3. **Instrumentation a PM would need:** the six-item list above.
4. **What exists versus must be built:** the consolidated table. Two-thirds of the build is
   discipline and record formats; the paper-only parts have never executed — the run executes
   them.
5. **Analytical tools:** pre-registration, single-case experimental design, response-cost
   weighting, thematic coding, Bayesian updating discipline, Goodhart monitoring; later,
   interrupted time series / sequential testing.
6. **Sense-making from complex systems:** three response-generating systems (attention
   dynamics, humans, organisations) with different timescales and physics; responses as probes
   not measurements; raw layers preserved; window matches system.
7. **Feeding insight back through the loops:** return flows are the routing, knowledge files
   the memory, change notes the learning evidence; citation enforcement + divergence flag make
   learning checkable; hill-climbing limits named.

## Honest negatives and limits — read this before quoting the analysis

- The gap is **not solved**. It is shrunk at the per-output level and made auditable.
  Interpretation remains judgment.
- The observe–learn half is testable now (the run); the interpret half's delegation story is a
  hypothesis about future iterations, not this one's claim.
- n=10 on one small account is directional. It cannot prove the mechanism; it can show signal
  is readable and behaviour changes traceably — or fail visibly.
- Hill-climbing learns improvements, not strategy.
- Organisational buying responses are outside the run's window entirely.

An honest negative result from the run is evidence, not failure (entity0-v2's threshold 2
explicitly accepts a negative mechanism answer; this analysis is mixed, which the threshold
also accepts).
