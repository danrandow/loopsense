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

## randow-maps iterations

### Iteration 0 — development score 660.21
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-21 track view, score 994.3, finished](iteration-0/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 994.8, finished](iteration-0/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 990.9, finished](iteration-0/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 404.5, off_track](iteration-0/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 249.5, off_track](iteration-0/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 198.9, off_track](iteration-0/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9489
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 577.36
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-21 track view, score 994.2, finished](iteration-1/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 306.2, off_track](iteration-1/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 395.0, off_track](iteration-1/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 332.6, off_track](iteration-1/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 201.6, off_track](iteration-1/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 209.3, off_track](iteration-1/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 13504
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — not raced (action0's output was rejected after repeated attempts: entity0 contract violation: Additional properties are not allowed ('hypotheses' was unexpected))
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 537.52
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-21 track view, score 416.6, off_track](iteration-3/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 427.7, off_track](iteration-3/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 380.1, off_track](iteration-3/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 295.2, off_track](iteration-3/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 199.7, off_track](iteration-3/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 226.6, off_track](iteration-3/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 28264
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 537.52
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-21 track view, score 416.6, off_track](iteration-4/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 427.7, off_track](iteration-4/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 380.1, off_track](iteration-4/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 295.2, off_track](iteration-4/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 199.7, off_track](iteration-4/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 226.6, off_track](iteration-4/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 21857
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 629.78
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-21 track view, score 992.0, finished](iteration-5/trials/oval-21/track-view.svg)
- [development: oval-22 track view, score 992.7, finished](iteration-5/trials/oval-22/track-view.svg)
- [development: s-bend-21 track view, score 374.4, off_track](iteration-5/trials/s-bend-21/track-view.svg)
- [development: s-bend-22 track view, score 993.2, finished](iteration-5/trials/s-bend-22/track-view.svg)
- [development: slalom-21 track view, score 166.1, off_track](iteration-5/trials/slalom-21/track-view.svg)
- [development: slalom-22 track view, score 169.1, off_track](iteration-5/trials/slalom-22/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 24948
- Scenario file: scenario-iteration-5.yaml

## randow-maps token cost

- Total charged: 129082 of 300000 allowed; 90581 input and 7481 output over 10 completed model calls, plus 31020 on rejected attempts
- History pack (estimate, part of input): 43307

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3645 | 519 | 4164 | 3 |
| 0 | 2 | action1 | 4634 | 691 | 5325 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 5456 | 519 | 5975 | 3 |
| 1 | 2 | action1 | 6882 | 647 | 7529 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 7257 | 568 | 7825 | 3 |
| 3 | 2 | action1 | 18623 | 1816 | 20439 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 8874 | 563 | 9437 | 3 |
| 4 | 2 | action1 | 11547 | 873 | 12420 | 3 |
| 4 | 3 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 10215 | 490 | 10705 | 3 |
| 5 | 2 | action1 | 13448 | 795 | 14243 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-101 track view, score 354.8, off_track](final-held-out/trials/hairpin-101/track-view.svg)
- [held-out: hairpin-102 track view, score 991.6, finished](final-held-out/trials/hairpin-102/track-view.svg)
- [held-out: hairpin-b-101 track view, score 372.0, off_track](final-held-out/trials/hairpin-b-101/track-view.svg)
- [held-out: hairpin-b-102 track view, score 357.5, off_track](final-held-out/trials/hairpin-b-102/track-view.svg)
- [held-out: slalom-b-101 track view, score 163.8, off_track](final-held-out/trials/slalom-b-101/track-view.svg)
- [held-out: slalom-b-102 track view, score 291.4, off_track](final-held-out/trials/slalom-b-102/track-view.svg)
