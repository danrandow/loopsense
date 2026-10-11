# race-32 — race report

| Place | Entrant | Held-out score | Final development score |
|---:|---|---:|---:|
| 1 | randow-maps | 0.0 | 6.7371 |
| 2 | opt-eval | 0.0 | — |

[Open the leaderboard chart](leaderboard.svg)

## opt-eval iterations

### Iteration 0 — development score 992.38
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 992.3, finished](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 992.4, finished](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9116
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 675.17
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 993.3, finished](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 357.0, off_track](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 77019
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — not raced (token budget exhausted: action0 needs about 25950 input tokens plus at least 500 to answer, but 3704 remain)
- Action runs: 2 · re-triggered runs: 0 · tokens: 76296
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — not raced (token budget exhausted: action0 needs about 26368 input tokens plus at least 500 to answer, but 2369 remain)
- Action runs: 2 · re-triggered runs: 0 · tokens: 77631
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 617.24
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-17 track view, score 993.1, finished](iteration-4/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 241.4, off_track](iteration-4/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 78943
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — not raced (token budget exhausted: action0 needs about 23919 input tokens plus at least 500 to answer, but 9632 remain)
- Action runs: 2 · re-triggered runs: 0 · tokens: 70368
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total: 389373 of 500000 allowed (384307 input, 5066 output) over 12 model calls
- History pack (estimate, part of input): 26545

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3616 | 530 | 4146 | 3 |
| 0 | 2 | action1 | 4587 | 383 | 4970 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 38093 | 445 | 38538 | 3 |
| 1 | 2 | action1 | 38144 | 337 | 38481 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 38128 | 555 | 38683 | 3 |
| 2 | 2 | action1 | 37343 | 270 | 37613 | 3 |
| 3 | 1 | action0 | 39171 | 485 | 39656 | 3 |
| 3 | 2 | action1 | 37614 | 361 | 37975 | 3 |
| 4 | 1 | action0 | 40200 | 513 | 40713 | 3 |
| 4 | 2 | action1 | 37891 | 339 | 38230 | 3 |
| 4 | 3 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 36373 | 519 | 36892 | 3 |
| 5 | 2 | action1 | 33147 | 329 | 33476 | 3 |

## Final held-out race

Not raced: no design was delivered in the final iteration. Score 0.
