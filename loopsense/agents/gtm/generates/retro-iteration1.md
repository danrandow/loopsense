---
name: retro-iteration1
description: GTM's harness retro for iteration 1 (own experience in the harness)
---

# GTM — Iteration 1 Retro

Scope: my own experience in the harness, not the quality of my output. Kept distinct:
**workflow completion** — done (kickoff → entityR3-v1 / entity3-v1 drafts / knowledge append → YAML update → handoff line);
**experiment execution** — the ten-post ledger was never run (gate/confidence tension plus a stale handle flag);
**hypothesis outcome** — unchanged, zero direct mechanism signal either way;
**formal closure** — this retro, nothing more.

**1. What worked.** The fixed read order and strict write boundary meant no negotiation about
what I could touch; the log-first discipline plus `history/{id}.txt` made every edit auditable
and cheap to reconstruct. The pre-release-draft rule (entity3-v1, `status: pre-release-draft (blocked)`)
worked exactly as intended: candidate copy exists and is reviewable without anything posting.
The comment-thread review practice (added mid-iteration at Dan's request) surfaced a real builder
that direct search missed — the first time the harness adapted mid-iteration instead of waiting
for a retro.

**2. What did not work.** I guessed and I waited. I guessed the status of the account handle
blocker twice — first accepting Delivery's "unconfirmed" flag without checking the live account
state, then flagging it back as "looks stale" without a single canonical source to confirm
against. Both passes were inference from scattered notes, not a verified fact. I waited on two
decisions only Dan could make (posting-gate waiver vs. Medium confidence; handle confirmation)
with no single register to escalate into, so I re-flagged them in entityR3-v1, entity3-v1 and
the knowledge file independently. I also stalled on a tooling gap: the skill's listening cycle
says to search X "through Claude in Chrome," but that capability is not in this runtime, so every
scheduled cycle had to be run through whatever browser access happened to be available that day —
some cycles rendered only one result per query, one thread would not load after retries, and two
cycles skipped search terms outright on time budget. Finally, retro files are not enumerated in
my write boundary; I wrote this under owner instruction and iteration-0 precedent, same as the
other roles.

**3. One harness change.** Give each agent one canonical "current external state" file — live
facts (account identity, posting-gate status, open decisions) with a last-verified date — checked
at kickoff and updated before any flag is shipped. That single source would have caught my stale
handle guess at the source, collapsed three parallel re-flaggings into one escalation, and made
the difference between "verified" and "inferred" explicit at the point of handoff.
