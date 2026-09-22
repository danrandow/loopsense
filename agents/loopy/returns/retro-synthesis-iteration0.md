---
name: retro-synthesis-iteration0
description: Loopy's cross-agent synthesis of the four lightweight iteration-0 retros, with proposed harness changes for Dan/PM
---

# Retro synthesis — iteration 0

All four agents (PM, Exec, Delivery, GTM) filed. Strong convergence — this reads like one finding from four angles, not four separate opinions.

## What worked (unanimous)
Every agent named the same thing: the SKILL.md "Session protocol" — fixed read order plus an explicit write boundary — removed the "am I allowed to touch this?" hesitation entirely. `team-registry.md`'s generates/ path convention made finding "the current X" mechanical rather than a search. PM also called out that keeping the *why* in the knowledge file's iteration log (not just the final entity) made later revisions easy to justify.

## What didn't (also converges, on one thing)
All four hit the same seam: the log-append mechanism.
- **Duplicate rule.** PM found `standing-rules.md` has two near-identical "7." blocks (the second adds PM-routing) — had to guess which was authoritative. I checked: this is real, not a misread.
- **No real append primitive.** PM and Delivery both note the rule assumes an exact-match line-level append tool; all any agent actually has is a shell, so append means read-whole-file, string-replace, rewrite — the exact operation the rule is trying to avoid, done carefully but unprovably.
- **Id-scan fragility.** Exec and Delilvery both want `id` mandatory on every entry (some recent entries, including mine, omitted it) so "next id" is a trusted read, not a manual scan.
- **Concurrency collision.** GTM's append actually failed mid-session — Exec appended id 123 between GTM's read and write, so GTM's computed id and `old_string` were both stale. One retry fixed it, but it's a guessable collision once more than one agent closes out the same day.

## Proposed harness changes (need Dan's approval — standing-rules.md is outside my free-write area)

1. **De-duplicate rule 7** in `knowledge/standing-rules.md` — delete the first (shorter) block, keep the second (has the PM-routing sentence). Pure cleanup, no behaviour change.
2. **Make `id` mandatory on every log entry**, including non-YAML writes where rule 6 currently says it's optional. Removes the "some entries have no id, ignore those" caveat and the manual scan it forces.
3. **Name the retry as the expected path, not a workaround.** Rule 6 already says "if the Edit fails, someone else appended: re-read, recompute, retry" — GTM did exactly this and it worked. I'd make this explicit as step 3's normal case (not an edge case) so agents don't treat a stale-match failure as something gone wrong.
4. Delivery's and GTM's sidecar/anchor ideas (a `lastid` file, or anchoring the match on a regex instead of a literal block) would still race under concurrent writers without a real lock, so I'd hold off on those unless collisions keep happening after (2) and (3) — cheap fixes first.

None of this touches the audit-trail model itself (append-only, never-Write, history record before change) — everyone found that sound. The friction is purely in id bookkeeping and one duplicated paragraph.

## Recommendation
Fix (1) and (2) now — both are small, low-risk, and would have prevented every friction point raised except the live-collision case, which (3) covers by documentation alone. Say the word and I'll follow rule 6/7 in full (history record, log first, targeted edit, read-back) for the standing-rules.md change itself.
