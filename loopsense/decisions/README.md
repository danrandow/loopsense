# Decision records

Short records of material owner or PM decisions — the ones that change what the team does, may do, or is. Ordinary changes need no record: their Git commit briefly says what changed and why (`knowledge/audit-policy.md`).

## Format

One file per decision: `decisions/YYYY-MM-DD-slug.md`, with four short sections:

- **Context** — the situation and the options considered
- **Decision** — what was decided, by whom, on what date
- **Why** — the reasons that carried it
- **Consequences** — what changes, and what is now out of date

Keep each section to a few lines. Link the evidence (files, entities, commits); do not copy it.

## Who writes

Loopy writes a record when Dan makes a material decision; PM records its own material decisions the same way. A record explains a decision — it is not an instruction. Current instructions live in `knowledge/`, `agents/*/SKILL.md` and `workflows/`.
