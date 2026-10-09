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

## randow-maps iterations

### Iteration 0 — development score 19.66
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 28.0, off_track](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 11.3, off_track](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 6455
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 20.69
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 30.0, off_track](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 11.4, off_track](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 19807
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 20.68
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-17 track view, score 30.0, off_track](iteration-2/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 11.4, off_track](iteration-2/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 25719
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 17.08
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-17 track view, score 28.0, off_track](iteration-3/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 6.2, off_track](iteration-3/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 27008
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 17.08
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-17 track view, score 28.0, off_track](iteration-4/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 6.2, off_track](iteration-4/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 22920
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 27.53
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-17 track view, score 41.7, off_track](iteration-5/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 13.4, off_track](iteration-5/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 24501
- Scenario file: scenario-iteration-5.yaml

## randow-maps token cost

- Total: 126410 of 250000 allowed (118762 input, 7648 output) over 12 model calls
- History pack (estimate, part of input): 33331

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 2228 | 468 | 2696 | 3 |
| 0 | 2 | action1 | 3009 | 750 | 3759 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 8703 | 464 | 9167 | 3 |
| 1 | 2 | action1 | 9866 | 774 | 10640 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 15008 | 511 | 15519 | 3 |
| 2 | 2 | action1 | 9322 | 878 | 10200 | 3 |
| 2 | 3 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 16331 | 422 | 16753 | 3 |
| 3 | 2 | action1 | 9545 | 710 | 10255 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 11964 | 487 | 12451 | 3 |
| 4 | 2 | action1 | 9676 | 793 | 10469 | 3 |
| 4 | 3 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 12957 | 625 | 13582 | 3 |
| 5 | 2 | action1 | 10153 | 766 | 10919 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-17 track view, score 6.2, off_track](final-held-out/trials/hairpin-17/track-view.svg)
- [held-out: slalom-17 track view, score 2.1, off_track](final-held-out/trials/slalom-17/track-view.svg)
