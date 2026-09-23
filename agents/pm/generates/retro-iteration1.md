# PM retro — iteration 1 (harness experience)

Scope: my own experience working in the harness, not the quality of my output. Status, kept
distinct: **workflow** — completed (kickoff → Exec → Delivery → GTM → return to me);
**experiment** — the ten-post loop was never executed; **hypothesis outcome** — unchanged, zero
direct evidence for the mechanism; **formal closure** — this retro.

## 1. What worked

The session protocol left no ambiguity — fixed read order, strict write boundary, log discipline;
I always knew what to read and what I could touch. The starting question forced a real
continue/pivot/stop decision instead of drift. Exec's returned questions made the bet answerable
point by point; the return flows carried signal I could actually use.

## 2. What did not work

My biggest failure was a guess: I set the evidence threshold ("run the ten-post loop") without
checking it against GTM's posting gate (Medium confidence). My ask and that gate contradicted
each other; GTM burned a cycle discovering it, and nothing in my protocol made me check
executability before handoff. Then the iteration stalled waiting: two decisions only Dan could
make (gate waiver, account handle) had no single recorded home, so all three of us re-flagged
them independently — and the handle flag I carried into entity0-v1 was already stale (@loopsense
is live). The log-append mechanism Loopy's synthesis named cost me ceremony but caused no guesses
or stalls; my friction was upstream of it. Smaller gap: retros are not enumerated in my write
boundary; I proceed on your instruction and iteration-0 precedent.

## 3. One harness change

Gate-check the evidence threshold before handoff: every required action must clear the
downstream agent's gates, and any gate that must yield becomes one dated decision request to Dan
in a single register — while it is open, the loop pauses instead of spinning another empty cycle.
