# Handover: Robot Race reset (written 2026-10-12)

Read AGENTS.md too (Randow Maps rules). This file is the brief for the autonomous Claude Code session.

## Mandate
Dan has spent ~5 days and has not seen an agent team learn. You own the work end to end: run races/experiments, read results, diagnose, fix mechanics, rerun. Do NOT ask Dan to run anything or relay results. Ask only at the gates and stop conditions below.

## Question being answered (in order; do not skip ahead)
1. Can ONE LLM agent improve a robot design from feedback in this simulator, beyond a free non-LLM search / random hill-climb baseline?
2. Only if yes: does the LoopSense (randow-maps) team beat opt-eval, over many replicates?

## Evidence so far (see robotrace/docs/SIMULATOR_REVIEW_AND_DESIGN_APPROACH.md, robotrace/scratch/k4_haiku.txt, robotrace/races/race-40-replicates.md)
- tools/baseline_search.py (no tokens, ~129 s) reaches 100% finish on all six tracks. Sensor layout is the decisive lever.
- Haiku 5.5 K=4 hill-climb (+130) is about equal to random best-of-4 (+111). Sonnet 5.5 was no better than Haiku in small probes. Model strength is NOT shown to be the constraint.
- Race agents get ~6-12 iterations of summarised feedback and cannot run the simulator; the search used ~400 evaluations.
- Race 40 (n=3): neither team learns. Sim/tracks changed twice since, so old scores are not comparable. Race 104 died on a read timeout.

## Plan
Phase 0 (calibrate, no LLM): freeze simulator, tracks, scoring, seeds (record a version hash). Write the pass criterion BEFORE running (e.g. dev score at last iteration beats iteration 0 in >=8 of 10 paired-seed replicates). Run baseline_search and random hill-climb with several seeds to get ceiling and noise. Resolve max_steps 300 vs 1200 (experiment.yaml vs race.yaml).
Phase 1 (single agent, Haiku 5.5 via OpenRouter): give the agent the simulator as a tool with ~400-evaluation budget; compare with the current 6-12 iteration summary-feedback loop. If Haiku with sim access matches the search, the earlier failures were access, not intelligence. If not, try Sonnet 5.5 on the identical setup.
Phase 2 (only after a Phase 1 pass): topology comparison, >=8 replicates per team, same frozen setup, non-LLM search reported as the reference line in every result.

## Gates (stop and report to Dan with a results table + recommendation)
G1 Phase 0 done. G2 Phase 1 result. G3 before any Phase 2 spend.
Also stop for: budget exhaustion; anything that changes what agents see or how scoring works after the freeze; anything irreversible.

## Charter (Dan's validity rules; do not break)
- Agents are told constraints accurately (limits, mechanics, how to steer) but never design advice or findings from your own probing. They must learn to build themselves. Suspected simulator bugs: do not fix unless sure, and then as a PR on the simulator repo.
- Prompts say what to achieve, not how. Agent prompts live in the topology (each action's notes). Same common prompt for all agents; only team/agent-specific exceptions split out.
- Harness must be resilient: out-of-range values or rejected output must not abort a race; they are fed back as feedback. No fiddly retry/prompt micromanagement.
- Both teams get identical information and budgets. "Orchestrator" = harness; "controller" = the robot's control part.
- Race failures are diagnosed as team-design/incentive problems first, harness mechanics second.
- Mechanics fixes (timeouts, retries, accounting, crashes) you may make without asking; log each in robotrace/CHANGELOG-autonomous.md.

## Budget and ops
- OpenRouter key is in env OPENROUTER_API_KEY (never write it to a file, log or commit). A 12-iteration race with Haiku 5.5 measured at $0.089-0.116 (races 105/106 opt-eval, race 107 randow-maps, 2026-10-14) -- the old "~$0.30" figure was a safe overestimate, not wrong in direction; corrected here from measured OpenRouter balance drops, not from published pricing. Observed rate ~$0.11-0.13 per million tokens charged on the per-call `usage.cost` figure.
- **2026-10-15 (Gate 9): the $4.00 hard-floor rule is removed, per Dan.** Replacement rule for any future paid work: keep a **$0.50 reserve against in-flight requests** -- stop issuing new calls when the balance is within $0.50 of zero. Dashboard balance confirmed $3.34 at the time of this change.
- **Root cause found (Gate 10) for the "dashboard reads ~$1.05-1.08 higher than the API" pattern seen since Gate 6: wrong endpoint.** `/api/v1/auth/key`'s `limit`/`limit_remaining` tracks a $20 per-key budget -- a different, smaller scope than the account's real $40 credit pool the dashboard shows. `/api/v1/credits` (`total_credits - total_usage`) matched the dashboard to within $0.06 when checked side by side. **Use `/credits`, not `/auth/key`, for every future balance/reserve check.** This does not fully explain Gate 9's specific $0.877-vs-$1.392 per-call-cost gap (no root cause found there either, after checking in-flight/retried/unrecorded calls via OpenRouter's `/generation` endpoint for every logged request_id -- see `robotrace/GATE10_REPORT.md`); treat per-call `cost_usd` sums as a lower bound until that is resolved, and check `/credits` directly (not a per-call sum) before authorizing each new wave of concurrent races.
- **Gate 11: `/credits` lags, sometimes by 10+ minutes.** Checked before/after each of two race waves (~11 min total) and it read the exact same figure all four times despite ~$0.71 of confirmed real spend. It's the right endpoint for an absolute balance (matches dashboard), but is not a working real-time in-flight guard. Use the per-race cost cap (from that race's own live events) as the real-time guard; treat `/credits` as a slow-settling sanity check only.
- **Gate 12: `/credits` and `/auth/key` answer two different questions, and a paid run needs both.** `/credits` (`total_credits - total_usage`) is real money -- how much the account actually has left. `/auth/key`'s `limit_remaining` is a separate, provisioned per-key spending cap; OpenRouter returns HTTP 403 and rejects every call once it hits zero, *regardless* of how much real balance `/credits` still shows (confirmed directly: a Gate 12 run died with `/credits` at $0.66 real balance remaining but `limit_remaining` at $0). **Report both numbers on every balance check from now on, and stop any paid step on whichever of the two is smaller** -- `/credits` tells you if you're really out of money; `limit_remaining` tells you if the next call will be rejected even though you aren't. Values as of 2026-10-19 (both raised by Dan since Gate 12): `/credits` remaining $10.4667 (`total_credits` 50, `total_usage` 39.5333); `/auth/key` `limit_remaining` $19.4186 (`limit` 40, `spend_usd` 20.5814).
- There are uncommitted changes in robotrace/orchestrator/*, validators, race.yaml templates and tests/test_history.py: review them first and run the test suite before building on them. Commit your work on a branch, not main.
- Report once per gate, concisely. No per-race check-ins.
