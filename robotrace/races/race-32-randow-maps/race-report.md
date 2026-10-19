# race-32 — race report

| Place | Entrant | Held-out score | Final development score |
|---:|---|---:|---:|
| 1 | randow-maps | 0.0 | 6.7371 |
| 2 | opt-eval | 0.0 | — |

[Open the leaderboard chart](leaderboard.svg)

## randow-maps iterations

### Iteration 0 — development score 5.69
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 11.4, off_track](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 0.0, stalled](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9532
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 0.99
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 2.0, stalled](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 0.0, stalled](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 24264
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 8.81
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-17 track view, score 17.6, off_track](iteration-2/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 0.0, stalled](iteration-2/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 41404
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — not raced (token budget exhausted: action0 needs about 21374 input tokens plus at least 500 to answer, but 247 remain)
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — not raced (token budget exhausted)
- Action runs: 1 · re-triggered runs: 0 · tokens: 80118
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 6.74
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-17 track view, score 13.5, off_track](iteration-5/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 0.0, stalled](iteration-5/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 67955
- Scenario file: scenario-iteration-5.yaml

## randow-maps token cost

- Total: 223273 of 500000 allowed (215820 input, 7453 output) over 9 model calls
- History pack (estimate, part of input): 44055

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3642 | 502 | 4144 | 3 |
| 0 | 2 | action1 | 4617 | 771 | 5388 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 10773 | 604 | 11377 | 3 |
| 1 | 2 | action1 | 12163 | 724 | 12887 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 19009 | 544 | 19553 | 3 |
| 2 | 2 | action1 | 21079 | 772 | 21851 | 3 |
| 2 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 78558 | 1560 | 80118 | 3 |
| 5 | 1 | action0 | 53685 | 1070 | 54755 | 3 |
| 5 | 2 | action1 | 12294 | 906 | 13200 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-17 track view, score 0.0, stalled](final-held-out/trials/hairpin-17/track-view.svg)
- [held-out: slalom-17 track view, score 0.0, stalled](final-held-out/trials/slalom-17/track-view.svg)
