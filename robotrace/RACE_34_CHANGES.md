# Changes for race 34

Prompted by the analysis of race 33 (opt-eval 625.5, randow-maps 553.9). **Scores are not comparable with earlier races**: the track sets, development seeds and per-iteration token cap all changed.

## Why

- In race 33 the whole 72-point gap came from one held-out trial (randow-maps on hairpin seed 105: 233 against about 988). Without it randow-maps would have won (about 629 to 625).
- Both teams scored 984-994 on the development tracks (oval, s-bend) from iteration 1 on, with one development seed (noise about ±1). Development scores therefore gave no gradient: iteration-to-iteration changes were mostly noise, and neither team could see the slalom failure (0/10 held-out slalom trials finished).
- opt-eval's iteration 4 was reported as "not raced (token budget exhausted)" although only 586k of 1M tokens had been spent. It had hit the 160k per-iteration cap after two re-triggers; iteration 5 then spent about 87k tokens re-submitting the iteration-3 design.

## Tracks

| | Race 33 | Race 34 |
|---|---|---|
| Development | oval, s-bend | oval, s-bend, **slalom** |
| Held-out | hairpin, slalom | hairpin, **hairpin-b**, **slalom-b** |

- `tracks/held-out/slalom.json` moved to `tracks/development/slalom.json` (`held_out: false`).
- New held-out tracks: `hairpin-b` (family hairpin, difficulty 0.85, length 12) and `slalom-b` (family slalom, difficulty 0.7, length 28).
- Calibrated with the race-33 final designs on seeds 17, 101, 102, 103 before adoption. hairpin-b: opt-eval 1/4 finish, randow-maps 2/4. slalom-b: opt-eval 2/4, randow-maps 1/4. Plain hairpin is kept as an easy floor (opt-eval 5/5, randow-maps 4/5 finish). Hairpin at difficulty 0.85 or 1.0 with its original length was too easy (every seed finished) and was rejected.
- Caveat: slalom-b shares a family with the development slalom, so fitting development slalom may partly transfer. hairpin and hairpin-b are the only held-out families the teams never see in development.
- Caveat: on development slalom seed 17 randow-maps finished (984) while opt-eval failed (260); randow-maps fails three of the four other seeds, hence the extra seeds below.

## Development seeds

`seeds: [17, 29, 41]` (was `[17]`) in both templates: nine development trials per iteration. This averages out seed noise and exposes seed-sensitive designs. The history pack is still capped by `telemetry_token_ceiling`, so the extra trials should not grow prompts without limit; check the history-pack size in the first race. Held-out seeds are unchanged (101-105).

## Token caps and labels

- `max_tokens_per_iteration` raised from 160,000 to 300,000 in both templates (`total_tokens_per_condition` stays 1,000,000).
- `orchestrator/controller.py`: an iteration closed for tokens now says which limit bound. "iteration token cap reached: X of Y tokens used this iteration (Z of T total tokens still unspent)" or "total token budget exhausted: X of T tokens used". `tests/test_incomplete_iteration.py` updated.

## Not changed

Replicate races (own development seed each, shared held-out seeds) are still the way to judge learning; a single race's ranking should not be read as evidence.
