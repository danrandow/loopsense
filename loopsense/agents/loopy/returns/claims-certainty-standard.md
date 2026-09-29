---
name: claims-certainty-standard
description: Evidence-backing and certainty labeling standard for public material
iteration: 0
sources:
  - cowork
---

# Claims & Certainty Standard

## Status
Dan approved 2026-09-23. In effect for all public-facing material from this point forward.

## Purpose
Public credibility depends on making only claims we can back with evidence, and being explicit about our certainty level when it matters. This standard ensures high-stakes claims (market positioning, competitive analysis, research findings, and GTM material) are either sourced or explicitly labeled with certainty status. Prevents marketing and strategic claims from being misread as fact when they are hypothesis or interpretation, while keeping normal documentation prose readable.

## Standard

### Definition
A "claim" is any statement of fact about:
- Market conditions, trends, or practitioner behavior
- Competitor capabilities or positioning
- Loopsense's own performance, features, or viability
- Research findings, trends, or observed patterns
- Any statement attributing beliefs, actions, or capabilities to a named person or account

A "claim" does NOT include:
- Procedural statements (e.g., "the PM reads all downstream flows")
- Design decisions (e.g., "we chose YAML for configuration")
- Personal or hypothetical preferences (e.g., "we believe structured topologies are valuable")

### Labeling
Apply one of four labels to claims that are substantive, high-stakes, or easily misread (competitor positioning, market claims, research findings, GTM positioning). Labels are selective, not required on every factual statement—normal prose about what Loopsense does, design decisions, or documentation descriptions stays readable without mandatory inline labels.

#### 1. **[Verified]** — Source Linked
Direct evidence exists and is linked.
- Example: `[Verified] LangGraph is used in production by 100+ teams ([source: LangChain community metrics](link))`
- Rule: link must be to the primary source or to a page that cites the source with full context
- No interpretation or calculation between the source and the claim

#### 2. **[Unverified]** — Claim Exists; We Haven't Checked
A claim is widely made but we have not independently verified it.
- Example: `[Unverified] CrewAI has 50K+ GitHub stars (we saw this cited; have not verified latest count)`
- Rule: mark the claim as circulating but not sourced by Loopsense
- Use when a competitor's claim is notable but we lack a current source
- Do not use for speculation — only for claims others have made

#### 3. **[Hypothesis]** — Our Working Assumption
Our own hypothesis about how the market, practitioners, or the product works.
- Example: `[Hypothesis] Practitioners building multi-agent product work experience verification gaps similar to those in testing frameworks`
- Rule: this is our bet, not yet validated by evidence
- Hypotheses are live while we gather evidence
- Mark as [Verified] once practitioner verbatims confirm it

#### 4. **[Our Interpretation]** — Data Exists; This is Our Read
We are interpreting raw data or combining multiple sources to form a conclusion.
- Example: `[Our Interpretation] The shift from LangGraph code-first to CrewAI role-based reflects practitioner preference for API simplicity over control`
- Rule: cite the sources being interpreted
- Make the interpretation step clear (e.g., "inferring from 7 practitioner posts mentioning frustration with graph APIs")
- Distinguish from [Verified] by being transparent that this is synthesis, not direct evidence

### Placement & Formatting
1. **In entity/knowledge files:** place the label in brackets at the start of the paragraph or sentence
   - Example: `[Hypothesis] The core issue practitioners face is...`
2. **In social media posts:** include the label in the post or thread header
   - Example: "🔍 [Our Interpretation] The feedback pattern suggests..."
3. **In claims citing a source:** label immediately before the claim, link immediately after
   - Example: `[Verified] Multi-agent error amplification reaches 17.2× ([source: bag-of-agents-2026.md](link))`

### Review Before Publishing

**For GTM material, competitive analysis, and research claims:**
1. Identify substantive claims (competitor positioning, market trends, Loopsense performance claims, research findings)
2. For each substantive claim: verify it has either a source link OR one of the four certainty labels
3. If [Verified]: confirm the link works and supports the claim
4. If [Unverified]: ensure the claim is widely known enough to warrant mention without our own evidence
5. If [Hypothesis] or [Our Interpretation]: confirm the reasoning is sound and the sources are cited if applicable

**For normal documentation and product descriptions:**
- Ensure claims are accurate and evidence-backed (no speculation)
- No need for inline labels on standard product descriptions, design decisions, or procedural statements
- Apply labels only when uncertainty or interpretation is material to understanding

### Enforcement

- **In iteration 0:** GTM agent applies labels selectively to high-stakes claims before posting; Loopy applies to competitive/research content and GTM docs
- **In iteration 1+:** add a pre-publish checklist flagging substantive claims for label verification (not every factual statement)
- **In public review process:** public-account review (standing rule 8) includes checking that high-stakes claims are sourced or labeled, and that language is proportionate and evidence-backed

### Evolution

This standard applies to all public material from the release date forward. Private research, audit logs, and internal knowledge files do not require labels (they are evidence-gathering tools, not public claims).

When iterating on the standard itself, changes go through Loopy and Dan, recorded in standing-rules.md or this file.

