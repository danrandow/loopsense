# race-40-a — race report

| Place | Entrant | Held-out score | Best development score | Final development score |
|---|---|---:|---:|---:|
| 1 | randow-maps | 455.7675 | 751.0044 | 693.8474 |
| 2 | opt-eval | 30.591 | 105.6406 | 31.2149 |

[Open the leaderboard chart](leaderboard.svg)

## Token cost

Total charged is what each team spent against its allowance, including calls whose output the contract rejected (their tokens are not in the input and output columns). History-pack tokens are an estimate of the part of the input that is the history pack (about 3 characters per token).

| Entrant | Model calls | Input tokens | Output tokens | Total charged | of which rejected attempts | history pack (est.) |
|---|---:|---:|---:|---:|---:|---:|
| randow-maps | 12 | 107858 | 7698 | 115556 | 0 | 64880 |
| opt-eval | 30 | 213341 | 11845 | 225186 | 0 | 91520 |
| **Race total** | 42 | 321199 | 19543 | **340742** | 0 | 156400 |

## opt-eval iterations

### Iteration 0 — development score 105.64
- [Open development race summary](iteration-0/iteration-summary.svg)
- [development: oval-1 track view, score 76.9, off_track](iteration-0/trials/oval-1/track-view.svg)
- [development: oval-2 track view, score 76.9, off_track](iteration-0/trials/oval-2/track-view.svg)
- [development: s-bend-1 track view, score 99.7, off_track](iteration-0/trials/s-bend-1/track-view.svg)
- [development: s-bend-2 track view, score 117.9, off_track](iteration-0/trials/s-bend-2/track-view.svg)
- [development: slalom-1 track view, score 62.5, off_track](iteration-0/trials/slalom-1/track-view.svg)
- [development: slalom-2 track view, score 63.6, off_track](iteration-0/trials/slalom-2/track-view.svg)
- Action runs: 5 · re-triggered runs: 2 · tokens: 18262
- Scenario file: scenario-iteration-0.yaml

### Iteration 1 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 38528
- Scenario file: scenario-iteration-1.yaml

### Iteration 2 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 44517
- Scenario file: scenario-iteration-2.yaml

### Iteration 3 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 49641
- Scenario file: scenario-iteration-3.yaml

### Iteration 4 — not raced (action-run budget exhausted: 6 of 6 runs used before completion)
- Action runs: 6 · re-triggered runs: 4 · tokens: 54405
- Scenario file: scenario-iteration-4.yaml

### Iteration 5 — development score 31.21
- [Open development race summary](iteration-5/iteration-summary.svg)
- [development: oval-1 track view, score 45.3, off_track](iteration-5/trials/oval-1/track-view.svg)
- [development: oval-2 track view, score 45.3, off_track](iteration-5/trials/oval-2/track-view.svg)
- [development: s-bend-1 track view, score 16.5, off_track](iteration-5/trials/s-bend-1/track-view.svg)
- [development: s-bend-2 track view, score 16.5, off_track](iteration-5/trials/s-bend-2/track-view.svg)
- [development: slalom-1 track view, score 31.9, off_track](iteration-5/trials/slalom-1/track-view.svg)
- [development: slalom-2 track view, score 31.9, off_track](iteration-5/trials/slalom-2/track-view.svg)
- Action runs: 3 · re-triggered runs: 0 · tokens: 19833
- Scenario file: scenario-iteration-5.yaml

## opt-eval token cost

- Total charged: 225186 of 300000 allowed; 213341 input and 11845 output over 30 completed model calls, plus 0 on rejected attempts
- History pack (estimate, part of input): 91520

## Action runs and tokens per call

Every recorded action run, in order. A run beyond the first of the same action in an iteration counts as a re-trigger.

| Iteration | Call | Action | Input tokens | Output tokens | Total tokens | Repair attempts |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 1 | action0 | 3619 | 520 | 4139 | 3 |
| 0 | 2 | action1 | 4583 | 365 | 4948 | 3 |
| 0 | 3 | action0 | 3925 | 454 | 4379 | 3 |
| 0 | 4 | action1 | 4501 | 295 | 4796 | 3 |
| 0 | 5 | action2 (simulator) | — | — | — | — |
| 1 | 1 | action0 | 5408 | 460 | 5868 | 3 |
| 1 | 2 | action1 | 6489 | 286 | 6775 | 3 |
| 1 | 3 | action0 | 5678 | 494 | 6172 | 3 |
| 1 | 4 | action1 | 6541 | 244 | 6785 | 3 |
| 1 | 5 | action0 | 5636 | 479 | 6115 | 3 |
| 1 | 6 | action1 | 6510 | 303 | 6813 | 3 |
| 2 | 1 | action0 | 6383 | 552 | 6935 | 3 |
| 2 | 2 | action1 | 7522 | 338 | 7860 | 3 |
| 2 | 3 | action0 | 6651 | 461 | 7112 | 3 |
| 2 | 4 | action1 | 7480 | 329 | 7809 | 3 |
| 2 | 5 | action0 | 6635 | 425 | 7060 | 3 |
| 2 | 6 | action1 | 7438 | 303 | 7741 | 3 |
| 3 | 1 | action0 | 7205 | 582 | 7787 | 3 |
| 3 | 2 | action1 | 8423 | 301 | 8724 | 3 |
| 3 | 3 | action0 | 7491 | 467 | 7958 | 3 |
| 3 | 4 | action1 | 8304 | 357 | 8661 | 3 |
| 3 | 5 | action0 | 7474 | 450 | 7924 | 3 |
| 3 | 6 | action1 | 8283 | 304 | 8587 | 3 |
| 4 | 1 | action0 | 8065 | 464 | 8529 | 3 |
| 4 | 2 | action1 | 9165 | 289 | 9454 | 3 |
| 4 | 3 | action0 | 8284 | 424 | 8708 | 3 |
| 4 | 4 | action1 | 9129 | 303 | 9432 | 3 |
| 4 | 5 | action0 | 8294 | 499 | 8793 | 3 |
| 4 | 6 | action1 | 9160 | 329 | 9489 | 3 |
| 5 | 1 | action0 | 8998 | 449 | 9447 | 3 |
| 5 | 2 | action1 | 10067 | 319 | 10386 | 3 |
| 5 | 3 | action2 (simulator) | — | — | — | — |

## Final held-out race

- [Open held-out race summary](final-held-out/iteration-summary.svg)
- [held-out: hairpin-101 track view, score 52.6, off_track](final-held-out/trials/hairpin-101/track-view.svg)
- [held-out: hairpin-102 track view, score 52.6, off_track](final-held-out/trials/hairpin-102/track-view.svg)
- [held-out: hairpin-b-101 track view, score 9.3, off_track](final-held-out/trials/hairpin-b-101/track-view.svg)
- [held-out: hairpin-b-102 track view, score 9.3, off_track](final-held-out/trials/hairpin-b-102/track-view.svg)
- [held-out: slalom-b-101 track view, score 29.9, off_track](final-held-out/trials/slalom-b-101/track-view.svg)
- [held-out: slalom-b-102 track view, score 29.9, off_track](final-held-out/trials/slalom-b-102/track-view.svg)
