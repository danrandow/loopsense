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

## randow-maps iterations

### Iteration 0 — development score 699.44
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-17 track view, score 992.2, finished](iteration-0/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 406.7, off_track](iteration-0/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 9429
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — development score 991.64
- [Open development race summary](iteration-1/iteration-summary.svg)
- [development: oval-17 track view, score 991.8, finished](iteration-1/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 991.5, finished](iteration-1/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 70298
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — development score 984.00
- [Open development race summary](iteration-2/iteration-summary.svg)
- [development: oval-17 track view, score 977.4, finished](iteration-2/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 990.6, finished](iteration-2/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 81974
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — development score 992.46
- [Open development race summary](iteration-3/iteration-summary.svg)
- [development: oval-17 track view, score 993.5, finished](iteration-3/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 991.4, finished](iteration-3/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 81441
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — development score 992.46
- [Open development race summary](iteration-4/iteration-summary.svg)
- [development: oval-17 track view, score 993.5, finished](iteration-4/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 991.4, finished](iteration-4/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 83417
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 991.38
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-17 track view, score 993.1, finished](iteration-5/trials/oval-17/track-view.svg)
- [development: s-bend-17 track view, score 989.7, finished](iteration-5/trials/s-bend-17/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 85805
- Scenario file: scenario-iteration-5.yaml

## randow-maps token cost

- Total charged: 412364 of 1000000 allowed; 405547 input and 6817 output over 12 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 52514

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3643 | 498 | 4141 | 3 |
| 0 | 2 | action1 | 4608 | 680 | 5288 | 3 |
| 0 | 3 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 33878 | 524 | 34402 | 3 |
| 1 | 2 | action1 | 35276 | 620 | 35896 | 3 |
| 1 | 3 | action2 (simulator) | — | — | — | — |
| 2 | 1 | action0 | 39430 | 469 | 39899 | 3 |
| 2 | 2 | action1 | 41354 | 721 | 42075 | 3 |
| 2 | 3 | action2 (simulator) | — | — | — | — |
| 3 | 1 | action0 | 38927 | 450 | 39377 | 3 |
| 3 | 2 | action1 | 41409 | 655 | 42064 | 3 |
| 3 | 3 | action2 (simulator) | — | — | — | — |
| 4 | 1 | action0 | 39721 | 422 | 40143 | 3 |
| 4 | 2 | action1 | 42646 | 628 | 43274 | 3 |
| 4 | 3 | action2 (simulator) | — | — | — | — |
| 5 | 1 | action0 | 40604 | 457 | 41061 | 3 |
| 5 | 2 | action1 | 44051 | 693 | 44744 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-101 track view, score 988.3, finished](final-held-out/trials/hairpin-101/track-view.svg)
- [held-out: hairpin-102 track view, score 988.3, finished](final-held-out/trials/hairpin-102/track-view.svg)
- [held-out: hairpin-103 track view, score 988.3, finished](final-held-out/trials/hairpin-103/track-view.svg)
- [held-out: hairpin-104 track view, score 988.3, finished](final-held-out/trials/hairpin-104/track-view.svg)
- [held-out: hairpin-105 track view, score 233.4, off_track](final-held-out/trials/hairpin-105/track-view.svg)
- [held-out: slalom-101 track view, score 153.3, off_track](final-held-out/trials/slalom-101/track-view.svg)
- [held-out: slalom-102 track view, score 208.4, off_track](final-held-out/trials/slalom-102/track-view.svg)
- [held-out: slalom-103 track view, score 314.0, off_track](final-held-out/trials/slalom-103/track-view.svg)
- [held-out: slalom-104 track view, score 411.7, off_track](final-held-out/trials/slalom-104/track-view.svg)
- [held-out: slalom-105 track view, score 264.5, off_track](final-held-out/trials/slalom-105/track-view.svg)
