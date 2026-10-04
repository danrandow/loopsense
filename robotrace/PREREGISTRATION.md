# Robot Race recorded run v1 — preregistration

Frozen before inspecting any results from the native-physics recorded run.

## Primary comparison

Compare the five-iteration adaptation trajectory of the LoopSense producer–integrator condition with the conventional optimizer–evaluator condition. Report current score, best-so-far score, improvement per iteration, and improvement per 10,000 tokens. Do not interpret pilot or smoke scores as evidence.

## Frozen run

- Run identifier: `race-4`
- Configuration: `config/recorded-race-v1.json`
- Conditions: LoopSense and control, deterministically interleaved by iteration
- Iterations: exactly five per condition
- Continuation: no extension based on observed scores; a later run requires a new preregistration
- Model: `openai/gpt-4.1-mini` through OpenRouter
- Sampling: temperature 0, low reasoning, 2,000 maximum output tokens
- Budget: 50,000 tokens per condition; 10,000 per iteration
- Control cycles: at most two optimizer–evaluator cycles per iteration
- Repair policy: one mechanical repair call per malformed artifact
- Simulator: `robottracesim-native-v1`, maximum 1,200 steps per trial
- Seeds: 17 and 29
- Noise: 0.02
- Development tracks: oval and S-bend; oval is the anchor
- Held-out track: hairpin, evaluated only after the fifth build and never supplied to a model
- Score weights: validity gate, then completion 500, progress 250, robustness 120, time 60, precision 70

## Decision and reporting rules

The primary record includes all raw metrics and the composite score. Conclusions must state development and held-out results separately. A topology is not declared superior solely because of one final composite score; the comparison must include adaptation trajectory, worst case, invalid artifacts, repair calls, and token use. Equal or conflicting results are reported as ambiguous.

A harness defect stops both conditions. Fixing a defect requires a new version and a fresh run. Transient model failures follow the recorded bounded retry policy. Budget exhaustion does not grant extra calls. Resume is allowed only when configuration and implementation-plan hashes match the frozen manifest.

## Run gate

Before starting, all tests must pass, configuration validation must pass, the native library must rebuild from the pinned source, the Git worktree must identify the exact implementation commit, and no `race-4` output directory may already exist.
