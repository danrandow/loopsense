# Visible sessions for substantive role interactions

## Context

Substantive LoopSense role interactions — iteration kickoffs, entity handoffs, review requests, retrospectives — were running as hidden subagent runs (including the iteration-2 PM kickoff). That leaves Dan no inspectable prompt and response in the Control UI, which undercuts the auditability the team runs on.

## Decision

Dan, 2026-09-24, effective immediately: every substantive interaction Loopy initiates with PM, Exec, Delivery or GTM must run in a visible persistent session for that named agent — clearly named (e.g. `Iteration 2 kickoff — PM`), grouped under the relevant iteration where supported, isolated context, with a self-contained prompt containing everything the receiving agent needs. Hidden subagents may be used only for disposable internal clerical work outside the LoopSense role-to-role process. Any role already invoked invisibly during the current iteration-2 startup gets a visible session repeating the substantive prompt; a hidden exchange is not an adequate visible record.

## Why

Dan must be able to inspect the complete prompt and response of every role interaction in the Control UI. Invisible runs break the chain of inspectable evidence between roles.

## Consequences

Each role interaction costs one persistent sidebar session and keeps its full transcript. The iteration-2 PM kickoff is repeated visibly. The wording change that makes this rule portable and durable (`agents/loopy/SKILL.md`, `workflows/start-next-iteration.md`, `workflows/retro.md`) is proposed separately and awaits owner approval.
