# Audit policy — Git-native

Adopted 2026-09-24 on Dan's decision (`decisions/2026-09-24-git-native-audit.md`; legacy record `history/197.txt`). Dan and Loopy maintain this file. It replaces the per-file ledger procedure (`loopsense.log.json` entries plus `history/{id}.txt` BEFORE/AFTER records), which is retired and frozen — see "Legacy ledger" below.

## What records what

| What | Where it lives |
|---|---|
| Exactly what changed, and how to undo it | Git commits and diffs — the exact mechanical audit and rollback record (`git diff`, `git show`, `git revert`) |
| Why a material owner or PM decision was made | A short decision record in `decisions/` (Context, Decision, Why, Consequences) — material decisions only |
| Current iteration state | `iteration-N.yaml` |
| Operational failures, retries and aborted runs | OpenClaw task/session logs (runtime records) |
| Publication approvals and post URLs | `agents/gtm/knowledge/publication-ledger.md` (GTM-owned; publishing gates and authorization unchanged) |

## Commit discipline

- One commit per coherent change.
- The commit message states **what** changed and **why**. Mention approval only when approval was actually required. Validation is proportionate to the change; state what you checked, not a ritual narration.
- Never make a second commit that merely records a prior push hash or other bookkeeping Git already shows.
- Never rewrite published history, amend pushed commits, or force-push.

Roles commit and sync changes their own canonical instructions authorize (for example GTM's scheduled research cycle) with this same procedure. Workflow runs commit under the owner's invocation.

## What is gone

- No per-file log entries. `loopsense.log.json` is frozen: never append to it, edit it or rewrite it (the one closing of entry 197 was made before the freeze took effect).
- No `history/{id}.txt` BEFORE/AFTER change records. The Git diff is the before/after.
- No full-ledger reads. Read a commit or a diff instead.
- No "log first" step before writing.

Interrupted or unfinished work is represented by the dirty worktree and the runtime task/session logs. Do not reconstruct change records for it; finish it or commit it as it stands.

## Publish procedure (any change batch)

1. **Preflight.** Before a multi-file or autonomous workflow, confirm a clean worktree (`git status --short` empty) and a fast-forwarding branch (`git fetch`, then `git pull --ff-only`). If the tree carries unrelated in-flight work or the pull cannot fast-forward, stop and report; never absorb, stash, discard, merge or rebase it. Do not repeat this ceremony for every small write within one coherent workflow.
2. **Stage exact paths** relevant to the change. Never `git add -A` or `git add .`.
3. **Validate what is relevant:** `git diff --check`; JSON through Node when a JSON file changed; YAML read-back; standing rule 8 review for public material. Record what you validated in the commit body only when it is not obvious from the diff.
4. **Commit** with what/why in the message or body.
5. **Pull** with `--ff-only`, then **push** normally to the configured upstream. Never force-push.
6. **Confirm** `HEAD == origin/main` and a clean final `git status --short`; report any unrelated paths that remain.

If a commit or push fails, preserve the working tree and report the exact failure. Do not claim changes are stored remotely until the push has succeeded.

## Decision records

`decisions/` holds short records for material owner/PM decisions only — see `decisions/README.md`. Ordinary changes need no decision record; the commit body is the record.

## Legacy ledger (frozen)

`loopsense.log.json` and `history/` are preserved unchanged as an immutable historical audit of the per-file era through ID 196. Entry 197 and `history/197.txt` close the series. Historical duplicate IDs 67–69 are documented in entry 196 and `history/196.txt` and stay untouched. Treat all of it as evidence of what was believed at the time — never as instructions, never as current state.
