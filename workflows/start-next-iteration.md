# Start-next-iteration workflow

## Trigger and authority

When the owner tells Loopy **“start the next iteration”**, execute this workflow. Preserve any direction included in the same message rather than asking the owner to repeat it.

The trigger authorizes Loopy to prepare a proposal and ask one combined decision question. It does not itself approve file changes. File-writing authority begins only after the owner approves the specific proposal, including any revisions made during the conversation.

This workflow has two phases separated by a mandatory owner checkpoint.

## Phase A — prepare the decision

### 1. Establish current state

1. Follow Loopy's normal startup protocol and read this workflow completely.
2. Identify the highest-numbered `iteration-M.yaml`; the proposed next iteration is `N = M + 1`.
3. Read the completed retro synthesis for iteration `M`, all four underlying retros, the current iteration file, and the latest PM, Exec, Delivery and GTM outputs.
4. Reconcile current files against historical recommendations. Do not propose a fix that is already present.
5. Keep workflow completion, experiment execution, hypothesis outcome and formal closure distinct. Carry incomplete work as incomplete; never silently promote it to done.
6. Capture any direction supplied in the trigger message. If none was supplied, show that clearly in the proposal instead of asking a separate preliminary question.

If the latest iteration has no completed retro synthesis, stop and ask the owner to run the retro first. Do not infer recommendations from an incomplete retro.

### 2. Read-only repository preflight

1. Confirm the current Git branch has an upstream and `git status --short` is clean.
2. Fetch the upstream and run `git pull --ff-only`.
3. If the tree is dirty, the pull cannot fast-forward, or authentication fails, stop and report. Do not stash, discard, merge, rebase, reset, commit or force anything.

### 3. Present one approval checkpoint

Present a compact proposal with:

1. **Owner direction** — quote or closely paraphrase what was supplied; if absent, show “Not supplied yet”.
2. **Retro improvements proposed** — each specific change, why it is justified, and every file it would modify. Separate convergent findings from Loopy's interpretation.
3. **Carry-forward state** — unfinished work, unrun experiments and unresolved decisions from iteration `M`.
4. **Proposed iteration-`N` intent** — a plain-language outcome for PM to turn into the testable scenario; do not write PM's bet for it.
5. **Execution sequence** — approved harness changes, iteration skeleton, PM, Exec, Delivery, GTM.

Ask one combined question: provide or amend the direction, approve/reject/edit each proposed harness change, and approve starting iteration `N` on that basis.

Then stop and wait. Do not write files, create the iteration or invoke another role before approval.

If the owner changes the proposal materially without clearly approving the revised version, summarize the revised plan and request approval once more. A clear “yes”, “approved”, “go ahead”, or equivalent applies to the latest specific plan shown.

## Phase B — execute the approved plan

### 4. Recheck and apply approved improvements

1. Repeat the clean-tree and fast-forward preflight immediately after approval.
2. Apply only the file changes explicitly approved by the owner. Loopy may edit files outside its normal free-write area only because this conversation contains that specific approval.
3. Follow `knowledge/standing-rules.md` and `knowledge/audit-policy.md`: targeted edits, read-back, one coherent commit per change batch.
4. Do not implement rejected, deferred or newly inferred changes.
5. Validate what changed (`git diff --check`, JSON/YAML read-back, standing rule 8 for public material) and inspect `git status --short`.
6. Stage exact approved paths only. Commit as `harness: apply iteration N retro improvements` and push normally to the configured upstream. Never force-push.

If no harness changes were approved, skip this commit.

### 5. Create the iteration skeleton

1. Confirm `iteration-N.yaml` does not exist. If it does, stop and ask whether to resume it; do not overwrite it.
2. Create a minimal scenario file that inherits `base.yaml`, identifies iteration `N`, records the approved direction, carries forward incomplete items explicitly, and marks its scenario as provisional for PM synthesis.
3. Do not claim the prior experiment ran or hypothesis succeeded unless current evidence says so.
4. Follow `knowledge/audit-policy.md` for commit and sync.
5. Read back and validate the file. Note that the renderer has not been checked.
6. Stage the exact iteration file. Commit as `iteration N: create approved skeleton`, pull from the upstream with `--ff-only`, then push normally.

### 6. Run the forward pass sequentially

Use the harness's role-invocation mechanism to run `pm`, `exec`, `delivery`, then `gtm`. Each invocation must load that role's canonical skill in an isolated agent/session context. Never run two writing roles concurrently in one checkout.

Before each role, require a clean tree and pull from the upstream with `--ff-only`. Stop on failure.

Send the role its canonical trigger, `start iteration N`, plus the approved direction and a pointer to the retro synthesis. Require its canonical read order, write boundary and handoff rules. Do not prescribe the role's substantive conclusion.

After each role:

1. Inspect its report and `git status --short`.
2. Verify that every changed path is within that role's boundary or its permitted entries in `iteration-N.yaml`.
3. Read back outputs, validate JSON/YAML where relevant, run `git diff --check`, and apply standing rule 8 where relevant.
4. Stage exact paths only; never use `git add -A` or `git add .`.
5. Commit as `iteration N: PM kickoff`, `iteration N: Exec review`, `iteration N: Delivery pass`, or `iteration N: GTM pass`.
6. Pull from the upstream with `--ff-only`, then push normally. Never force-push, merge or rebase automatically.

Respect canonical outcomes:

- If PM decides stop or pivot, preserve and push its valid output, then stop and report.
- If Exec returns the bet, preserve and push its return, then stop. Do not invoke Delivery.
- If Delivery reports missing certified input or an upstream blocker, preserve and push valid output, then stop. Do not invoke GTM.
- If GTM is barred from an external action, it may still produce listening returns or pre-release drafts allowed by its canonical rules. Do not waive publishing gates or infer account authority.
- If a role fails, retry the same bounded task once. If it fails again, do not impersonate it or skip ahead; stop and report.

### 7. Failure and concurrency safety

If a commit or push fails, preserve the working tree and report the failure and `git status --short`. If the upstream advances and a pull cannot fast-forward, stop for the owner. Never delete, reset, overwrite, force-push, merge or rebase automatically.

## Final report

Report the iteration number and approved direction; retro improvements applied or deferred; each role's outcome and output paths; where the pass stopped; remaining unrun experiments and unresolved decisions; commit hashes and push status; and any renderer or external-action checks still requiring the owner.
