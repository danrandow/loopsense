# Retrospective workflow

## Trigger

When the owner tells Loopy **"run the retro"**, execute this workflow for the highest-numbered `iteration-N.yaml`. The phrase authorizes the retrospective and the bounded Git operations described here. It does not authorize implementing recommendations or changing skills, standing rules, topology, iteration YAML, publishing state or other harness files.

The trigger means the current iteration is entering closing review as it stands. Record unfinished work and unrun experiments as unfinished or unrun. Never convert a filed workflow return into evidence that an experiment ran, a hypothesis succeeded, or an iteration was already formally closed.

## 1. Establish scope

1. Follow Loopy's normal startup protocol and read this workflow completely.
2. Identify the highest-numbered `iteration-N.yaml`; call that number `N`.
3. Read the current iteration file and current outputs from PM, Exec, Delivery and GTM.
4. Establish which workflows completed, which experiments ran, what the evidence says, and whether formal closure was recorded. Preserve these distinctions in the synthesis.
5. If no iteration file exists, stop and tell the owner. Do not invent an iteration number.

## 2. Repository preflight

From the repository root:

1. Confirm the current Git branch has an upstream.
2. Run `git status --short`. If the tree is not clean, stop and report the changed paths. Do not stash, discard, commit or absorb pre-existing work.
3. Fetch the upstream and run `git pull --ff-only`. If either fails or a fast-forward is impossible, stop and report. Do not merge, rebase, reset or force anything.

## 3. Invoke roles sequentially

Use the harness's role-invocation mechanism to run `pm`, `exec`, `delivery`, then `gtm`. Each invocation must load that role's canonical skill and run in its own agent/session context. Each role runs in its own visible persistent session (label `Iteration N retro — <role>`, group `Iteration N`) with the complete prompt and response preserved; hidden subagent runs are not acceptable for these. Wait for one to finish before starting the next.

Send each role this task, substituting its ID and `N`:

> Iteration N is entering its retrospective at the owner's instruction. Reflect on your own experience working in the harness, not on the quality of your output. Read your canonical instructions and current iteration evidence first. In no more than half a page, answer: (1) What worked? (2) What did not work—where did you guess, stall, wait, or work around a gap? (3) What one harness change would help most next iteration? Do not let Loopy's prior diagnosis lead your answer. Keep workflow completion, experiment execution, hypothesis outcome and formal closure distinct. Write only `agents/AGENT-ID/generates/retro-iterationN.md` within your canonical boundary. Do not edit skills, rules, YAML or another agent's files. Report the path written and confirm read-back.

After each result:

1. Verify that the expected file exists and is no more than approximately half a page.
2. Verify that it describes that role's own experience and does not falsely mark an unrun experiment as run.
3. If invocation fails, retry once with the same bounded task. If it fails again, do not write on that role's behalf; record the missing retro and continue collecting the others.

## 4. Synthesize

After all four attempts:

1. Read every retro that exists.
2. Write `agents/loopy/returns/retro-synthesis-iterationN.md`.
3. Separate findings independently raised by multiple roles, role-specific findings, Loopy's interpretation, and proposed changes requiring owner approval.
4. List any missing retro explicitly. Do not infer that silence means agreement.
5. Do not implement recommendations during this workflow.

## 5. Validate and publish repository changes

1. Read back all new retro and synthesis files.
2. Run `git diff --check`.
3. Scan changed files for credentials, private contact details and accidental runtime state.
4. Review `git status --short`. Only expected retro files may be included.
5. Stage those exact paths; never use `git add -A` or `git add .`.
6. Commit with `retro: complete iteration N retrospective`. If retros remain missing after retry, use `retro: save partial iteration N retrospective`.
7. Pull from the configured upstream with `--ff-only` immediately before pushing. If it cannot fast-forward, stop and report; do not rebase or merge automatically.
8. Push normally to the configured upstream. Never force-push.

If commit or push fails, preserve the working tree and report the exact failure and `git status --short`. Do not claim the changes are safely stored remotely until the push succeeds.

## 6. Report

Return the iteration number; four retro paths and whether each succeeded; synthesis path; strongest convergent finding; decisions requiring the owner; commit hash and push status; and anything incomplete or needing recovery.
