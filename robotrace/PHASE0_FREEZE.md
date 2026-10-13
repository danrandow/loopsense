# Phase 0: freeze and pre-registered pass criterion

Written 2026-10-12, before any Phase 0 baseline run was read and before any Phase 1 (LLM) run. This file is the
pre-registration required by `CLAUDE.md`: the frozen configuration and the pass/fail rule for Phase 1 are fixed
here, in advance, so neither can be adjusted after seeing results.

## 1. What is frozen

| Element | Value |
|---|---|
| Simulator / adapter version | `robottracesim-native-v2` (`ADAPTER_VERSION` in `simulator/adapter`) |
| Simulator code digest (sha256 of all `.py`/`.c`/`.so` under `simulator/`, 15 files) | `f8725dc8ed83ff91…` |
| Tracks digest (sha256 of all `tracks/*/*.json`, 6 files) | `cd99e42ad630a02b…` |
| `randow-maps` template package digest (`MapPackage.hashes()` over 17 definition files, combined) | `2f2015a6d271c9a9…` |
| `opt-eval` template package digest (same method, 17 files) | `c8bd38dd8c8ecb1c…` |
| Development tracks | oval, s-bend, slalom |
| Held-out tracks | hairpin, hairpin-b, slalom-b |
| Development seeds | 1–20 (per track) |
| Held-out seeds | 101–120 (per track), shared/identical across replicates |
| Noise | 0.02 (right-motor PWM bias per seed; sensor noise sd 0.001, fixed in the adapter, not in race.yaml) |
| `max_steps` | **300** (= 3.0 s at the adapter's 10 ms step) — see §2 for the 300-vs-1200 resolution |
| `stall_steps` / `stall_min_progress` | 50 / 0.002 |
| Score weights | completion 500, progress 250, robustness 120, time 60, precision 70 |
| Iterations per race | 12 (raised from 6 in this freeze; see `CHANGELOG-autonomous.md`) |
| `max_action_runs` | 6 per iteration |
| `total_tokens_per_condition` / `max_tokens_per_iteration` | 2,000,000 / 300,000 |

Confirmed before freezing: `evaluation`, `simulator`, and `score` blocks are byte-identical between the
`randow-maps` and `opt-eval` templates (diffed directly; `MapDrivenController.validate_pair` also enforces this
on every race). Both entrants race under the same frozen numbers.

The digests above describe the code as of commit **`80ac0f05`** ("robotrace: clarify per-call budget fields, cut-off
feedback, raise iteration/token caps; fix two pre-existing test bugs") on branch `sim-validity-fixes` — the commit
that last touched `orchestrator/*`, `simulator/*`, `tracks/*`, or either `race.yaml` template before this freeze
was written. Any change to simulator code, track files, score weights, seeds, or `max_steps` after that commit
invalidates comparisons against the Phase 0 baseline runs below and requires a new freeze (new digests, new
commit hash, reported as a deviation per the Gate rules in `CLAUDE.md`).

## 2. Resolution: `max_steps` 300 (race.yaml) vs 1200 (experiment.yaml)

`config/experiment.yaml` is a legacy artifact from the removed pre-map-driven runner (`mode: "smoke"`,
`experiment_id: "robotrace-smoke"`). It is **not read by any live race code path**: `orchestrator/race_service.py`,
`orchestrator/controller.py`, and `orchestrator/executors.py` only ever read `config/race.yaml` inside a package
(confirmed by grep — no reference to `experiment.yaml` anywhere under `orchestrator/`). The file is still read by
four adapter-level unit tests (`test_experiment.py`, `test_sim_validity.py`, `test_race16.py`,
`test_design_contract.py`) and by `tools/calibration/survey_tracks.py`, each as a convenient bag of adapter
defaults — and two of those test files already override `max_steps` to 300 locally before asserting anything
sim-validity-relevant, which shows the 300 value was already understood as authoritative, just never written
down.

**Resolution: `race.yaml`'s `max_steps: 300` (3.0 s) is what every race actually runs under, and is the value this
freeze uses throughout.** `experiment.yaml`'s 1200 is dead for race purposes. This is not merely a default
pick: the baseline search (§3) finds designs that finish all six tracks with mean completion times of 1.9–2.4 s,
comfortably inside the 3.0 s / 300-step cap — so 300 steps is a real, binding, but *achievable* budget, not an
arbitrary one that makes every run time out regardless of design quality. No code change was needed; this
section is the record of the decision for anyone who reads `experiment.yaml` next and wonders.

## 3. Ceiling and noise (no LLM): ES search and random hill-climb

All runs below cost zero tokens (pure simulation) and use the frozen config in §1. Seeds for the *search's own*
randomness (`--rng`) are varied to show how much the result depends on search luck, separately from the dev/
held-out seed sets, which are fixed per §1.

### 3a. Ceiling: `tools/baseline_search.py`, full design space, 5 independent search seeds

Command: `python3 tools/baseline_search.py --space full --evals 300 --train-seeds 10 --rng {1..5}`
(train seeds are the tool's own offset block 1000–1009, by design distinct from the race's dev seeds 1–20, so the
search never sees the exact seeds a race would use — see tool docstring). Validation = 50 fresh seeds (5000–5049),
never used by the search. Held-out = seeds 101–110 on hairpin/hairpin-b/slalom-b. Start design (same for every
run, zero search-seed randomness applied yet): train 688, validation 674, held-out 232.

| search `--rng` | train mean | validation mean (fresh) | held-out mean | wall clock |
|---:|---:|---:|---:|---:|
| 1 | 944 | 932 | 794 | 573 s |
| 2 | 945 | 920 | 579 | 561 s |
| 3 | 949 | 917 | 721 | 514 s |
| 4 | 935 | 932 | 266 | 504 s |
| 5 | 947 | 937 | 639 | 612 s |
| **mean (n=5)** | **944.0** | **927.6** | **599.8** | |
| **sd (n=5)** | **5.4** | **8.6** | **203.6** | |

300 evaluations × 10 train seeds × 3 dev tracks, full design space, each run ≈ 9–10 minutes single-threaded (ran
5-way in parallel on an 8-core machine).

**Reading this:** the ceiling on fresh dev-track seeds (the column the Phase 1 pass criterion actually uses) is
tight and reproducible across search-seed luck — mean 927.6, sd 8.6 (<1% relative). Held-out-*track* (new track
shape, not just new seed) generalization is not — sd 203.6 on a mean of 599.8, CV ≈ 34% — which search seed you
land on matters a great deal for whether the found design transfers to an unseen track shape. This matters for
interpreting any Phase-2 held-out comparison later, but the held-out column is not part of either Phase 1
criterion (§4/§4a are scored on fresh dev-track seeds only), so it is not gating here.
**ES ceiling for §4a's headroom-closed metric: 927.6 (validation mean, n=5), start 674 → 253.6 points of
headroom available over 300 full-space evaluations.**

### 3b. Noise/reference line: `tools/probe_step.py --random-only`, matched to the race's 12-iteration budget

This is the free baseline a single LLM agent (Phase 1) must beat: a random hill-climb given the *same* iteration
budget (12) the race template now gives a team, selecting on the same evidence (summary, not full telemetry) the
agents see, scored on fresh held-out-style seeds the search never used.

Command (K=1, one proposal per iteration — matches the race's one-call-per-role-per-iteration structure):
`python3 tools/probe_step.py --random-only --loop 12 --runs 10 --space full --rng 1`

Command (K=4, best-of-4 per iteration — kept for continuity with the earlier Haiku K=4 probe in
`k4_haiku.txt`, not the structure an actual race uses):
`python3 tools/probe_step.py --random-only --loop 12 --runs 10 --candidates 4 --space full --rng 2`

Start design mean on 30 fresh seeds (5000–5029): 674 — same start design as §3a, consistent across both tools.

**K=1 (matches the race's one-proposal-per-iteration structure), 10 runs, final-iteration gain over start:**
`[70, 132, 7, 259, 72, 0, 0, −7, 104, 3]`; best-so-far-per-run (never dips below the running max):
`[70, 186, 7, 259, 72, 0, 0, 0, 104, 3]` → **mean +70.1, sd 90.4, median +38.5**. 3 of 10 runs never improve at
all in 12 steps (a single random mutation per step has a real chance of never finding an uphill move); 1 run
reaches +259. This is the primary free baseline for §4's in-race-loop comparison: it is noisy (sd nearly 1.3×
the mean) because K=1 is a weak search, which is itself informative about how low a bar "beat random K=1" can
be.

**K=4 (best-of-4 per iteration), 10 runs, final best-so-far-by-evidence:**
`[243, 272, 212, 71, 213, 188, 243, 220, 260, 257]` → **mean +217.9, sd 57.7, median +231.5**. Markedly higher and
less noisy than K=1 (no near-zero runs) — matches the qualitative pattern in the earlier (pre-freeze, v1-adapter)
`k4_haiku.txt` probe where K=4 was a much steadier baseline than K=1, though the absolute numbers there are not
comparable (different adapter version, different track calibration; this run is the v2-adapter, frozen-config
measurement and supersedes that one for any future comparison under this freeze). Reported for context; §4's
gating comparison uses K=1 because that is the structure an actual race iteration has.

## 4. Pre-registered pass criterion for Phase 1 (write BEFORE running any LLM)

Phase 1's question (G2): *does a single LLM agent (Haiku 5.5 via OpenRouter), given the simulator as a tool with
an evaluation budget, improve a design from feedback beyond what the free random hill-climb baseline in §3b
achieves with the same 12-iteration budget?*

Design: 10 paired replicates. Replicate *i* gives the LLM agent and a random-hill-climb run (§3b, K=1) the
**same** starting design and the **same** development-seed evidence draw, so the comparison is paired, not just
two independent samples. "Dev score" = mean score over the three development tracks on the fresh validation
seeds defined in `tools/probe_step.py` (the 30-seed block offset 5000+, never seen during the loop) — the same
metric `run_loop`'s `score()` already reports, so no new scoring code is needed.

**Pass (Phase 1 clears G2) only if BOTH hold:**

1. **Learning.** The agent's best-so-far dev score at iteration 12 exceeds its iteration-0 (start) dev score in
   at least **8 of 10** replicates. (One-sided sign test against a 50% null; 8/10 gives p ≈ 0.055 — the loosest
   threshold still worth calling a result rather than noise, matching the number CLAUDE.md itself suggested.)
2. **Beats the free baseline.** In the same 10 replicates, the agent's final best-so-far dev score exceeds the
   paired random-hill-climb run's final best-so-far dev score in at least **8 of 10** replicates.

**Fail** if either condition is not met. A pass on (1) alone ("it learns, but no better than free search") is
explicitly **not** a pass for G2 — the mandate's question is whether an LLM agent clears the free baseline, not
whether it merely improves on its own first attempt. If (1) fails, (2) need not be evaluated and the result is
reported as a fail with the (1) numbers.

**Noise context.** §3a's search-seed spread (ceiling: sd 8.6 on fresh dev seeds — tight) and §3b's replicate
spread (K=1 random hill-climb over 12 iterations: mean +70.1, sd 90.4 — very wide, sd exceeds the mean) show that
almost all of the run-to-run variation in this setup comes from the free baseline's own luck, not from the
ceiling being unstable. An agent result only a little above +70 on average could easily be noise; the §4a(ii)
10-point minimum effect size is a floor, not a substitute for looking at the full paired distribution.

This criterion is fixed before any Phase 1 (LLM) run starts. If Phase 1 data suggest it was a poor choice (too
strict, too loose, or scoring something unintended), that is reported as a deviation at Gate 2, not changed
quietly.

## 4a. Amendment (2026-10-12, before Phase 1 — no LLM run has occurred under §4 or this amendment)

Five changes to §4, made before any Phase 1 data exists and logged here rather than edited into §4 silently, so
the before/after and the reasoning are both on record.

**(i) Criterion 2 is now evaluated at matched *evaluation* budget, not matched *iteration* count.** §4 as written
compared the agent's iteration-12 result to a random-hill-climb run also given exactly 12 steps. That under-
counts the baselines if the agent's harness lets it spend more simulator evaluations per iteration than one
hill-climb step does (e.g. tool-call access to the simulator, or multiple trials per proposal) — in that case 12
iterations is not 12 units of search effort, and "beats a 12-step hill-climb" would be comparing unequal budgets.
Phase 1's harness must log, per replicate, the number of simulator evaluations the agent's run actually consumed
(`N_evals`: one evaluation = one candidate design scored across the dev tracks/seed grid, the same unit
`baseline_search.py --evals` and `probe_step.py --loop` steps already use). Criterion 2 then compares the agent's
final dev score, per replicate, against:
  - a random-hill-climb run (`probe_step.py --random-only --loop`) given exactly `N_evals` steps, and
  - an ES run (`baseline_search.py --space full`) given exactly `N_evals` evaluations,
  both re-run per replicate at that replicate's own `N_evals` (seeded so the comparison stays paired), rather than
  a fixed 12.

**(ii) Two non-gating supplementary numbers are added, not used to pass/fail:**
  - *Headroom closed* = `(agent_final − start) / (ES_ceiling − start)`, where `ES_ceiling` is §3a's mean ceiling
    score (full-space search, large `--evals`, not capped to `N_evals`). Reported per replicate and as a mean;
    shows how much of the available improvement the agent captured, independent of whether it beat the
    matched-budget baselines.
  - *Minimum effect size for a "win".* A replicate only counts as a win for criterion 2 if the agent's margin over
    the matched-budget baseline exceeds **10 points** (on the same dev-score scale as §3). A margin inside ±10
    is treated as a tie, not a win, since §3's own replicate-to-replicate spread (noise) is on that order — a
    "win" smaller than the baseline's own noise band would not be evidence of anything.

**(iii) The original 12-iteration-matched comparison in §4 is kept, not replaced.** It is reported as a separate
result labelled "in-race-loop comparison" (how the agent does within the race harness's actual 12-iteration
structure, regardless of how many simulator evaluations that took), alongside the matched-`N_evals` comparison in
(i). The two answer different questions — "does it beat free search given the same number of race iterations"
vs. "...given the same amount of search effort" — and both are reported, with neither silently standing in for
the other.

**(iv) 7 of 10 is inconclusive, not a fail.** For both criterion 1 (learning) and criterion 2 (beats the matched
baseline, win-margin applied), the reporting bands are: **≥8/10 → pass**, **≤6/10 → fail**, **exactly 7/10 →
inconclusive**, reported as such rather than rounded down to fail. An inconclusive result at Gate 2 is reported
to Dan as inconclusive, with a recommendation (more replicates, or treat as a soft fail) rather than resolved
unilaterally.

**(v) Commit hash.** The code state these digests and this document describe is commit `80ac0f05` (see §1, filled
in above). This amendment and the rest of this document are committed in later commits on `sim-validity-fixes`;
`git log -- robotrace/PHASE0_FREEZE.md` is authoritative for exactly when each part was written, which matters
here only insofar as every part of §4/§4a predates any Phase 1 run.

## §4b. Primary metric reversed (2026-10-14, approved by Dan, before any new race result is seen)

**Reason.** `PHASE1_RESULTS.md`'s Gate 3b held-out comparison: the agent's held-out mean (545.3) was not
clearly separated from the matched free-search baseline's (517.0) -- well inside one sample sd of either side
(agent sd 155.4, pooled matched-baseline sd 143.1, the full-search ES ceiling sd 203.8 on n=5). Held-out
per-design sd is on the order of **143-204** against means in the 500-600 range (CV roughly 25-40%), while the
same designs' dev-validation score sd was 19.8 -- an order of magnitude tighter. Ranking on a metric with this
much noise relative to signal risks measuring which design happened to transfer to three fixed unseen track
shapes, not which design (or team) is actually better; this was flagged as a reversal needing explicit sign-off
in `PHASE2_DESIGN.md` §3 and has now been approved.

**What changes.** The **primary** comparison metric is now: mean score over the three fresh validation seeds
(5000-5029) run against (a) the three literal development tracks (oval, s-bend, slalom, as before) and (b)
freshly generated tracks from the same three families, at a fixed generator seed. The fixed held-out tracks
(hairpin, hairpin-b, slalom-b) become a **secondary**, reported-but-not-gating transfer metric -- still computed
and shown in every result, just no longer what a pass/fail or a team-vs-team ranking is decided on.

**Evaluation path (implemented, zero token cost).** `tools/fresh_tracks.py`:
- `generate_fresh_tracks(seed=777)` samples `{difficulty, length}` per dev family (oval, s-bend, slalom) around
  that family's own existing dev-track values (`DEV_TRACK_CENTRE`), spread `difficulty ± 0.20`, `length ± 3.0`
  -- the same scale of difference already seen between a dev track and its held-out counterpart (e.g. dev
  `slalom` difficulty 0.25 vs held-out `slalom-b` difficulty 0.45). **`FRESH_TRACK_SEED = 777`, fixed and
  recorded here; do not change without a new freeze entry.** 3 fresh tracks per family (9 total), deterministic
  (same seed always returns the same tracks -- checked directly: calling it twice returns identical output).
- `primary_metric(design, dev_tracks, config, seeds, fresh_tracks=None)` scores a design on the 3 dev tracks
  plus the 9 fresh tracks (12 tracks total), on the given seeds, and returns the mean -- the same `run_trial`
  / scoring code every other tool in this session uses, so this is additive to the existing dev-score
  machinery, not a new scoring path. Tracks are a pure function of `{family, difficulty, length}`
  (`simulator/adapter/headless.py`'s `_track_polyline`), confirmed by construction, not just by inspection: the
  module generates them directly from those three fields.
- Sanity-checked against the frozen starting design (seeds 5000-5009): mean 653.6 across all 12 tracks,
  individual fresh-track scores (e.g. `oval-fresh-1` 940.5, `slalom-fresh-2` 187.9) falling in between their
  family's dev and held-out scores as expected, not off in some unrelated range.
