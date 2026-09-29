---
name: entityR2-v2
description: Delivery reality, iteration 2. The mechanism analysis conclusion (can the verification gap be closed without a continuous human, and how), what was built (analysis + root README), what it took, and feasibility confidence. Return flow from Delivery to PM.
entity: entityR2
direction: return
from: actor2 (Delivery)
to: actor0 (PM)
iteration: 2
status: open
last_updated: 2026-09-24
sources:
  - cowork
---

# entityR2: Delivery Reality (iteration 2)

Basis: `entity1-v2` (Exec brief, Low-Medium on explicitly partial inputs), `entity0-v2`
(revised bet), `decisions/2026-09-24-iteration-2-checkpoint-answers.md`, and the current
harness files. Input check per standing rule 9: **entityR3A and entityR4C do not exist** (no
GTMs field requests, no practitioner defects) — nothing blocks this pass. Required-input state
per iteration-2.yaml's State & inputs block, re-verified 2026-09-24: entityR2A missing (never
produced — see below), entityR3B stale at v0.

## The mechanism answer (core content — full analysis in `entity2-v2.md`)

**Question (entity0-v2):** can a system without a continuous human close the verification gap
by learning from how the world responds to its work?

**Verdict: partially — and the boundary is now precise.** The mechanism is the four-part
capability PM's framing set: **sense** (read the channels at fixed windows; raw snapshots; gap
records), **observe** (attribute responses to outputs — one-change-per-post is what makes this
possible; type responses by kind and cost), **interpret** (typed observations → a stated
reading with alternatives and confidence, against pre-registered frames), **learn** (change
notes citing ledger rows, with citation enforcement and a divergence flag). All four have
available substrates now; what must be built is mostly **discipline and record formats**, not
technology — and the paper-only parts (ledger, change notes, return routing) have never
executed. The ten-post run is the instrument that executes and tests the observe→learn half.

**The finding PM most needs:** the verification gap is **not eliminated — it is relocated and
shrunk**. Interpretation is itself knowledge work with no binary check: "what is a good
response *for*?" is a value judgment only a holder of intent can set. What the mechanism buys
is the human's retreat from **once-per-output to once-per-frame**: frame-setting (what counts as
good, who is the ICP, the weights), ambiguity tie-breaks (silence is three worlds in one
observable), and authorization of exposure (the publish gate — safety/brand/legal, not
quality). Human effort then scales with frames and ambiguities, not with outputs. That is a
real reduction and it is honest to claim it as "partially closes"; claiming "no humans" would
trip Exec's counter-evidence condition (c) on its face.

