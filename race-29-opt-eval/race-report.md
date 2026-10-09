# race-29 — race report

| Place | Entrant | Held-out score | Final development score |
|---:|---|---:|---:|
| 1 | opt-eval | 20.6196 | 48.0978 |
| 2 | randow-maps | 4.1132 | 27.5312 |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Input plus output tokens over every model call. History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total tokens | of which history pack (est.) |
|---|---:|---:|---:|---:|---:|
| opt-eval | 12 | 150103 | 6148 | 156251 | 20655 |
| randow-maps | 12 | 118762 | 7648 | 126410 | 33331 |
| **Race total** | 24 | 268865 | 13796 | **282661** | 53986 |

## opt-eval iterations

### Iteration 0 — development score 39.91
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 21.0, off_track](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 58.8, off_track](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 6084
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 40.90
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 24.0, off_track](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 57.8, off_track](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 25697
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 41.89
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-17 track view, score 24.9, off_track](iteration-2/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 58.8, off_track](iteration-2/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 27585
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 41.38
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-17 track view, score 24.9, off_track](iteration-3/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 57.8, off_track](iteration-3/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 29209
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 11.47
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-17 track view, score 12.6, stalled](iteration-4/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 10.4, off_track](iteration-4/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 30728
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 48.10
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-17 track view, score 38.3, off_track](iteration-5/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 57.9, off_track](iteration-5/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 36948
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total: 156251 of 250000 allowed (150103 input, 6148 output) over 12 model calls
- History pack (estimate, part of input): 20655

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 2202 | 445 | 2647 | 3 |
| 0 | 2 | action1 | 3052 | 385 | 3437 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 12089 | 504 | 12593 | 3 |
| 1 | 2 | action1 | 12516 | 588 | 13104 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 13555 | 478 | 14033 | 3 |
| 2 | 2 | action1 | 12974 | 578 | 13552 | 3 |
| 2 | 3 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 14794 | 469 | 15263 | 3 |
| 3 | 2 | action1 | 13313 | 633 | 13946 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 16058 | 429 | 16487 | 3 |
| 4 | 2 | action1 | 13656 | 585 | 14241 | 3 |
| 4 | 3 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 17911 | 408 | 18319 | 3 |
| 5 | 2 | action1 | 17983 | 646 | 18629 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-17 track view, score 22.7, off_track](final-held-out/trials/hairpin-17/track-view.svg)
- [held-out: slalom-17 track view, score 18.6, off_track](final-held-out/trials/slalom-17/track-view.svg)
