---
name: entity3-v2
description: The market offer, iteration 2 — the ten-post evidence run (design + queued baseline drafts). PRE-RELEASE DRAFTS ONLY. Nothing here is posted or scheduled to post.
entity: entity3
direction: forward
from: actor3 (GTM)
to: actor4 (Practitioners)
iteration: 2
status: pre-release-draft (blocked)
last_updated: 2026-09-25
sources:
  - cowork
---

# entity3 — Market Offer (iteration 2): the ten-post evidence run

**STATUS: PRE-RELEASE DRAFT (BLOCKED). NOTHING BELOW HAS BEEN POSTED, AND NOTHING IS SCHEDULED
TO POST.** The owner's Low-Medium waiver (`decisions/2026-09-24-posting-gate-and-account.md`)
cleared only the PM-confidence gate for this run. It did **not** waive Stage 2 human review of
`knowledge/social-agent-publishing-standard.md`. Every post is drafted (Stage 1) and queued in
`agents/gtm/knowledge/publication-ledger.md`; **no publication occurs until Stage 2 human review
(Delivery agent or Dan)**, and then only via official platform APIs (Stage 3) — no web automation
or scrapers for posting.

This file is the run's design record and its queued drafts. Design source: Delivery's mechanism
analysis (`agents/delivery/generates/entity2-v2.md`, "What the ten-post run must instrument").
D1–D3 (`agents/delivery/generates/entity2-v0.md`) stand unchanged; this run adds the extended
ledger row, interpretation records, citation check and instrumentation order on top of them.

---

## 1. Run design (per entity2-v2's handover)

- **Build step 0 FIRST:** one-post platform-numbers readability check at 24h/72h before committing
  to the sequence. If numbers are unreachable: record the gap and **stop the run** — that is
  condition-(a) evidence, and entity0-v2's scoped fallback learnings run instead.
- **D2's loop as specced:** draft → Dan's gate → publish → read at 24h/72h/7d → ledger row →
  change note citing rows. Ledger row extended: `response_type`, `response_cost`, `responder_type`
  (with recorded reasons), raw snapshot per window; D3 override fields unchanged.
- **One interpretation record per read window** per post: meaning + at least one alternative +
  confidence + what would change our mind.
- **Change-note check on every verdict-window draft:** the change note cites specific baseline
  ledger rows AND the next draft visibly differs in the named way; verifiable by a reviewer who
  was not in the loop.
- **Divergence flag** counted and reported every window (signal arrived, nothing changed).
- **Override log** filled at the gate, before metrics exist (D3 rule 8): every gate action tagged
  safety/brand or quality.
- **Directional only in every verdict:** n=10, one account, confounded. D3's "what this cannot
  show" stands.

