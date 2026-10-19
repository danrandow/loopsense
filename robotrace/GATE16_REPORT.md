# Gate 16: how often does geometry actually change, and a design-only dialogue arm

Written 2026-10-19. Part A is free, offline, zero-cost diagnostics on existing races. Part B is a design,
built and validated but **not run** — no Gate 16 race has started, per Dan's explicit instruction.

## Part A: diagnostics on randow-maps (16 races) and randow-maps-muted (the primary n=8)

### 1. Geometry-change share and controller field-change counts

Two distinct metrics, since Dan's "172-of-176" figure and "how often does the Builder change geometry"
are not the same question — kept separate here so both are answered without conflating them.

**Metric A — does the Integrator pass the Builder's own current-iteration proposal through unchanged**
(the metric behind Dan's recollected "172"): checked directly (comparing `entity0.geometry` written this
iteration against `entity1.geometry` raced this same iteration). **Corrected figure: 173/176 (98.3%)** for
randow-maps (3 overrides: race-139 iteration 11, race-165 iterations 7 and 8), **88/88 (100%)** for
randow-maps-muted. Dan's recollection was off by one — the true pass-through count is 173, not 172.

**Metric B — does the Builder change geometry from the previous iteration's raced design** (freshly
computed, not previously reported): comparing `entity1.geometry` at iteration *i−1* (what actually raced)
against `entity0.geometry` proposed at iteration *i*.

| arm | transitions | geometry changed |
|---|---:|---:|
| randow-maps | 176 | **155 (88.1%)** |
| randow-maps-muted | 88 | **87 (98.9%)** |

Controller field-change counts (Integrator), out of the same transition counts:

| field | randow-maps (/176) | randow-maps-muted (/88) |
|---|---:|---:|
| base_speed | 13 | 7 |
| kp | 38 | 26 |
| ki | 5 | 3 |
| kd | 31 | 29 |
| sensor_weights | 11 | 12 |
| line_loss | 0 | 0 |

`kp` and `kd` dominate in both arms; `line_loss` policy never changes in either.

### 2. Dev score after a geometry change vs. after geometry stayed the same

| arm | mean dev score after CHANGE | mean dev score after SAME | drop share after CHANGE | drop share after SAME |
|---|---:|---:|---:|---:|
| randow-maps | 187.9 (n=155) | 278.1 (n=21) | 67/155 (43.2%) | 2/21 (9.5%) |
| randow-maps-muted | 227.1 (n=87) | 450.6 (n=1) | 35/87 (40.2%) | 0/1 (0.0%) |

A geometry change is followed by a score drop roughly 4x more often than keeping geometry is (43.2% vs.
9.5% for randow-maps). The "SAME" sample is small, especially for randow-maps-muted (n=1 — this arm's
Builder changes geometry nearly every iteration, so almost no same-geometry transitions exist to compare).
Read directionally, not as a tight estimate: mean score is also lower after a change in both arms, though
the small same-geometry n (especially n=1 for the muted arm) means this comparison carries most of its
weight from randow-maps' own n=21.

### 3. Five geometry changes with the weakest telemetry signal

No iteration in either arm was found to be literally reasonless — every geometry change's `intent` cites a
specific, evidence-tied hypothesis, even when the prior design was already performing well. Ranked by the
preceding race's own `finish_rate` (highest first, i.e. the design was already working best when the
Builder changed it anyway), the five weakest-signal cases, all from randow-maps:

**race-169, iteration 11** (prior finish_rate 0.77, line_loss 0.68) — intent: *"Keep the iteration 10
design (best so far, 785.3) and change only body_length from 0.12 m to 0.11 m. This lowers yaw inertia by
about 8 percent at unchanged mass, so the slalom's direction changes are taken faster..."*

**race-169, iteration 10** (0.70, 0.68) — intent: *"Keep the iteration 9 design (best so far, 741.9) and
change only mass from 0.5 to 0.45 kg, a further ~10 percent cut in yaw inertia, to test whether the
slalom progress trend continues..."*

**race-169, iteration 8** (0.67, 0.62) — intent: *"Keep the iteration 7 design... Change only wheel_track
from 0.10 m to 0.09 m to add turn authority at the slalom's direction changes..."*

**race-167, iteration 9** (0.65, 1.02) — intent: *"Change one variable from the best known design
(iteration 8, wheel_track 0.16, score 661.5): raise wheel_track to 0.17 m... This continues the monotone
track-width trend, which R1 specified as the next step..."*

