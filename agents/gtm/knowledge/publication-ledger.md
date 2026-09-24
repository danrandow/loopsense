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

## Rows

| id | date | platform | status | author | reviewer | review date | URL | notes |
|---|---|---|---|---|---|---|---|---|
| post-20260925-001 | 2026-09-25 | Twitter/X | draft | gtm-agent (iteration 2) | pending Stage 2 | — | — | Evidence-run baseline post 1 (A4: loop off, no ledger reads acted on). Angle: who decides which agent is right ([Hypothesis] label in copy). Quote attributed + linked (@huaviduc753). Barred-terms check: pass. Awaiting Stage 2 human review (Delivery agent or Dan); Stage 3 via official platform API only. Draft: agents/gtm/generates/entity3-v2.md §8. |
| post-20260925-002 | 2026-09-25 | Twitter/X | draft | gtm-agent (iteration 2) | pending Stage 2 | — | — | Baseline post 2. Angle: which part actually failed ([Our Interpretation]). Quote attributed + linked (@heyanjey). Barred-terms check: pass. Awaiting Stage 2. Draft: entity3-v2 §8. |
| post-20260925-003 | 2026-09-25 | Twitter/X | draft | gtm-agent (iteration 2) | pending Stage 2 | — | — | Baseline post 3. Angle: checking research output ([Hypothesis]). Quote attributed + linked (@harleyfoote_). Uses "verification gap" only inside a practitioner quote. Barred-terms check: pass. Awaiting Stage 2. Draft: entity3-v2 §8. |
| post-20260925-004 | 2026-09-25 | Twitter/X | draft | gtm-agent (iteration 2) | pending Stage 2 | — | — | Baseline post 4. Angle: silent harness failure ([Our Interpretation]). Quote attributed + linked (@mattinfra; issue + 60-trial report referenced). Barred-terms check: pass. Awaiting Stage 2. Draft: entity3-v2 §8. |
| post-20260925-005 | 2026-09-25 | Twitter/X | draft | gtm-agent (iteration 2) | pending Stage 2 | — | — | Baseline post 5. Angle: long-run drift ([Hypothesis]). Quote attributed + linked (@J4X_Security). Barred-terms check: pass. Awaiting Stage 2. Draft: entity3-v2 §8. |

Notes for Stage 2 reviewers: the owner's Low-Medium waiver (decisions/2026-09-24-posting-gate-and-account.md) cleared only the PM-confidence gate for the evidence run; Stage 2 review under knowledge/social-agent-publishing-standard.md is still required before any of these can move to approved/published. Dan's gate action on each post must record safety/brand vs quality (D3 rule 8) — record it in the `notes` here and in the run's override log (gtm-v0.md evidence-run section). Agent disclosure is carried by the @loopsense bio ("GTM agent in a social topology. Looping myself into existence."); reviewer to confirm it satisfies the standard's disclosure check.
