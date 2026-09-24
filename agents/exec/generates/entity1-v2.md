---
entity: entity1
label: Iteration 2 brief — evidence run viability
version: v2
iteration: 2
author: exec
updated: 2026-09-24
status: certified-brief
---

# Exec Brief — Iteration 2 (Certified, Low-Medium)

**Certified:** 2026-09-24. PM's revised aligned bet `agents/pm/generates/entity0-v2.md` (commit
f8bac77). Tested question: *Can a system without a continuous human close the verification gap by
learning from how the world responds to its work?*

**Basis of certification:** proceeding on partial inputs, explicitly. `entityR2A` (Delivery cost
& risk) has never been produced and `entityR3B` (GTM pipeline) is stale at v0 (iteration 0) — two
of four required inputs are missing or stale. Waiting would stall the forward pass for inputs
that cannot arrive before Delivery and GTM have run; the bet as revised is designed to generate
the very evidence those inputs would carry. This certification is therefore made without a cost
& risk case and without a current pipeline read, and both are requested this iteration (see
Constraints). `entityR4` / `agents/practitioners/generates/` remains absent.

This brief is the operative instruction for Delivery and GTM alongside entity0-v2. Where it is
silent, entity0-v2 governs; where they conflict, the owner decisions of 2026-09-24 govern.

## 1. Who is the customer — specifically (provisional, by design)

**Honest status: the buyer is not yet identified.** Seven listening cycles produced zero ICP
matches, and a genuine buyer usually leaves a trace. This brief does not paper over that. Per the
owner's direction, the search is restructured: find real, sourced problems first, then the people
who have them. The grounded catalogue is the instrument that firms or replaces this section.

**Provisional customer frame (to be confirmed or replaced by the catalogue before any offer is
made):** the person doing AI-assisted knowledge work — strategy, discovery, research synthesis,
content — whose output currently needs a human to check it before it counts. Their job title
varies (founder, product lead, consultant, research lead); the shared property is that **their
work has no cheap binary check**, unlike code (tests) or data entry (rules). Their current tool
is human review — themselves or a colleague as the verification gate — which is either slow
(expensive) or skipped (unreliable). The conversation they are already having is the one GTM has
documented: "verification gap", "checker node", "who reviews the agent's work" appearing as
organic vocabulary in the wild (8+ independent posters, 11–20 Sep 2026; trend #3 in the Fall 2026
State of AI Report). That vocabulary being public cuts both ways: it confirms the pain is real
and shared, and it commoditises the naming (see Positioning).

**What replaces this section if the catalogue disagrees:** if the grounded catalogue names real
problem groups that differ from this frame, GTM brings the groups and PM revises the bet; no
offer (`entity3`) goes out on the provisional frame alone.

## 2. Market positioning — one sentence

For practitioners whose AI-generated knowledge work has no cheap way to be verified, LoopSense is
an open loop topology that closes part of the verification gap with real-world response instead
of human review or simulated judgement; unlike LLM-as-judge and synthetic-persona validation
(loopi.tech), we route what actually happened back through the loop, and unlike human-in-the-loop
review, we do not make the human the permanent verifier.

**Caveat Delivery and GTM must respect:** the vocabulary in that sentence is being taught at
scale by unaffiliated accounts. Do not position on naming. Position on demonstrated mechanism and
real evidence — which does not exist yet and is what this iteration produces. Until the run
lands, the honest public claim is "we are testing this", not "this works".

## 3. Investment thesis — why now, why this (business model, treated fresh)

**Why now:** every major AI capability win has had binary, cheap verification (tests for code,
rules for typing/OCR). Knowledge work has none, the gap is now named in the wild, and 2026
production data shows why it bites (11% of multi-agent systems reach production; 64% of tasks do
better single-agent than orchestrated). The window is real but closing on vocabulary: the framing
is being commoditised before we have a mechanism to differentiate on.

**Fresh business-model read (not inherited):** two monetisation paths were on the table —
(A) attention-first open spec, later hosted signal-routing/ledger connectors; (B) loop-design
work from Dan's consulting base. The fresh read changes the weight, not the paths:

- Vocabulary commoditisation means the attention-first moat can no longer come from naming or
  thought leadership. If path A holds, the moat must be **accumulated real-outcome data** —
  ledger rows and verdict outcomes nobody else has (the community + data flywheel precedent).
