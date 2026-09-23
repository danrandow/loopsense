# LoopSense workflows

This directory contains runtime-neutral orchestration workflows that are part of LoopSense itself.

An agent harness can implement them with subagents, separate sessions, API calls, scheduled jobs or human-mediated handoffs. The mechanism may differ; the role boundaries, approval gates, file outputs, evidence discipline and stopping conditions must remain the same.

## Harness contract

To run the included workflows, a harness must be able to:

- give Loopy access to the LoopSense repository;
- invoke isolated PM, Exec, Delivery and GTM agents using their canonical `agents/<role>/SKILL.md` files;
- return each role's result to Loopy;
- run roles sequentially when they share one checkout;
- preserve each role's write boundary;
- perform ordinary Git status, pull, commit and push operations when the owner invokes a workflow that authorizes them;
- stop safely on dirty state, conflicts, missing authority or failed agents.

Runtime-specific setup belongs under that runtime's adapter directory, such as `openclaw/`. Canonical workflow behavior does not.

## Included workflows

- `retro.md` — collect role retrospectives and produce a cross-agent synthesis.
- `start-next-iteration.md` — obtain owner direction and approval, apply approved retro improvements, create the next iteration and run the forward pass.