**race-169, iteration 9** (0.65, 0.62) — intent: *"Revert wheel_track to 0.10 m, which scored best
(iteration 7, 707.2), and reduce mass from 0.6 to 0.5 kg to lower yaw inertia about 17 percent further,
testing whether a faster-turning robot keeps the slalom line for longer..."*

All five cite a single-variable change against a named best-so-far baseline, framed as a continued sweep
rather than a response to an acute failure signal. The honest finding: these are the closest thing to
"no clear reason" in the data, and they are not reasonless — they are *continued exploration from an
already-good point*, which is a different thing than "changing because something is visibly broken."

### 4. Does the current output contract allow "keep geometry" and "decline the advice"?

Checked against the literal instruction text in `package-templates/randow-maps/base.yaml` (quoted in
full in `PHASE0_FREEZE.md` §4i's diff section against the new text). Nothing in the schema forbids holding
geometry or declining advice — but nothing in the **instructions** states either is a legitimate choice:

- Builder's instructions: *"work out what in that evidence points at geometry"* — frames the task as
  finding something to change, with no sentence anywhere permitting "nothing points at geometry, keep it
  unchanged."
- Integrator's instructions: *"Tell the Builder what to change depending on what the next race shows (if
  one thing happens, change this field; if another, change that)"* — every branch in this sentence is a
  change branch; no "hold" branch is ever presented as an option.

**Answer: no, not explicitly.** The schema (`entity0`/`entityR1` contracts) doesn't require a change, but
the instruction text, read literally, never tells either role that holding or declining is on the table.
This is exactly the gap Part B's dialogue arm is designed to close.

### 5. Reasoning/thinking setting

Checked directly in `orchestrator/executors.py`'s `_openrouter` function — the literal request body sent
to OpenRouter:

```python
body = {"model": ..., "messages": ..., "temperature": ..., "max_tokens": ...,
        "response_format": {"type": "json_object"}, "usage": {"include": True}}
```

**No `reasoning`, `thinking`, or `effort` parameter is set anywhere in this codebase.** A full grep for
`reasoning|thinking|effort` across the orchestrator turns up only unrelated hits (a docstring and the
response-shape instruction telling the model to put reasoning fields like `rationale`/`intent` first in
its JSON). Any reasoning tokens the model generates are the provider/model's own unconfigured default
behaviour — this project has never deliberately set or tuned this.

## Part B: randow-maps-dialogue — designed, validated, not run

Full detail, exact diffs, and the pre-registration are in `PHASE0_FREEZE.md` §4i (renumbered from Dan's
"§4h," which is already Gate 15's section — same renumbering convention used at every earlier collision).
Summary here:

- **No schema change needed**, confirmed directly: the Integrator already reads `entity0` (which already
  requires `intent`), and the Builder already reads `entityR1` (the Integration Feedback), today, in
  randow-maps unmodified. Only the `notes` (instruction) text changes.
- **Instruction diff** (full text in §4i): adds one shared sentence stating the joint-scoring goal;
  the Builder gains explicit permission to hold geometry, a requirement to say in `rationale` whether it
  took the last advice and why not if it didn't, and permission to preview un-committed geometry thinking
  in `intent`; the Integrator's mandatory "name one to three specific `requested_changes` fields" becomes
  optional, and its feedback may explicitly recommend holding, changing, or exploring, and may ask
  questions. No field, direction, or frequency of change is named or suggested anywhere in the new text.
- **Build and checks, all done at zero cost:** `randow-maps-dialogue` built as a copy of `randow-maps`;
  `diff -rq` confirms only the `entrant` field and the two roles' `notes` differ; `MapPackage.validate()`
  passes; a 3-iteration mock-provider smoke test ran clean (all 3 actions fire every iteration, no stalls,
  no schema errors).
- **Pre-registration (n=8), in §4i:** primary comparison is paired improvement (`primary_metric`, final
  minus iteration 0) against randow-maps (n=16, +160.90) and opt-solo (n=16, +664.70), with a proposed
  decision rule (Dan didn't specify thresholds this time, so one is proposed in §4i mirroring every earlier
  causal gate's "within 100 points + CI excludes 0" framework). Secondary measures pre-specified: geometry-
  change frequency, how often and why the Builder states it declined the last advice, and the controller-
  field-change share shift vs. randow-maps' own Part A figures above.
- **Cost estimate:** $0.12-0.18/race x 8 = **$0.96-$1.44**, grounded in randow-maps' own measured history
  (Gate 8: $0.1311/race; Gate 12 muted: $0.1213/race) — same topology/model/budget, so the same cost
  structure applies.

**No race has been run under this template. Stopping here, per Gate 16's instruction.**
