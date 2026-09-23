---
name: social-agent-publishing-standard
description: Governance and compliance standard for Loopsense agents posting to social platforms
iteration: 0
sources:
  - cowork
---

# Social Agent Publishing Standard

## Status
Established 2026-09-23. Required for all agent-authored posts to Twitter/X, LinkedIn, and similar public social platforms.

## Purpose
Loopsense agents will publish analysis, research, and positioning to social platforms. This standard ensures compliance with:
- **Anthropic's Claude API usage policy** (high-risk: automated journalistic content requires human review + AI disclosure)
- **Platform-specific automation policies** (X/Twitter, LinkedIn)
- **Standing rule 8** (evidence-backed, proportionate tone; no unjustified disrespect)
- **Claims-certainty standard** (all substantive claims sourced or labeled)

Prevents reputational and legal risk while maintaining agent autonomy and publishing velocity.

## Scope
Applies to any post authored or co-authored by Loopsense agents and published to:
- Twitter/X (timeline posts, threads, replies)
- LinkedIn (posts, articles)
- Other social platforms with similar automation policies

Does NOT apply to:
- Internal team communications or Slack
- Private research or draft documents
- User-generated content from external sources (retweets, shares, quotes)

## Pre-Publication Review Workflow

### Stage 1: Agent Drafting
Agent prepares post with:
- Substantive claim draft
- Source links (live URLs)
- Certainty labels where applicable ([Verified], [Hypothesis], etc.)
- Platform tag (X, LinkedIn, etc.)
- Metadata: agent name, timestamp, iteration

Post is queued in pending state. **No publication occurs until human approval.**

Example queued post:
```
PLATFORM: Twitter
AUTHOR: gtm-agent v2.1
TIMESTAMP: 2026-09-23T14:32:00Z

[Verified] Multi-agent error amplification can reach 17× under specific conditions
([source: Bag of Agents 2026 empirical study](https://link...))

This explains why single-agent systems often fail to catch compounding mistakes.
Our topology approach mitigates this through blameless feedback loops.

#AIAgents #AgenSystem
```

### Stage 2: Human Review (Required)
Designated reviewer (Delivery agent or Dan) performs pre-publication audit:

**Checklist:**
- [ ] **Sourcing & Certainty**
  - All factual claims have source link OR [Verified]/[Hypothesis]/[Unverified]/[Our Interpretation] label
  - Source links are live and current (test in preview)
  - No unsourced claims presented as fact
  
- [ ] **Standing Rule 8 Compliance** (Tone & Fairness)
  - No unjustified or disrespectful characterizations of named people/accounts
  - Criticism is evidence-backed and proportionate
  - Language addresses observable behavior/positioning, not character/motive
  - Example: ✓ "not building for knowledge work" vs ✗ "not a real builder"
  
- [ ] **Claims-Certainty Standard**
  - Substantive claims use appropriate certainty label
  - GTM/competitive claims prioritized for labeling
  - Hypothesis/interpretation claims clearly marked
  - Claim language matches certainty level
  
- [ ] **Platform Compliance**
  - **X/Twitter**: No trending-topic manipulation, no automated engagement automation
  - **LinkedIn**: Posting time randomized (not robotic pattern), mix with manual engagement
  - Post uses platform-native features (not bypassing official APIs)
  
- [ ] **Agent Disclosure**
  - Post or profile discloses agent involvement
  - Format: "Posted by Loopsense agent" or similar explicit disclosure
  - Links to governance docs (standing rules, claims standard)
  
- [ ] **Appropriateness**
  - Post aligns with Loopsense positioning and values
  - No controversial claims without strong evidence
  - Tone matches platform norms (X ≠ LinkedIn tone)
  - No misleading brevity or out-of-context claims
  
- [ ] **Technical Review**
  - Links are working and non-malicious
  - No accidental credential/email exposure
  - Image alt-text present if posting media
  - Character count fits platform

**Review Result:**
- ✓ **APPROVED**: Post moves to Stage 3 (Publication)
- 🔄 **REVISE**: Specific feedback provided; agent resubmits
- ✗ **REJECTED**: Post does not meet standard; guidance provided

Reviewer records: name, date, approval status, reasoning (logged in loopsense.log.json).

### Stage 3: Publication
Approved posts are published via official platform APIs:
- **X/Twitter**: Official Twitter API v2
- **LinkedIn**: Official LinkedIn Share API
- **No web automation or scrapers**

Published post metadata is recorded:
```json
{
  "id": "post-20260923-001",
  "platform": "twitter",
  "status": "published",
  "timestamp": "2026-09-23T14:35:00Z",
  "author": "gtm-agent",
  "reviewer": "dan",
  "review_date": "2026-09-23T14:33:00Z",
  "platform_url": "https://twitter.com/loopsense/status/...",
  "claims": [
    {
      "text": "Multi-agent error amplification can reach 17×",
      "certainty": "Verified",
      "source": "https://..."
    }
  ]
}
```

Post URL is added to loopsense.log.json history entry for audit trail.

## Platform-Specific Guidance

### Twitter/X

**Allowed:**
- Posts based on external data (research, metrics, market data)
- Threads with substantiated analysis
- Retweets with added commentary
- Engagement with followers (replies, mentions)

**Prohibited by X policy:**
- Automated posting about trending topics
- Trending-topic manipulation or coordinated pushing
- Non-API automation (scripting, web scraping)
- Unsolicited bulk Direct Messages
- Engagement automation (likes, follows) at scale

