---
name: verification-gap
description: Stable concept — the core unsolved problem this product addresses; knowledge work agents have no automatic pass/fail
sources:
  - "AI Daily Brief, Sep 3 2026"
  - "Simon Willison on Lenny's Podcast, Apr 2026"
---

# The Verification Gap

**Named by**: AI Daily Brief, "Agentic Loops for Knowledge Workers" (Sep 3 2026)

> "Coders got verification for free. You have to manufacture the referee."

## The asymmetry

**Coding agents** have built-in verification: tests pass or they don't. The agent gets a signal. It can iterate against a ground truth without human intervention.

**Knowledge work agents** have no equivalent. A market analysis, a strategy bet, a product decision — there is no test suite. The agent cannot know whether its output is good without external input. Every knowledge work agent loop is, in principle, infinite and unanchored.

## Why this matters for multi-agent systems

In a multi-agent knowledge work system, the verification gap compounds. Without a referee:
- Agents tend toward confidence (they don't flag their own uncertainty)
- Each pass adds polish without adding correctness
- Agreement between agents is not evidence of quality — homogeneity failure

The manufactured referee is the response. Something that functions like a test suite for knowledge work outputs.

## The product-manager-bet response

The consideration mechanism in the Randow Maps topology is the proposed manufactured referee:
- Each agent reads a knowledge file that encodes what "good" looks like for their lens
- The Exec agent applies the viability lens — a structured set of questions that reject a bet if it doesn't meet criteria
- The GTM agent is explicitly tasked with finding counter-evidence, not confirmation

This is not a complete solution. It is an inspectable, improvable approximation of one.

## Status as of iteration 0

- Problem is named and publicly recognised (AI Daily Brief, Sep 2026)
- No production-ready solution exists ([[multi-agent-production-2026]])
- The product-manager-bet topology is a proposed partial solution
- Not yet validated with practitioners

## Related

- [[bag-of-agents-2026]] — what happens without structure
- [[multi-agent-production-2026]] — current production state