**What is genuinely unique:** not any single tool — pre-registration, single-case design and
qualitative coding all pre-exist — but the combination: (1) the question is changed from
unverifiable ("is this good?") to record-verifiable ("what did the world do, and did the next
output change because of it?"); (2) the human-override log with a quality/safety tag makes
"humans not needed for quality verification" a *measurable* claim (falling quality-override
rate) rather than a promise; (3) the YAML topology makes the routing itself inspectable and
diffable between runs — though the mechanism is substrate-independent and would run over a
disciplined human team too. Per owner direction: we do not claim topology is the answer; it is
the substrate that makes the mechanism operable by agents without a continuous human.

**Where humans remain necessary (named precisely):** publish-gate authorization; frame-setting;
ambiguity resolution; strategy leaps (feedback surveys what landed, never the search space of
what to make); environment surgery when platforms change the measurement setup. Also the
honest limits: n=10 on one small account is directional only; learning here is hill-climbing,
not strategy; organisational buying signals (months, multi-person) are outside the run's
window entirely.

**Instrumentation a PM needs** (full list in entity2-v2): readable response counts with gap
flags; typed responses with responder reasons; the change trail (row → note → visible draft
difference); interpretation records (meaning + alternative + confidence + mind-changer);
the human-override log; the divergence count. If these six arrive legibly each iteration, the
sense–observe–interpret–learn cycle is checkable from files alone.

## What was built

1. **`agents/delivery/generates/entity2-v2.md`** — the mechanism analysis, in full. It gates
   GTM's ten-post evidence run (owner sequencing, 2026-09-24) and specifies what the run must
   instrument: a one-post readability check first (condition (a) lives or dies on it), the D2
   loop as specced with the ledger row extended (`response_type`, `response_cost`, raw
   snapshots), one interpretation record per read window, the change-note check (cites rows AND
   visible difference), the divergence flag, and the override log. D1–D3 stand unchanged.
2. **`README.md` at the repository root** — owner-authorized this iteration
   (`decisions/2026-09-24-iteration-2-checkpoint-answers.md`). Complete product story, repo
   map, practical replication/adaptation guidance, honest tested-vs-not-tested status. Written
   under the standing rule 8 regime: mechanical scan and public-account review are **Loopy's
   step before publication** — I have flagged every passage needing review in my handoff report
   rather than self-clearing anything. No uncited figures used: the 11%/64% production
   statistics in entity1-v2 carry no source and appear nowhere in the README.

## What it took

One working session. The cost was mostly analysis, not writing. Constraints that shaped the
work:

- **The brief prescribes a frame, not a conclusion** (owner direction; entity0-v2). I analysed
  the four functions and the seven sub-questions without presuming topology, and the analysis
  landed on a mixed verdict — which entity0-v2's threshold 2 explicitly accepts as evidence.
- **Surprise: the gap reappears one level up.** Analysing the interpret function honestly
  showed the verification gap is not closed but relocated — interpretation is unverifiable
  judgment too. This reframes the deliverable claim from "solves" to "shrinks and audits", and
  it is the analysis's most decision-relevant finding: it defines what the run can and cannot
  demonstrate.
- **Most of "what must be built" is discipline, not code** — record formats and enforcement
  conventions. That is good news for the window and bad news for defensibility (low technical
  moat; the moat, per Exec's fresh business-model read, would have to be accumulated real-
  outcome data). Flagged for Exec's business-model thinking, not escalated (below).
- **README public-scope discipline:** every claim had to be either sourced, marked as our
  interpretation, or marked untested. The uncited statistics ban removed the two headline
  figures from consideration; the README leads with the mechanism's honest status instead.

## What is genuinely unique about the technical approach

Stated above under the mechanism answer. In one line: a record-verifiable reformulation of the
verification question (behaviour changed because of cited world-response, checkable from files
by an outsider), plus a measurable human-removal claim via the quality-override rate.

## What would take longer than the opportunity window

- **Frame validation and delegation** of interpretation rules to the system — needs several
  iterations of frames meeting outcomes before any judgment can be handed over.
- **Organisational-response sensing** — months-long, multi-person buying signals need windows
  the ten-post run does not have.
- **Larger-n sequential testing** (interrupted time series, always-valid intervals) — the
  statistics that would turn "directional" into "significant".
- **Automated multi-channel capture** — manual reads are fine at n=10.

None of these blocks the run; they are named so the verdict is not over-read.

## Flags

- **No entityR2A this iteration — deliberate, and stated because Exec expects one.** Exec's
  certification invited an escalation if Delivery uncovered "an urgent feasibility constraint".
  The analysis found a *structural* constraint (interpretation remains human judgment) but not
  an urgent one that reshapes certification: it is compatible with the bet as written
  ("partially closed") and with Exec's Low confidence on mechanism. The one genuinely urgent
  item — platform numbers may be unreadable at our access level (condition (a)) — is a run
  risk already inside Exec's revoke conditions, handled by the build-step-0 readability check
  rather than an escalation. If the run's check fails, that failure report is the escalation.
- **README review flags** are in my handoff report to Loopy (mechanical scan + public-account
  review are Loopy's step per the checkpoint decision and standing rule 8). Nothing in the
  README is self-cleared.
- **Uncited figures excluded from the README:** entity1-v2's 11%/64% production statistics
  have no source on file; they are not used. Same treatment for any other figure without a
  source.
- **Carried forward, still open:** D3's A4 assumption (baseline posts drafted without acting
  on ledger reads) is adopted by PM into the evidence threshold but never independently
  confirmed. The mechanism analysis does not depend on A4; the run's interpretation does.
- **Required inputs (standing rule 9):** entityR2A missing (my deliberate non-production,
  above — Exec already certifies on partial inputs); entityR3B stale at v0 (GTM's to refresh).
  Neither blocks this pass; both named at handoff as required.
- **State & inputs block** (iteration-2.yaml map.notes) re-verified 2026-09-24: all lines
  current as written; posting-gate line is GTM's to maintain.

## Feasibility confidence for the current bet

- **The mechanism being real in the observe→learn half:** medium-high on paper (the disciplines
  are standard and checkable), low in practice until the first ledger row exists. The run is
  the right next instrument and its failure modes are legible.
- **The mechanism holding in the interpret half without humans:** low — by the analysis's own
  finding, and that is the honest read to carry into the bet, not a delivery failure.
- **GTM executing the run with the added instrumentation:** medium. The additions (response
  typing, interpretation records, readability check) are small next to D2 as specced.
- **The README being publishable after Loopy's review:** high. Every flagged passage is minor
  (naming/attribution hygiene), none structural.

---
*Full mechanism analysis: `agents/delivery/generates/entity2-v2.md`. Root README: `README.md`.*
