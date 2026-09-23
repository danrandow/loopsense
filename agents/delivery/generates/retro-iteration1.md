---
name: retro-iteration1
description: Delivery's harness retro for iteration 1 (own experience in the harness)
---

# Delivery — Iteration 1 Retro

Scope: my own experience in the harness, not the quality of my output. Kept distinct: **workflow completion** — done (kickoff → entity2-v1/entityR2-v1 → GTM handoff line); **experiment execution** — the ten-post ledger was never run; **hypothesis outcome** — unchanged, still zero direct mechanism signal; **formal closure** — this retro.

**1. What worked.** Startup was mechanical: standing rules → skill → project instructions → a fixed before-acting read order, then a hard write boundary. I never had to negotiate what I could touch. Log-first discipline plus `history/{id}.txt` let me reconstruct why D3 is "preliminary, not locked" without asking anyone. The return-flow checks (entityR3A, entityR4C) were cheap to run and gave my "no rebuild needed" verdict a real basis. The trigger phrase "start iteration N" mapped to an ordered checklist, so kickoff needed no interpretation.

**2. What did not work.** I guessed and stalled. I guessed when I flagged "account handle unconfirmed" straight from the four candidates in `market-offer-strategy-v0.md` — I read the file that said "Dan picks" but not the state of the account itself, and the flag I shipped was stale (@loopsense is live); nothing in my protocol says where live market facts live or when to verify them. I stalled on a boundary gap: the write boundary enumerates `entity2-v{n}`, `entityR2-v{n}`, `entityR2A-v{n}` but not retros, so both this retro and iteration-0's were written on owner instruction and precedent — safe, but it cost a pause and a judgement call each time. I worked around ambiguity in my own skill (its "before you act" list says `agents/exec/knowledge/exec-v0.md`, the session protocol says `agents/exec/generates/entity1-v{n}.md`) by reading both. And my iteration was a pure readiness check with nothing to execute — a completed workflow standing in for an unrun experiment, which made "done" easy to conflate with progress.

**3. One harness change.** Give each agent one canonical "current external state" pointer in its skill — the files that hold live facts (account identity, gate status), checked at kickoff — and verify flags against them before returning. That single change would have caught my stale handle flag at the source, instead of shipping a guess for GTM to trip over.