**Loopsense compliance:**
- Posts must use X API only; no web automation
- Randomize posting times (avoid 9am or noon sharp)
- No trending-topic posts without explicit non-manipulation review
- Disclose agent involvement in profile or post
- Threads should vary in structure/timing (not templated)

**Disclosure format (X):**
Profile: "Account managed by Loopsense agent system. See [governance](link)"
Or in post thread: "Thread by Loopsense agent. [Learn about our transparency](link)"

### LinkedIn

**Allowed:**
- Varying posting schedules (not robotic)
- Mix of automated posts + manual engagement
- Personalized content (not identical templates)
- Professional articles and thought leadership

**Prohibited by LinkedIn policy:**
- Identical generic posts from multiple accounts
- Robotic timing (same time daily)
- Acceptance rates <20% on connection requests
- Bulk messaging with templates
- Bulk outreach (>30 connections/day to cold contacts)

**Loopsense compliance:**
- Post at varying times (use randomization algorithm; 8am-6pm window, ±30 min random)
- Vary post structure and length (not identical templates)
- Mix agent posts with "manual" engagement (likes, comments, shares)
- Keep engagement authentic (don't engage with every post in feed)
- No bulk outreach or connection requests

**Disclosure format (LinkedIn):**
Profile: "This account is managed by the Loopsense agent system"
Or in post: "Authored by Loopsense agent research system"

## Claims Verification Checklist

Every social post must pass this verification before human review:

### Fact vs. Claim
**Fact**: Observable, verifiable information
- ✓ "LangGraph has 50K+ GitHub stars" → [Source: GitHub count as of 2026-09-23](link)

**Claim**: Interpretation, analysis, or hypothesis
- ✓ "[Hypothesis] Practitioners prefer API simplicity over low-level control" → cite evidence (N practitioner interviews, GitHub issue trends, etc.)

**Not a claim** (no label needed):
- "We chose YAML for configuration"
- "Topology-based architecture reduces error amplification"

### Sourcing Rules by Certainty Level

#### [Verified] — Source Linked, Direct Evidence
- Direct quote from primary source, or
- Metric/statistic from official account, or
- Published research with DOI/peer review
- **Rule**: Source link must support the claim exactly; no interpretation gap

Example:
```
[Verified] Multi-agent systems show error amplification under Byzantine failures
([source: Bag of Agents 2026 empirical study](https://arxiv.org/abs/...))
```

#### [Unverified] — Claim Circulates; We Haven't Checked
- Widely repeated claim in the market
- Source is "what we've seen cited" not "what we've verified"
- **Rule**: Use only when the claim is well-known enough to warrant mention

Example:
```
[Unverified] CrewAI's adoption rate is 10K+ monthly active users
(seen cited in recent posts; we haven't independently verified latest count)
```

#### [Hypothesis] — Our Working Assumption
- Our prediction about market/practitioners
- Not yet validated by evidence
- **Rule**: Mark as live hypothesis; update to [Verified] when evidence arrives

Example:
```
[Hypothesis] Knowledge-work practitioners will prioritize error auditability
over raw token throughput in 2026-2027
```

#### [Our Interpretation] — We're Synthesizing Data
- Combining multiple sources into conclusion
- Our read of raw data or trends
- **Rule**: Cite the sources being interpreted; show the synthesis

Example:
```
[Our Interpretation] The shift from code-first (LangGraph) to role-based (CrewAI)
reflects practitioner preference for simplicity over control
(inferring from 12 practitioner posts expressing API frustration, 
competitor positioning shifts, and GitHub issue sentiment analysis)
```

## Enforcement & Escalation

### Regular Compliance
- Each post reviewed before publication
- Reviewer approval recorded in metadata
- Non-compliant posts revised or rejected
- Feedback loop: reviewer notes guide agent training

### Escalation Path
1. **Minor issues** (formatting, typo, missing alt-text): Reviewer fixes, notifies agent
2. **Sourcing gaps** (missing link, weak evidence): Agent resubmits with sources
3. **Tone issues** (unclear disrespect, overstatement): Agent revises language
4. **Major violations** (unsourced claims, platform abuse, defamatory): Post rejected; Dan reviews with agent
5. **Repeated violations**: Agent publishing suspended pending Dan review

### Audit Trail
All decisions logged in loopsense.log.json:
```
{
  "id": 172,
  "status": "done",
  "timestamp": "2026-09-23T14:35:00Z",
  "actor": "dan",
  "action": "review_and_approve",
  "file": "social-posts/post-20260923-001",
  "record": "history/172.txt",
  "note": "Approved Twitter thread on error amplification. Sources verified; standing rule 8 passed; certainty labels applied."
}
```

## Evolution

This standard applies to all social posts from 2026-09-23 forward. Changes to the standard are:
- Proposed by Loopy or agents
- Reviewed by Dan
- Recorded in standing-rules.md or this file
- Logged in loopsense.log.json

### Iteration Roadmap
- **Iteration 0 (current)**: Manual human review for every post
- **Iteration 1**: Automated compliance flagging (agent pre-checks before human review)
- **Iteration 2**: Risk-based review (low-risk posts auto-approved; high-risk escalated)
- **Iteration 3**: Multi-reviewer consensus for high-stakes posts (competitive claims, statements about named parties)
