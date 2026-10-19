# Gate 17: randow-maps-dialogue, run (n=8)

Written 2026-10-19, per the pre-registration in `PHASE0_FREEZE.md` §4i and its Gate 17 addendum
(committed `b64208ca8` before any Gate 17 race ran). The addendum fixed §4i's original rule to explicitly
cover all five elements Dan asked to confirm — see "The rule, before vs. after" below.

## The rule, before vs. after

§4i as written at Gate 16 already covered (1) and partly (3)/(4) but did not explicitly state a hold-rate
benchmark against randow-maps' figure, commit to quoting examples, or state a Gate-11-class defect check.
The Gate 17 addendum restated the complete rule to cover, explicitly:

1. **Primary: improvement with a CI, vs. both reference arms** — paired improvement (`primary_metric`,
   final iteration minus iteration 0), Welch 95% CI, against randow-maps (n=16) and opt-solo (n=16).
2. **Hold rate, benchmarked against randow-maps' own 11.9% (~12%)** — not just "measure geometry-change
   frequency" in the abstract.
3. **Advice-decline frequency, with 5 reasons quoted verbatim** (or the true count if fewer occur).
4. **Controller-edit share**, restated against randow-maps' own per-field counts.
5. **Zero Gate-11-class defects**, checked structurally before running (zero edges changed from
   randow-maps) and confirmed empirically after.

This is the rule applied below, unchanged from the addendum.

## Ops

8 races (218-225), all completed in full (12/12 iterations, no truncation, no missing iteration 0, no
harness faults, zero reruns needed). Total logged cost **$0.9474** against the $1.50 gate cap; no
individual race approached the $0.25 per-race cap (range $0.0998-$0.1369/race). Balances checked
throughout: `/credits` moved from $6.6862 to $5.7519, `limit_remaining` from $15.6382 to $14.7039 — both
stayed far above the $0.50 stop floor the whole run; the cap was never hit.

## 5. Gate-11-class defect check — zero, confirmed both ways

**Structurally** (pre-registered, before running): `randow-maps-dialogue` changes zero edges from
`randow-maps`; the Integrator's `on_new_inputs` reentry trigger runs over the same input set it always has.
**Empirically** (checked now, after running): zero `"workflow stalled"` or `"no action can run"` outcomes
across all 8 races' `outcome.json` files; zero truncated races; zero races missing iteration 0. The defect
class did not occur, as the structural check predicted.

## 1. Primary comparison: improvement (primary_metric, final − iteration 0)

| race | improvement |
|---|---:|
| race-218 | +645.13 |
| race-219 | +559.01 |
| race-220 | +778.61 |
| race-221 | +8.36 |
| race-222 | +1.72 |
| race-223 | +40.25 |
| race-224 | +20.82 |
| race-225 | +474.82 |
| **mean (sd)** | **+316.09 (330.19)** |

| comparison | Δ | SE | df | 95% CI |
|---|---:|---:|---:|---|
| dialogue − randow-maps (+160.90, n=16) | +155.19 | 125.09 | 9.13 | [−127.15, +437.53] — includes 0 |
| dialogue − opt-solo (+664.70, n=16) | −348.61 | 123.48 | 8.70 | [−629.39, −67.83] — excludes 0 |

**Applying the rule exactly as written: "no detectable difference from randow-maps."** The point estimate
is directionally higher than randow-maps' own (+155 on average) but the CI includes 0 at n=8 — not
significant. Against opt-solo, the CI excludes 0 the other way: opt-solo still significantly exceeds
dialogue. Dialogue has not closed the gap to opt-solo; on this primary measure it is statistically
indistinguishable from the randow-maps arm it modifies.

Variance is wide and bimodal: three races (218, 219, 220) land in the +559 to +779 range, comparable to
opt-solo's own typical range; two (221, 222) show almost no improvement at all (+8, +2); three more sit in
a low-middle band (+20 to +475). This split is noted descriptively — n=8 is not enough to characterise it
further here.

## 2. Hold rate — a large, clear behavioural shift

| arm | transitions | hold (geometry unchanged) |
|---|---:|---:|
| randow-maps (Gate 16) | 176 | 21 (**11.9%**) |
| **randow-maps-dialogue** | 88 | **30 (34.1%)** |

Dialogue holds geometry roughly **3x more often** than randow-maps does. This is the clearest behavioural
difference the new instruction text produced — the Builder uses the newly-granted permission to hold
substantially, not marginally.

## 3. Advice-decline frequency, with 5 reasons quoted

**9 of 88 transitions (10.2%)** contain an explicit statement in the Builder's `rationale` that it did not
take the Integrator's last advice, each with a stated reason (found by text search, not inferred — every
one of the 9 cites a specific piece of evidence). Five, verbatim:

**race-220, iteration 4:** *"This departs from the Integrator's request to keep ±0.04 m. I am declining
that request because race 3 showed ±0.04 m costs oval finishes without fixing s-bend or slalom."*

**race-221, iteration 1:** *"The Integrator advised holding the baseline for a reference race, but I did
not take that advice. The first race is already complete and shows the failure mode clearly, so holding
would waste a race on a known-failing result."*

**race-224, iteration 5:** *"I did not take the Integrator's advice to hold the ±0.04 row, because its own
kp change was part of the candidate and the result is worse."*

**race-224, iteration 9:** *"I therefore do not take the Integrator's request to hold ±0.04 m for another
race, because that race would repeat a result already measured. The Integrator's feedback calls iteration
9 an isolating test, but iteration 8 already ran it."*

**race-225, iteration 6:** *"I did not take the Integrator's earlier suggestions to move sensors forward
or change body width, because the evidence does not support them. The Integrator's controller is also
tuned to this geometry, so holding it unchanged keeps the integration stable."*

Every decline cites a specific prior result (a score, a finish rate, a repeated test) as the reason, not a
vague dismissal — the new instruction text appears to be eliciting exactly the accountability Dan asked
for (state whether advice was taken, and why not if not).

## 4. Controller-edit share

| field | randow-maps (/176) | randow-maps-dialogue (/88) |
|---|---:|---:|
| base_speed | 13 (7.4%) | 21 (**23.9%**) |
| kp | 38 (21.6%) | 33 (**37.5%**) |
| ki | 5 (2.8%) | 5 (5.7%) |
| kd | 31 (17.6%) | 31 (**35.2%**) |
| sensor_weights | 11 (6.3%) | 2 (2.3%) |
| line_loss | 0 | 0 |

Controller edits are proportionally more frequent per transition in dialogue across every field except
`sensor_weights`. This is consistent with the hold-rate finding: when geometry is held more often, the
Integrator appears to lean more on controller tuning (`kp`, `kd`, `base_speed`) to keep improving the same
platform, rather than waiting on a new geometry proposal.

## Plain summary

Dialogue produces a clear, large behavioural shift exactly where the new instructions aimed it — holding
geometry 3x more often than randow-maps, and explicitly declining advice with a stated, evidence-based
reason in about 1 in 10 transitions. It does **not** yet show a statistically detectable improvement over
randow-maps' own primary-metric result at n=8 (point estimate higher, +155 on average, but CI includes 0),
and it remains significantly behind opt-solo. The behavioural change is real and measured; whether it
translates into a reliably better score needs a larger N than this gate's n=8 to resolve — reported here
as "no detectable difference," not as "no effect."

**No further runs. Stopping here per Gate 17's instruction.**
