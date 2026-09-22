---
name: entityR2-v0
description: Delivery reality, iteration 0. What was built, what it took, what would run long, and feasibility confidence for the current bet. Return flow from Delivery to PM.
entity: entityR2
direction: return
from: actor2 (Delivery)
to: actor0 (PM)
iteration: 0
status: open
last_updated: 2026-09-21
sources:
  - cowork
---

# entityR2: Delivery Reality (iteration 0)

Basis: `entity1-v0` (Exec brief), `entity0-v0`, `entityR3-v0`, and the harness files. No entityR3A or entityR4C has arrived, so nothing here comes from practitioners.

## What was built

`agents/delivery/generates/entity2-v0.md`, in six parts, finalised for iteration 0 and ready for GTM:

- **D1, start-here page (Part 1).** One-sentence version first, the problem in practitioner phrases, the idea, the moving parts, a worked example, five concrete steps to run one iteration, and a tested / not tested table. About 830 words, so within the two-page limit.
- **D2, content-loop spec (Part 2).** The @loopsense loop (draft, Dan's publish gate, post, read, ledger row, next change note), the signal ledger fields, proposed metric weights, and stop rules.

- **Design rationale (Part 3).** Eighteen design choices with the reason and where it is recorded, taken from `history/`, the log, the standing rules and `dna.md`. Reasons that were never written down are marked as inferred.
- **FAQ (Part 5) and handover notes for GTM (Part 6).** The notes list claims safe to use, claims not to use yet (Navier-Stokes, 17.2x, "solves", "manufactured referee", `landing-page-v0.mdx`), the gates, and where the ledger should live.
- **D3, verdict rule (Part 4), preliminary and not locked.** Written on stated Delivery assumptions, because Dan says no more PM input will arrive this iteration. It follows the Exec's rule (baseline of 5, verdict window posts 6 to 10) and adds a reporting rule and a fallback if there is no ICP-fit response.

## Not done, by choice

- No cold read by someone outside the team. The acceptance test (say it back in one sentence) is checked only by me. GTM is the first reader.
- The template files (clean `base.yaml`, SKILL.md and knowledge-file templates) and a standalone README and implementation guide. Dan asked to keep them in scope for later; Part 1 covers the essentials in the meantime.

## What it took

- One working session. The cost was mostly reading: the brief, the GTM cycles, and `base.yaml`.
- **Surprise 1:** the map already carries the content loop with no new elements. The post is entity3, the response is entity4, and the raw response reaching the drafter is entityR4B. What is missing is the return edge itself, which is a file convention (GTM appends to its knowledge file and cites ledger rows in the next draft), not something the map enforces.
- **Surprise 2:** `delivery-v0.md` listed file paths that no longer exist (`skills/...`); corrected.
- Constraint from the brief: no code runner, so the ledger is filled by hand by GTM. That is workable for ten posts and would not survive a hundred.

## What is genuinely unique about the approach

Only the combination: a diffable YAML topology, an explicit return edge, and a ledger where every change the drafter makes has to cite a row. The last part is what makes "did the loop change its behaviour" checkable by someone who was not in the room. None of the three is new alone.

## What would take longer than the opportunity window

- Any test with a real outside practitioner: none is reachable yet (R3: zero ICP matches located and reachable).
- Automating the signal pull. Manual reads are fine for n=10.
- Enough posts for a result that is more than directional.

## Assumptions D3 rests on (PM answers will not arrive this iteration)

1. "Verified without a human" means the verdict comes from ledger rows, not anyone's opinion of quality (R1 Q3).
2. Five posts against five is a direction only (R1 Q4).
3. Observed change means a change note citing ledger rows that shows up in the next draft (R1 Q6).
4. My reading of the brief: baseline posts are drafted without acting on ledger reads, changes begin at post 6. Not confirmed; open to change. Dan says D3 and the weights are preliminary and not locked.

These are for Dan and Loopy to keep or change at the retro.

## Flags

- `entity0-v0` footer is stale (entityR3 is filed; cycles run to 2026-09-21). Already raised by Exec.
- `iteration-0.yaml` title and header notes still say "manufactured referee" and name Dan as referee. Dan and Loopy own that.
- Actor2's label in `iteration-0.yaml` still reads "Delivery Agent — Not Yet Active". Not mine to edit; flagged for Dan and Loopy.
- Standing rule 7: history and the log are my source for documenting the design. The rationale is now in Part 3. Reasons for the early folder and naming choices were not recorded; that is a retro question.
- No escalation to Exec this iteration (no entityR2A).

## Feasibility confidence for the current bet

- **Shipping the documents (D1 to D3):** high. All three are drafted.
- **Running the loop by hand for ten posts:** medium. It depends on Dan approving drafts, and on GTM being able to read platform numbers at 24h and 72h.
- **The loop producing usable signal:** not mine to judge. Low, as Exec says, until a first ledger exists.