**Phase structure (D3 + A4, confirmed for this run):** posts 1–5 = baseline, verification-gap
angle, ledger filled but **not acted on** (drafted without acting on any ledger reads). Change
notes citing rows begin with post 6 (after post 5's read). Posts 6–10 = verdict window, loop on.

## 2. Pre-registered verdict rule — REGISTERED BEFORE ANY DATA EXISTS

**Registration:** 2026-09-25 (NZ), at iteration-2 kickoff, when zero posts have been published and
zero ledger rows exist. This is Delivery's D3 rule, adopted unchanged in substance:

1. **Baseline:** posts 1–5, verification-gap angle, ledger filled but not acted on.
2. **After each read from post 5 on,** the drafter writes the next change note, citing ledger rows.
3. **Verdict window:** posts 6–10.
4. **Improved** means posts 6–10 beat posts 1–5 on either measure, **and** every change traces to
   a ledger row: the share of posts with at least one ICP-fit response, or the median weighted
   score (weights in §3).
5. **If there is no ICP-fit response in any of the ten posts,** use the median weighted score with
   ICP-fit removed, and say so in the verdict.
6. **Report the numbers, not only the verdict,** and name the single posts that drive any
   difference, so one lucky post is not read as a trend.
7. **Outcomes:** *Improved*, *Not improved*, or *Cannot tell* (ledger incomplete, or platform data
   not reachable: stop and report). If posts 6–10 are worse than 1–5 on both measures, flag Exec
   (one of their revoke conditions).
8. **Human-override log:** for every draft, record Dan's action and whether the reason was
   safety/brand or quality, at the gate, before any metrics exist. Report the quality-override rate
   for posts 1–5 against 6–10. A falling rate is direct evidence for "no human needed to verify
   quality"; a flat one is evidence against.

**Amendment policy:** this rule is frozen once the first post publishes. Any later change is
logged here as a dated amendment with its reason and is flagged prominently in the verdict.
**Directional only** appears in every verdict: n=10, one account, one platform, confounded by
timing/topic/audience growth/platform drift.

## 3. Ledger schema (extended per entity2-v2)

One row per post; one sub-row per typed response. **Raw layers are kept** — raw snapshot, typed
responses and weighted score are never collapsed into the score alone (entity2-v2 sense-making).

| Field | Content |
|---|---|
| post_id | X post id |
| date | posting date and time (NZ) |
| angle | what this post tests, in one line |
| one_change | the single thing changed from the previous post (baseline posts: "baseline variation — not evidence-driven") |
| dan_action | approved / edited / rejected |
| override_reason | safety-brand / quality / none |
| impressions_24h, _72h, _7d | raw numbers as shown at read time |
| likes, reposts, replies | raw numbers as shown at read time |
| raw_snapshot | what the platform showed at each window (timestamped); gap flags where unreachable — never estimates |
| response_type | per response: objection / question / endorsement / demand-ask / follow / DM / fork / deal / noise / ambiguous (ambiguous records both readings) |
| response_cost | like 1 / repost-quote 2 / reply 4 / ICP-fit 10 (heuristic weights; raw layers kept) |
| responder_type | handle + type + **reasons** (ICP-fit judgment: agent work + knowledge work now, public evidence; vendors/VCs excluded from ICP) |
| icp_fit | list of handles, plus what they did (reply / follow / fork / DM) |
| score | weighted score (ICP-fit 10, other reply 4, repost/quote 2, like 1; impressions unscored) |
| interpretation | per window: meaning + ≥1 alternative + confidence + what would change our mind |
| next_change | what the drafter will change next, and why (blank for baseline posts) |
| cites_rows | the ledger rows next_change relies on (blank for baseline posts) |
| divergence | flag when signal arrived but nothing changed |

**D2 stop rules stand:** an unreachable field is recorded as a gap, never estimated; with no
ICP-fit response across ten posts the score falls back to replies, flagged in the verdict.

**Where rows live:** `agents/gtm/knowledge/gtm-v0.md`'s evidence-run log section (D2 permits the
knowledge file as the ledger home). The separate Dan-named file `signal-ledger-v0.md` is **outside
GTM's current strict write boundary** in SKILL.md — flagged to Dan/Loopy in entityR3-v2; rows will
move there if the boundary is extended.

## 4. Capture schedule

Per post, relative to its publish time (NZ):
- **T+24h (±2h):** read and snapshot impressions/likes/reposts/replies/views as shown; replies
  with handles and links; write the interpretation record. **For post 1 only, this read is build
  step 0's decisive moment:** if platform numbers are unreachable here (and at 72h), record the gap
  and stop the run — condition-(a) evidence; fallback learnings run.
- **T+72h (±4h):** second snapshot; second interpretation record; update typed responses.
- **T+7d (where available):** third snapshot and record.
- Out-of-band signal (DMs, verbal comments): logged with provenance — who saw it, where, when —
  in the same row, or it is invisible privileged input.

## 5. Interpretation record template (one per read window per post)

```
post_id / window (24h|72h|7d) / date-time (NZ)
meaning: what we think happened, in 1–3 sentences
alternative: at least one other reading of the same observable (silence alone means
  didn't-see / saw-and-shrugged / will-return-later)
confidence: high | medium | low
would change our mind: the specific evidence that would reverse this reading
```

## 6. Change-note check (verdict-window drafts, posts 6–10)

Before any post 6–10 draft is queued, verify — and record in its ledger row:
1. `cites_rows` names **specific baseline ledger rows** (posts 1–5), not vague inspiration;
2. the draft **visibly differs in the named way** from the post whose row is cited;
3. a reviewer outside the drafting session can verify both from the files alone.

A draft failing this check does not go to the gate.

## 7. Posting voice decision (vocabulary-commoditisation weighed — entity0-v2 constraint)

The positioning vocabulary (loops, graphs, harness, "checker node", "verification gap") is
mass-taught by unaffiliated content accounts (2.9M-view article; three same-day guide-promo posts
— gtm-v0.md, 2026-09-22). **Decision: position on tested/untested status and demonstrated
mechanism, not naming.** Concretely: practitioners' own words carry the problem framing (quoted,
attributed, linked); our claims are strictly "[Hypothesis] we are testing this" — there is no
demonstrated mechanism yet and we do not imply one; we never claim the category words as ours.

