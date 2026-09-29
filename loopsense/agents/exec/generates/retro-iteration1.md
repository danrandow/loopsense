# Exec — Iteration 1 Retro

Scope: my own experience working in the harness, not output quality. Status kept distinct: workflow — kickoff executed, brief and viability signal filed; experiment — the ten-post loop was never run (blocked on a gate/decision deadlock); hypothesis outcome — unchanged, zero direct evidence for the mechanism; formal closure — this retro.

## 1. What worked

The write boundary and read order removed all ambiguity; I never guessed where a file belonged. Reading `team-registry.md` and `reading-the-map.md` up front meant I could locate PM's bet and Delivery's/GTM's bypass flows without asking anyone. The `note` field's explicit Was/Now text in the log made the audit trail trustworthy without re-deriving intent from diffs. Standing rule 7's "no history record for own outputs" kept this session cheap.

## 2. What did not work

**The bypass flows never arrived.** I certify with four inputs: PM's bet, Delivery's cost & risk (entityR2A), GTM's pipeline (entityR3B), and my own knowledge file. Two of those four were missing or stale at every session this iteration — no `entityR2A` exists at all, and `entityR3B` on file is still iteration-0's. I flagged both as gaps per standing rule 2 and proceeded on a partial input set, but that is a workaround, not a protocol: nothing in the harness says "if a required input is missing after N cycles, surface it as a blocker" rather than "note it and carry on." I guessed that a spec-run certification does not need a cost/risk input; that guess is probably right but it is a guess.

**The output-status gap between workflow completion and experiment execution made my certification read as more than it was.** I certified "run the ten-post loop" and produced the brief; that is a completed workflow. But the loop itself never ran, and the hypothesis is unchanged. My certification is scoped to permission to run an existing spec — not a claim that the business model works, not a funding commitment, not evidence the mechanism is verified. I had to state that scope guard explicitly in the brief and again in the viability signal because nothing in the harness enforces the distinction between "workflow done" and "experiment done" at the point of handoff.

**I guessed at the retro's status without a source.** The write boundary in SKILL.md does not enumerate `retro-iteration1.md`. I wrote it under owner instruction and iteration-0 precedent (PM's retro at log 178 uses the same reasoning). That is a gap in the write boundary that I worked around by assumption.

## 3. One harness change

**Give every required input a staleness bound and a single escalation path.** Specifically: when an agent's "before acting" read list names a required input (entityR2A, entityR3B, etc.), the harness should record when that input was last updated and require the consuming agent to name the gap as a blocker — not a footnote — if it is older than one iteration or missing. Right now each agent independently re-discovers the same missing inputs and re-flags them to PM (I did it in entityR1-v0, entityR1-v1, and my certification notes; PM did it in entity0-v1; Delivery did it in entityR2-v1). A single dated "inputs outstanding" register, checked at kickoff, would replace three parallel re-discoveries with one actionable status line and make the difference between "certified on full inputs" and "certified on partial inputs" visible at the point of decision.

---

*Files written this session: `agents/exec/generates/entity1-v1.md`, `agents/exec/generates/entityR1-v1.md`, `agents/exec/knowledge/exec-v0.md` (certification history appended), `iteration-1.yaml` (entity1/entityR1 overrides). No entityR2A or current entityR3B existed at any point this iteration; both flagged as gaps in every output.*
