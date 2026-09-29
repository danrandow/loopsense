---
name: retro-iteration0
description: PM's harness retro for iteration 0, per retro-prompt-lightweight-v1.md
---

# PM retro — iteration 0

**What worked:** The SKILL.md session protocol (fixed read order, explicit write boundary) made picking up mid-iteration fast and low-risk — I never had to guess what I was and wasn't allowed to touch. `knowledge/team-registry.md` + the `generates/{entityId}-v{n}.md` naming convention meant finding "the current GTM signal" or "the current bet" was mechanical, not a search problem. Keeping the bet's evidence and reasoning in `pm.md`'s iteration log (separate from the bet document itself) made the 2026-09-19 and 2026-09-21 revisions easy to justify later, because the *why* was written down at the moment of the change, not reconstructed after.

**What didn't:** Standing rule 7 is duplicated verbatim in `knowledge/standing-rules.md` (two near-identical numbered "7."s, the second one adding the PM-routing sentence) — I read both and had to decide which was authoritative rather than being told. Appending to `loopsense.log.json` also has no exact-match edit tool available in this environment the way the rule assumes ("use Edit, never Write, never rewrite the file"); the only tool I have is a shell, so an append means reading, parsing, and rewriting the whole JSON file, which is exactly the operation the rule is trying to rule out. I did it as carefully as I could (append-only, no reordering, re-validated after), but there's no way for me to prove I didn't touch earlier entries other than a diff Dan would have to run himself.

**One change:** Either relax rule 6/7's "never rewrite, use Edit" language to say what's actually enforceable from a pure-shell agent (e.g. "append via a script that only ever adds to the end and is diffed against the prior file before confirming"), or give agents a real line-level append primitive for the log so the rule matches the tooling. Separately, de-duplicate the two rule-7 blocks in `standing-rules.md` — cheap fix, currently a small trust tax every session.