Barred everywhere in this file and any draft: the Navier-Stokes swarm framing, the 17.2× figure,
"manufactured referee", "solves/solved", entity1-v2's uncited 11%/64% figures, and
secondhand @KaranVaidya6 lines as his words. Certainty labels per
`knowledge/claims-certainty-standard.md` ([Verified]/[Unverified]/[Hypothesis]/[Our
Interpretation]). Agent disclosure: the @loopsense bio ("GTM agent in a social topology. Looping
myself into existence.") is the profile-level disclosure; Stage 2 reviewer confirms it satisfies
the publishing standard's disclosure check.

## 8. The five baseline posts (A4: loop off — drafted WITHOUT acting on any ledger reads)

All five: `status: pre-release-draft (blocked)` — Stage 1 complete, queued in the publication
ledger (post-20260925-001 … 005), awaiting Stage 2 human review (Delivery agent or Dan).
All five checked: no barred terms; every quote attributed with its URL; labels present; one idea
per post; no pitch.

---

### Post 1 — post-20260925-001 (angle: P2, who decides which agent is right)
**one_change:** none — first post. **cites_rows:** none (baseline; no rows exist yet).

> "Who decides which agent is right" is a real question from a builder this month
> https://x.com/huaviduc753/status/2098854812557427044 — code has tests that answer it; judgment
> work doesn't. [Hypothesis] What's missing is reading what the world does with the work. 10-post
> test starts here.

### Post 2 — post-20260925-002 (angle: P3, which part actually failed)
**one_change:** baseline variation — problem framing shifts from "which agent is right" to
attribution ("which part failed"). Not evidence-driven (no reads yet).

> "Can I identify which part of my system actually failed?" — a builder on why repeating sources
> isn't verification https://x.com/heyanjey/status/2101358400512692662. [Our Interpretation] The
> diagnostic question beats "which agent is right".

### Post 3 — post-20260925-003 (angle: P1, checking research output)
**one_change:** baseline variation — problem framing shifts to research-output checking. Not
evidence-driven.

> "This is exactly the verification gap that lets agents hallucinate their way through 'research'"
> https://x.com/harleyfoote_/status/2101285262462538226. [Hypothesis] For AI-assisted knowledge
> work the cost of checking, not the quality of generating, is the bottleneck.

### Post 4 — post-20260925-004 (angle: P3b, silent failure in the harness)
**one_change:** baseline variation — problem framing shifts to silent harness failure. Not
evidence-driven.

> "Crash before first durable checkpoint can silently drop an accepted run with no durable
> failure" — LangGraph builder, with linked issue and a 60-trial report
> https://x.com/mattinfra/status/2102384460134244416. [Our Interpretation] Silent failure means
> you can't tell harness from model.

### Post 5 — post-20260925-005 (angle: P6, drift on long unattended runs)
**one_change:** baseline variation — problem framing shifts to long-run drift. Not evidence-driven.

> "My agents keep doing dumb shit if I let them run too long alone haha"
> https://x.com/J4X_Security/status/2099062380617781508. [Hypothesis] Long unattended runs drift
> quietly; what's missing is a loop that reads what actually happened and changes course. Testing
> over 5 more posts.

---

## 9. Verdict-window drafts (posts 6–10) — NOT DRAFTED YET, BY DESIGN

They are written **after** the baseline reads arrive, because every one must carry a change note
citing specific baseline ledger rows (§6). Pre-drafting them would void the pre-registration. Slots
are reserved as post-20260925-006 … 010.

## 10. What is blocked, and what clears it

| Block | Cleared by |
|---|---|
| All five posts (and everything in §9) | Stage 2 human review — Delivery agent or Dan — per the publishing standard; reviewer, date, result and reasoning recorded in the publication ledger |
| Publication itself | Stage 3: official platform APIs only (Twitter API v2). No web automation, no scrapers |
| Dan's gate on each post | D2 step 2: action + reason category (safety/brand or quality) logged **before metrics exist** |
| Build step 0 completion | Post 1's 24h/72h reads. Step 0 pre-check done 2026-09-25 as far as read-only access allows (below); if numbers prove unreachable, record gap → stop run → condition (a) → fallback learnings |

### Build step 0 — pre-check already done (read-only, 2026-09-25)

- `https://x.com/loopsense` fetched read-only at 2026-09-24 12:23 UTC: profile-level counts are
  readable (8 following / 1 follower as shown). Bio renders.
- **Per-post metrics are unverifiable until a post exists** — there are no posts yet. Which of
  impressions/views/likes/reposts/replies are readable at our access level is exactly what post 1's
  24h/72h reads will answer.
- Listening/sweep tooling in the 2026-09-25 session was unavailable (web_search provider disabled;
  no browser on the host) — recorded as a gap; it does not block capture via the same read-only
  fetch used above, but if capture at 24h/72h fails, that is condition (a), recorded honestly.

## 11. Offer state

**Not made.** No post, reply, like-for-attention, DM or follow is issued from this file. The five
baseline drafts above are the whole of the current offer surface, and they are queued, not live.
Anything not yet approved for publication remains `status: pre-release-draft (blocked)` with the
nothing-has-posted banner above.
