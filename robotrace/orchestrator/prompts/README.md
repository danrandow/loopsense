# Prompt contracts

Prompts are assembled by `runner.py` from explicit per-call allowlists. Every call writes a `context-manifest.json` containing only key names and hashes. Entity 2, held-out tracks, and the run root are rejected as model context.

The bundled `mock` provider makes smoke tests offline and deterministic. A recorded run must add an explicit model-provider adapter and freeze its identifier and settings in `config/experiment.yaml`.

