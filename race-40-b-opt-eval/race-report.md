# race-40-b — race report

| Place | Entrant | Held-out score | Best development score | Final development score |
|---|---|---:|---:|---:|
| 1 | randow-maps | 519.8174 | 660.2122 | 629.7777 |
| 2 | opt-eval | 0.0 | 481.0129 | not raced |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Total charged is what each team spent against its allowance, including calls whose output the contract rejected (their tokens are not in the input and output columns). History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total charged | of which rejected attempts | history pack (est.) |
|---|---:|---:|---:|---:|---:|---:|
| randow-maps | 10 | 90581 | 7481 | 129082 | 31020 | 43307 |
| opt-eval | 24 | 235307 | 10139 | 245446 | 0 | 146701 |
| **Race total** | 34 | 325888 | 17620 | **374528** | 31020 | 190008 |

## opt-eval iterations

### Iteration 0 — development score 481.01
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-21 track view, score 990.4, finished](iteration-0/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 991.0, finished](iteration-0/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 987.3, finished](iteration-0/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 987.3, finished](iteration-0/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 0.0, stalled](iteration-0/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 0.0, stalled](iteration-0/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9168
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 408.56
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-21 track view, score 988.6, finished](iteration-1/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 989.8, finished](iteration-1/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 393.8, off_track](iteration-1/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 345.3, off_track](iteration-1/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 0.0, stalled](iteration-1/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 0.0, stalled](iteration-1/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 13382
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 217.01
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-21 track view, score 354.0, off_track](iteration-2/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 354.0, off_track](iteration-2/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 423.2, timeout](iteration-2/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 336.9, off_track](iteration-2/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 0.0, stalled](iteration-2/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 0.0, stalled](iteration-2/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 17059
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 62578
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 68834
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 74425
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total charged: 245446 of 300000 allowed; 235307 input and 10139 output over 24 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 146701

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3619 | 539 | 4158 | 3 |
| 0 | 2 | action1 | 4591 | 419 | 5010 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 5674 | 550 | 6224 | 3 |
| 1 | 2 | action1 | 6840 | 318 | 7158 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 7422 | 528 | 7950 | 3 |
| 2 | 2 | action1 | 8794 | 315 | 9109 | 3 |
| 2 | 3 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 9139 | 524 | 9663 | 3 |
| 3 | 2 | action1 | 10725 | 263 | 10988 | 3 |
| 3 | 3 | action0 | 9386 | 525 | 9911 | 3 |
| 3 | 4 | action1 | 10707 | 317 | 11024 | 3 |
| 3 | 5 | action0 | 9440 | 528 | 9968 | 3 |
| 3 | 6 | action1 | 10713 | 311 | 11024 | 3 |
| 4 | 1 | action0 | 10152 | 551 | 10703 | 3 |
| 4 | 2 | action1 | 11766 | 352 | 12118 | 3 |
| 4 | 3 | action0 | 10489 | 532 | 11021 | 3 |
| 4 | 4 | action1 | 11726 | 349 | 12075 | 3 |
| 4 | 5 | action0 | 10486 | 462 | 10948 | 3 |
| 4 | 6 | action1 | 11697 | 272 | 11969 | 3 |
| 5 | 1 | action0 | 11096 | 557 | 11653 | 3 |
| 5 | 2 | action1 | 12724 | 292 | 13016 | 3 |
| 5 | 3 | action0 | 11373 | 498 | 11871 | 3 |
| 5 | 4 | action1 | 12664 | 325 | 12989 | 3 |
| 5 | 5 | action0 | 11406 | 526 | 11932 | 3 |
| 5 | 6 | action1 | 12678 | 286 | 12964 | 3 |

## Final held-out race

Not raced: no design was delivered in the final iteration. Score 0.
