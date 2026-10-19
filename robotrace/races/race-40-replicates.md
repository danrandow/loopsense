# Replicate comparison

Races: race-40-a, race-40-b, race-40-c

Development score per iteration is the mean over development tracks and seeds; — means the iteration was not raced. Slope is the least-squares change in development score per iteration over the raced iterations. Learning shows as a positive slope, last above first, and a best that arrives late; held-out is the mean over every held-out track and seed.

## randow-maps

| Race | Dev score by iteration | Raced | First → last | Best | Slope/iter | Held-out | Delivered | Tokens charged |
|---|---|---:|---|---:|---:|---:|:-:|---:|
| race-40-a | 606.0 · 751.0 · 719.1 · 666.7 · 748.5 · 693.8 | 6/6 | 606.0 → 693.8 | 751.0 | 10.8 | 455.8 | yes | 115556 |
| race-40-b | 660.2 · 577.4 · — · 537.5 · 537.5 · 629.8 | 5/6 | 660.2 → 629.8 | 660.2 | -9.4 | 519.8 | yes | 129082 |
| race-40-c | 704.8 · 747.5 · 725.8 · 725.8 · 725.8 · 725.8 | 6/6 | 704.8 → 725.8 | 747.5 | 1.1 | 690.7 | yes | 114768 |
| **mean (n=3)** | | 5.7 | 657.0 → 683.2 | 719.6 | 0.9 | 555.4 (sd 121.5) | 3/3 | 119802 |

## opt-eval

| Race | Dev score by iteration | Raced | First → last | Best | Slope/iter | Held-out | Delivered | Tokens charged |
|---|---|---:|---|---:|---:|---:|:-:|---:|
| race-40-a | 105.6 · — · — · — · — · 31.2 | 2/6 | 105.6 → 31.2 | 105.6 | -14.9 | 30.6 | yes | 225186 |
| race-40-b | 481.0 · 408.6 · 217.0 · — · — · — | 3/6 | 481.0 → 217.0 | 481.0 | -132.0 | 0.0 | no | 245446 |
| race-40-c | 777.4 · — · — · 782.6 · 740.3 · 782.6 | 4/6 | 777.4 → 782.6 | 782.6 | -1.9 | 683.2 | yes | 184740 |
| **mean (n=3)** | | 3.0 | 454.7 → 343.6 | 456.4 | -49.6 | 237.9 (sd 385.9) | 2/3 | 218457 |

