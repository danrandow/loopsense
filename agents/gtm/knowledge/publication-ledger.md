# GTM publication ledger

Owner: GTM. Referenced by `knowledge/social-agent-publishing-standard.md`. This file records the outcomes of that standard's review and publication stages — it does not change them. Publishing still requires the human review, gates and authorization the standard sets out.

## What is recorded here

- Every human review result for a candidate post: approved / revise / rejected, with reviewer, date and reasoning.
- The URL of every published post, with platform, author and review date.

This replaces the old `loopsense.log.json` audit entries for publications. The legacy ledger is frozen (`knowledge/audit-policy.md`) — never record publications there.

## Format

One row per decision or post:

| id | date | platform | status | author | reviewer | review date | URL | notes |
|---|---|---|---|---|---|---|---|---|

- `id`: stable post id (`post-YYYYMMDD-nnn`)
- `status`: `draft` / `approved` / `revise` / `rejected` / `published`
- `notes`: reviewer reasoning and, where needed, the claim certainty labels ([Verified], [Hypothesis], …) with their sources

## Rules

- Record the review result before publishing; record the URL immediately after publishing.
- The ledger is a record, not authority: gates and human review stay exactly as the standard requires.
- Changes to this file are ordinary GTM writes inside GTM's boundary, committed per `knowledge/audit-policy.md`.
