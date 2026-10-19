# race-33 — race report

| Place | Entrant | Held-out score | Best development score | Final development score |
|---|---|---:|---:|---:|
| 1 | opt-eval | 625.4984 | 993.7913 | 990.5959 |
| 2 | randow-maps | 553.8736 | 992.4616 | 991.3778 |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Total charged is what each team spent against its allowance, including calls whose output the contract rejected (their tokens are not in the input and output columns). History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total charged | of which rejected attempts | history pack (est.) |
|---|---:|---:|---:|---:|---:|---:|
| opt-eval | 20 | 665063 | 8256 | 673319 | 0 | 60810 |
| randow-maps | 12 | 405547 | 6817 | 412364 | 0 | 52514 |
| **Race total** | 32 | 1070610 | 15073 | **1085683** | 0 | 113324 |

## opt-eval iterations

### Iteration 0 — development score 993.00
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 995.3, finished](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 990.7, finished](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 18214
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 993.79
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 995.4, finished](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 992.1, finished](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 156310
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 992.80
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-17 track view, score 994.0, finished](iteration-2/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 991.6, finished](iteration-2/trials/s-bend-17/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 161691
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 990.60
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-17 track view, score 992.0, finished](iteration-3/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 989.2, finished](iteration-3/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 83414
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — not raced (token budget exhausted)
- Action runs: 4 · re-triggered runs: 2 · tokens: 166406
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 990.60
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-17 track view, score 992.0, finished](iteration-5/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 989.2, finished](iteration-5/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 87284
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total charged: 673319 of 1000000 allowed; 665063 input and 8256 output over 20 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 60810

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3617 | 497 | 4114 | 3 |
| 0 | 2 | action1 | 4558 | 374 | 4932 | 3 |
| 0 | 3 | action0 | 3926 | 437 | 4363 | 3 |
| 0 | 4 | action1 | 4485 | 320 | 4805 | 3 |
| 0 | 5 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 38335 | 444 | 38779 | 3 |
| 1 | 2 | action1 | 39392 | 263 | 39655 | 3 |
| 1 | 3 | action0 | 38582 | 460 | 39042 | 3 |
| 1 | 4 | action1 | 38569 | 265 | 38834 | 3 |
| 1 | 5 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 39723 | 512 | 40235 | 3 |
| 2 | 2 | action1 | 41085 | 284 | 41369 | 3 |
| 2 | 3 | action0 | 39991 | 597 | 40588 | 3 |
| 2 | 4 | action1 | 39071 | 428 | 39499 | 3 |
| 2 | 5 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 40587 | 435 | 41022 | 3 |
| 3 | 2 | action1 | 42070 | 322 | 42392 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 41267 | 518 | 41785 | 3 |
| 4 | 2 | action1 | 43055 | 341 | 43396 | 3 |
| 4 | 3 | action0 | 41592 | 532 | 42124 | 3 |
| 4 | 4 | action1 | 38786 | 315 | 39101 | 3 |
| 5 | 1 | action0 | 42293 | 530 | 42823 | 3 |
| 5 | 2 | action1 | 44079 | 382 | 44461 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-101 track view, score 984.4, finished](final-held-out/trials/hairpin-101/track-view.svg)
- [held-out: hairpin-102 track view, score 985.0, finished](final-held-out/trials/hairpin-102/track-view.svg)
- [held-out: hairpin-103 track view, score 985.8, finished](final-held-out/trials/hairpin-103/track-view.svg)
- [held-out: hairpin-104 track view, score 985.7, finished](final-held-out/trials/hairpin-104/track-view.svg)
- [held-out: hairpin-105 track view, score 986.0, finished](final-held-out/trials/hairpin-105/track-view.svg)
- [held-out: slalom-101 track view, score 260.6, off_track](final-held-out/trials/slalom-101/track-view.svg)
- [held-out: slalom-102 track view, score 286.9, off_track](final-held-out/trials/slalom-102/track-view.svg)
- [held-out: slalom-103 track view, score 260.6, off_track](final-held-out/trials/slalom-103/track-view.svg)
- [held-out: slalom-104 track view, score 259.5, off_track](final-held-out/trials/slalom-104/track-view.svg)
- [held-out: slalom-105 track view, score 260.6, off_track](final-held-out/trials/slalom-105/track-view.svg)
