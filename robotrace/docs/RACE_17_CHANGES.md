# Harness changes for race 17

These change what the agents see and how an unfinished iteration is handled, so scores are **not comparable with races 0–16**.
Both entrants get identical behaviour: the changes are in the generic controller and executor, not in the frozen package files.
`CONTROLLER_VERSION` is now `map-driven-v2` and is recorded in each race manifest.

Trigger: race 16 failed with `workflow stalled; missing completion entities: ['entity2']`. In iteration 1 the model returned only
`entity3` and `entityPrv0` (the prompt allowed omitting outputs), `entity0` was never written, `action1` could not run,
and the controller raised, which failed the whole race.

| Change | Where |
|---|---|
| Each model action is told which other actions read each output it may write (from the topology's `used by` edges): the action id, what it does, its actor, and whether it cannot run without that output. The omission wording in the system message points at this list. | `orchestrator/executors.py` (`downstream_dependents`, `_openrouter`) |
| Each model action is told where it is in the race (`iteration`, `iterations_total`, `iterations_remaining_after_this`, `final_iteration`), which entities complete an iteration, and what happens if one does not finish. The final iteration carries an explicit warning that no delivered design means a held-out score of 0 that the team will not see. | `orchestrator/executors.py` (`iteration_guidance`), `orchestrator/controller.py` (`run_iteration`) |
| An iteration that cannot finish (no action can run, token budget spent, action-run budget spent) no longer raises. It writes `iteration-N/outcome.json` (`complete: false`, reason, `undelivered` entities, `blocked_actions`) and the next iteration is seeded as usual. Its development race is not run and not scored. | `orchestrator/controller.py` (`_close_incomplete`, `_seed_next_iteration`) |
| The next iteration's prompt includes `previous_iteration_incomplete` (reason, undelivered entities, blocked actions) so the actors can learn from it. | `orchestrator/controller.py` (`_previous_incomplete`), `orchestrator/executors.py` |
| If the final iteration ends with no design (`entity1`), the held-out race is not run: the entrant scores 0.0, `final-evaluation.json` records `incomplete: true` with the reason, and the race still completes. A design that was delivered is raced as before, even if the iteration itself was incomplete. | `orchestrator/race_service.py` (`_execute`, `_publish_iteration`) |

Not changed: "model response exceeded the configured token budget" still raises, because it is detected before the transaction commits. Invalid-design handling is unchanged.

Tests: `tests/test_incomplete_iteration.py`.