- That makes this iteration's ten-post run a direct test of the monetisation substrate: can a
  small account produce readable environmental signal at all (entityR1-v0 Q4, still unanswered)?
  If yes, the data flywheel is plausible and path A stands. If signal is unreadable even in
  miniature, path A weakens sharply and the near-term commercial asset is the **instrumentation
  and loop-design capability** (path B, or tooling) — a smaller but real business.
- No revenue target this iteration; `entityR4A` (revenue signal) is correctly empty.

**Why this team:** the composable-loop-topology position (YAML-defined, inspectable, composable
— between free mesh and adaptive graph) is a genuine architectural insight in search of evidence,
and Dan's environment-as-verifier reframe is the non-obvious insight competitors have missed:
the verifier is not a judge you build but the world you measure. Both are hypotheses. This
iteration is what converts them from architecture to evidence or fails honestly.

## 4. Constraints — what is off the table; what revokes this certification

**Off the table this iteration:**
- No revenue targets, pricing, or paid-layer build. Path A's hosted layer is thesis only.
- No public claim of working verification. Public material says "testing", cites sources,
  passes standing rule 8 review before publication. No unsourced claims in any public draft.
- No fabricated catalogue. If real problems cannot be sourced, GTM says so and stops that
  initiative (entity0-v2's rule; a fabricated catalogue is failure, not partial success).
- No spend beyond existing accounts and tooling. `@loopsense` is the confirmed posting account.
- No sequence violation: the ten-post evidence run happens **after** Delivery's mechanism
  analysis has landed (owner, 2026-09-24). Not parallel, not before.

**Cost & risk caveat:** this certification is made without `entityR2A`. If Delivery's work
uncovers an urgent feasibility constraint, produce `entityR2A` as your skill directs — it can
reshape or revoke what is certified here.

**Certification is revoked (or returned next cycle) if:**
- The catalogue ships invented use cases (counter-evidence threshold (b) plus a process failure).
- Public material goes out without standing rule 8 review or with private material.
- The run proceeds before the mechanism analysis (owner sequencing).
- `entityR3B`'s absence resolves badly: the catalogue finds real groups but none reachable and
  none resembling the buyer frame (entity0-v2's (d)) — then the buyer question gets the harder
  look entityR1-v1 demanded and GTM's strategy pivots before further spend.
- Accumulated counter-evidence across iterations shows the sense–observe–interpret–learn
  capability is unavailable and unbuildable, with humans necessary at exactly the claimed points.
  Per the owner, no single failed test revokes anything.

## 5. What success looks like in 90 days, and how we measure it

**Iteration-2 close (the checkable gate):** entity0-v2's three-part evidence threshold, all three
visible in files — (1) a grounded catalogue of real, sourced problems naming the groups that have
them; (2) Delivery's mechanism statement answering what would be built first, what exists vs
must be built, where humans remain necessary — an honest negative counts as met; (3) the run
actually executed: a ledger row per post, at least one verdict-window draft citing a specific
baseline ledger row. Read the run as directional only at our audience size.

**90-day checkable behaviour (roughly the next two iterations):** if this is working we will see,
in files and on the account: at least one complete sense–observe–interpret–learn cycle where an
observed external response produced a change note citing a baseline, and the change measurably
altered the next output's handling; a catalogue that names at least one reachable group and
moves the buyer question from "who?" to "these people, here"; and a mechanism statement concrete
enough that Delivery can say what to build first. What we will **not** accept as success:
completed artifacts without external evidence (the iteration-1 failure mode), audience vanity
metrics, or a rubric-based judge quietly substituting for real-world response.

**Failure is legible too:** per the owner, one failed test is evidence. If external evidence
cannot be obtained, the scoped fallback learnings run (failure-mode diagnosis, mechanism
analysis, grounded catalogue, sharper next test) and the iteration closes with learning and a
redesigned test — a stop question only after accumulated evidence, brought to Dan by PM.

---

*Certified by Exec 2026-09-24 at Low-Medium confidence (problem: Low-Medium; mechanism: Low),
on partial inputs as stated above. Viability signal and what would change this decision:
`agents/exec/generates/entityR1-v2.md`.*