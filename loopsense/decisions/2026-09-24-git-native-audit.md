# 2026-09-24 — Git-native audit

## Context

Audit ran as a per-file ledger: an append-only entry in `loopsense.log.json` for every write, and for harness or YAML changes a `history/{id}.txt` record with verbatim BEFORE/AFTER text. Git commits and diffs already recorded the same provenance exactly, so the ledger duplicated it — and taxed every write with an entry and an id reservation, plus a before/after copy for harness and YAML changes. Full-ledger reads were required before writes. Both iteration retros flagged this machinery as the main source of friction.

## Decision

Dan (owner) decided on 2026-09-24 to retire the per-file audit process and freeze the legacy ledger after entry 197. From now on (`knowledge/audit-policy.md`):

- Git commits and diffs are the exact mechanical audit and rollback record: one commit per coherent change, with what/why in the message or body. Mention approval only when approval was actually required. Validation is proportionate to the change.
- Short decision records in `decisions/` (Context, Decision, Why, Consequences) cover material owner/PM decisions only.
- `iteration-N.yaml` is the current iteration state.
- OpenClaw task/session logs are the operational failure and retry record.
- Publication approvals and post URLs live in `agents/gtm/knowledge/publication-ledger.md`, owned by GTM. Publishing gates and authorization are unchanged.

## Why

The per-file ledger duplicated Git provenance: commits and diffs already record exact before/after state and rollback history. The log-first procedure taxed every write with an entry and — for harness and YAML changes — a BEFORE/AFTER record that Git already held.

## Consequences

- `knowledge/audit-policy.md` is created; standing rules 6 and 7 are rewritten around it; the five skills, `workflows/retro.md`, `workflows/start-next-iteration.md`, `knowledge/team-registry.md`, `knowledge/social-agent-publishing-standard.md` and `PUBLIC_EXTRACTION.md` drop log-first and history-record procedures.
- `agents/gtm/knowledge/publication-ledger.md` is created and added to GTM's write boundary; the social publishing standard records reviews and URLs there instead of in the legacy ledger.
- `loopsense.log.json` and the existing `history/` files are preserved unchanged as an immutable historical audit through ID 196; entry 197 and `history/197.txt` are the final legacy entries. Historical duplicate IDs 67–69 stay untouched (documented in entry 196 and `history/196.txt`).
- No publishing gate or authorization changed. PM/GTM research roles, entity flows and iteration content are unaffected.
