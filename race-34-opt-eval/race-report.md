# race-34 — race report

| Place | Entrant | Held-out score | Best development score | Final development score |
|---|---|---:|---:|---:|
| 1= | opt-eval | 0.0 | 701.7034 | not raced |
| 1= | randow-maps | 0.0 | 779.4548 | not raced |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Total charged is what each team spent against its allowance, including calls whose output the contract rejected (their tokens are not in the input and output columns). History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total charged | of which rejected attempts | history pack (est.) |
|---|---:|---:|---:|---:|---:|---:|
| opt-eval | 10 | 980209 | 4573 | 984782 | 0 | 36595 |
| randow-maps | 10 | 965336 | 5842 | 971178 | 0 | 39307 |
| **Race total** | 20 | 1945545 | 10415 | **1955960** | 0 | 75902 |

## opt-eval iterations

### Iteration 0 — development score 628.76
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 990.8, finished](iteration-0/trials/oval-17/track-view.svg)
- [development: oval-29 track view, score 990.4, finished](iteration-0/trials/oval-29/track-view.svg)
- [development: oval-41 track view, score 992.6, finished](iteration-0/trials/oval-41/track-view.svg)
- [development: s-bend-17 track view, score 989.6, finished](iteration-0/trials/s-bend-17/track-view.svg)
- [development: s-bend-29 track view, score 988.6, finished](iteration-0/trials/s-bend-29/track-view.svg)
- [development: s-bend-41 track view, score 337.3, off_track](iteration-0/trials/s-bend-41/track-view.svg)
- [development: slalom-17 track view, score 127.7, off_track](iteration-0/trials/slalom-17/track-view.svg)
- [development: slalom-29 track view, score 142.4, off_track](iteration-0/trials/slalom-29/track-view.svg)
- [development: slalom-41 track view, score 99.5, off_track](iteration-0/trials/slalom-41/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9142
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 622.35
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 991.9, finished](iteration-1/trials/oval-17/track-view.svg)
- [development: oval-29 track view, score 990.5, finished](iteration-1/trials/oval-29/track-view.svg)
- [development: oval-41 track view, score 989.8, finished](iteration-1/trials/oval-41/track-view.svg)
- [development: s-bend-17 track view, score 989.8, finished](iteration-1/trials/s-bend-17/track-view.svg)
- [development: s-bend-29 track view, score 988.6, finished](iteration-1/trials/s-bend-29/track-view.svg)
- [development: s-bend-41 track view, score 314.1, off_track](iteration-1/trials/s-bend-41/track-view.svg)
- [development: slalom-17 track view, score 90.2, off_track](iteration-1/trials/slalom-17/track-view.svg)
- [development: slalom-29 track view, score 135.8, off_track](iteration-1/trials/slalom-29/track-view.svg)
- [development: slalom-41 track view, score 110.4, off_track](iteration-1/trials/slalom-41/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 243942
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — not raced (token budget exhausted: action0 needs about 77400 input tokens plus at least 500 to answer, but 53274 remain)
- Action runs: 2 · re-triggered runs: 0 · tokens: 246726
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 701.70
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-17 track view, score 990.4, finished](iteration-3/trials/oval-17/track-view.svg)
- [development: oval-29 track view, score 990.4, finished](iteration-3/trials/oval-29/track-view.svg)
- [development: oval-41 track view, score 990.4, finished](iteration-3/trials/oval-41/track-view.svg)
- [development: s-bend-17 track view, score 990.0, finished](iteration-3/trials/s-bend-17/track-view.svg)
- [development: s-bend-29 track view, score 991.1, finished](iteration-3/trials/s-bend-29/track-view.svg)
- [development: s-bend-41 track view, score 990.5, finished](iteration-3/trials/s-bend-41/track-view.svg)
- [development: slalom-17 track view, score 118.8, off_track](iteration-3/trials/slalom-17/track-view.svg)
- [development: slalom-29 track view, score 117.8, off_track](iteration-3/trials/slalom-29/track-view.svg)
- [development: slalom-41 track view, score 135.7, off_track](iteration-3/trials/slalom-41/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 246821
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — not raced (token budget exhausted: action0 needs about 75027 input tokens plus at least 500 to answer, but 15218 remain)
- Action runs: 2 · re-triggered runs: 0 · tokens: 238151
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — not raced (token budget exhausted: action0 needs about 75431 input tokens plus at least 500 to answer, but 15218 remain)
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total charged: 984782 of 1000000 allowed; 980209 input and 4573 output over 10 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 36595

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3620 | 507 | 4127 | 3 |
| 0 | 2 | action1 | 4572 | 443 | 5015 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 120922 | 568 | 121490 | 3 |
| 1 | 2 | action1 | 122128 | 324 | 122452 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 122247 | 527 | 122774 | 3 |
| 2 | 2 | action1 | 123630 | 322 | 123952 | 3 |
| 3 | 1 | action0 | 123315 | 553 | 123868 | 3 |
| 3 | 2 | action1 | 122635 | 318 | 122953 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 120699 | 570 | 121269 | 3 |
| 4 | 2 | action1 | 116441 | 441 | 116882 | 3 |

## Final held-out race

Not raced: no design was delivered in the final iteration. Score 0.
