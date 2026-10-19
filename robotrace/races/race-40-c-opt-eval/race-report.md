# race-40-c — race report

| Place | Entrant | Held-out score | Best development score | Final development score |
|---|---|---:|---:|---:|
| 1 | randow-maps | 690.711 | 747.4739 | 725.8295 |
| 2 | opt-eval | 683.2374 | 782.5979 | 782.5979 |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Total charged is what each team spent against its allowance, including calls whose output the contract rejected (their tokens are not in the input and output columns). History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total charged | of which rejected attempts | history pack (est.) |
|---|---:|---:|---:|---:|---:|---:|
| randow-maps | 12 | 106504 | 8264 | 114768 | 0 | 62469 |
| opt-eval | 24 | 174823 | 9917 | 184740 | 0 | 79699 |
| **Race total** | 36 | 281327 | 18181 | **299508** | 0 | 142168 |

## opt-eval iterations

### Iteration 0 — development score 777.38
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-41 track view, score 993.3, finished](iteration-0/trials/oval-41/track-view.svg)
- [development: oval-42 track view, score 994.0, finished](iteration-0/trials/oval-42/track-view.svg)
- [development: s-bend-41 track view, score 991.7, finished](iteration-0/trials/s-bend-41/track-view.svg)
- [development: s-bend-42 track view, score 991.3, finished](iteration-0/trials/s-bend-42/track-view.svg)
- [development: slalom-41 track view, score 401.1, timeout](iteration-0/trials/slalom-41/track-view.svg)
- [development: slalom-42 track view, score 389.7, timeout](iteration-0/trials/slalom-42/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 18455
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 39201
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 44932
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 782.60
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-41 track view, score 991.0, finished](iteration-3/trials/oval-41/track-view.svg)
- [development: oval-42 track view, score 991.4, finished](iteration-3/trials/oval-42/track-view.svg)
- [development: s-bend-41 track view, score 987.6, finished](iteration-3/trials/s-bend-41/track-view.svg)
- [development: s-bend-42 track view, score 989.0, finished](iteration-3/trials/s-bend-42/track-view.svg)
- [development: slalom-41 track view, score 381.0, timeout](iteration-3/trials/slalom-41/track-view.svg)
- [development: slalom-42 track view, score 382.2, timeout](iteration-3/trials/slalom-42/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 16930
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 740.29
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-41 track view, score 991.9, finished](iteration-4/trials/oval-41/track-view.svg)
- [development: oval-42 track view, score 993.7, finished](iteration-4/trials/oval-42/track-view.svg)
- [development: s-bend-41 track view, score 990.6, finished](iteration-4/trials/s-bend-41/track-view.svg)
- [development: s-bend-42 track view, score 428.0, timeout](iteration-4/trials/s-bend-42/track-view.svg)
- [development: slalom-41 track view, score 288.0, off_track](iteration-4/trials/slalom-41/track-view.svg)
- [development: slalom-42 track view, score 370.2, timeout](iteration-4/trials/slalom-42/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 41148
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 782.60
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-41 track view, score 991.0, finished](iteration-5/trials/oval-41/track-view.svg)
- [development: oval-42 track view, score 991.4, finished](iteration-5/trials/oval-42/track-view.svg)
- [development: s-bend-41 track view, score 987.6, finished](iteration-5/trials/s-bend-41/track-view.svg)
- [development: s-bend-42 track view, score 989.0, finished](iteration-5/trials/s-bend-42/track-view.svg)
- [development: slalom-41 track view, score 381.0, timeout](iteration-5/trials/slalom-41/track-view.svg)
- [development: slalom-42 track view, score 382.2, timeout](iteration-5/trials/slalom-42/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 24074
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total charged: 184740 of 300000 allowed; 174823 input and 9917 output over 24 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 79699

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3619 | 574 | 4193 | 3 |
| 0 | 2 | action1 | 4622 | 340 | 4962 | 3 |
| 0 | 3 | action0 | 3958 | 481 | 4439 | 3 |
| 0 | 4 | action1 | 4518 | 343 | 4861 | 3 |
| 0 | 5 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 5508 | 485 | 5993 | 3 |
| 1 | 2 | action1 | 6616 | 264 | 6880 | 3 |
| 1 | 3 | action0 | 5756 | 482 | 6238 | 3 |
| 1 | 4 | action1 | 6601 | 348 | 6949 | 3 |
| 1 | 5 | action0 | 5789 | 471 | 6260 | 3 |
| 1 | 6 | action1 | 6595 | 286 | 6881 | 3 |
| 2 | 1 | action0 | 6455 | 478 | 6933 | 3 |
| 2 | 2 | action1 | 7558 | 310 | 7868 | 3 |
| 2 | 3 | action0 | 6690 | 478 | 7168 | 3 |
| 2 | 4 | action1 | 7556 | 271 | 7827 | 3 |
| 2 | 5 | action0 | 6711 | 470 | 7181 | 3 |
| 2 | 6 | action1 | 7546 | 409 | 7955 | 3 |
| 3 | 1 | action0 | 7399 | 466 | 7865 | 3 |
| 3 | 2 | action1 | 8700 | 365 | 9065 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 9011 | 542 | 9553 | 3 |
| 4 | 2 | action1 | 10596 | 310 | 10906 | 3 |
| 4 | 3 | action0 | 9305 | 503 | 9808 | 3 |
| 4 | 4 | action1 | 10548 | 333 | 10881 | 3 |
| 4 | 5 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 10699 | 524 | 11223 | 3 |
| 5 | 2 | action1 | 12467 | 384 | 12851 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-101 track view, score 988.3, finished](final-held-out/trials/hairpin-101/track-view.svg)
- [held-out: hairpin-102 track view, score 987.4, finished](final-held-out/trials/hairpin-102/track-view.svg)
- [held-out: hairpin-b-101 track view, score 221.5, off_track](final-held-out/trials/hairpin-b-101/track-view.svg)
- [held-out: hairpin-b-102 track view, score 983.7, finished](final-held-out/trials/hairpin-b-102/track-view.svg)
- [held-out: slalom-b-101 track view, score 329.8, timeout](final-held-out/trials/slalom-b-101/track-view.svg)
- [held-out: slalom-b-102 track view, score 287.3, off_track](final-held-out/trials/slalom-b-102/track-view.svg)
