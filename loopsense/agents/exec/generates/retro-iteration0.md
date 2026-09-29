# Exec — Iteration 0 Retro

**1. What worked.** The write-boundary in SKILL.md was unambiguous — I never had to guess where a file belonged, and reading `team-registry.md` + `reading-the-map.md` up front meant I could locate Delivery's and GTM's latest generates without asking. The log's `note` field with explicit Was/Now text also made it easy to trust the audit trail without re-deriving intent from diffs.

**2. What didn't.** Rule 6's id-selection step ("highest id in the log, ignoring entries with no id") only works if every entry that matters is consistently id'd — several recent entries (loopy's, an earlier PM retro) omitted `id` even though later entries used one, which meant I had to read the log tail by hand to confirm the next free id and history path rather than trust a single field. I also didn't have a clean signal for when GTM's/Delivery's inputs were "final for this iteration" vs. still in flux — I read whatever version existed at session start with no freshness marker.

**3. One harness change.** Make `id` mandatory on every log entry (even non-YAML ones), assigned sequentially at write time — that turns "find the highest id" from a scan-and-verify step into a single trusted read, and removes the collision risk between an entry's own id and a `record` path someone else already used.
