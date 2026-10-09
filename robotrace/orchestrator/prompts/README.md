# Prompt contracts

Prompts are assembled by `runner.py` from explicit per-call allowlists. Every call writes a `context-manifest.json` containing only key names and hashes. Entity 2, held-out tracks, and the run root are rejected as model context.

Role instructions are loaded from `conditions/<condition>/actors/<role>/instructions.md`; their hashes are frozen in each race manifest. Static private expertise is loaded from `conditions/<condition>/private/`. Each AI role also owns one private learning file under the race run root (`<condition>/learning/<role>.md`). The model returns a complete replacement for that compact learning state after every valid turn, so learning persists across iterations within one race and resets for a new race.

Addressed return routing is enforced by the prompt assembler: `entityR2A` goes only to actor0 and `entityR2B` only to actor1. The control condition's shared candidate/evaluation blackboard lives under `control/blackboard/` for one race and is included as shared history; it is not carried into another race.

The bundled `mock` provider makes smoke tests offline and deterministic. A recorded run must add an explicit model-provider adapter and freeze its identifier and settings in `config/experiment.yaml`.
