# GTM listening tooling — runtime-neutral wording

## Context

`agents/gtm/SKILL.md` told GTM to search X "through Claude in Chrome", a capability of a different runtime. On this runtime every scheduled listening cycle fell back to ad-hoc browser access with degraded results (GTM iteration-1 retro). The owner agreed the correction was necessary but required the canonical instruction to stay runtime-neutral, with runtime-specific guidance in the runtime's adapter.

## Decision

Dan approved on 2026-09-24: the canonical listening step now reads "Search X using the web search and browsing tools your runtime provides" (term list unchanged), and the concrete tool mapping (`web_search` plus the `browser` tool) lives only in `openclaw/agents/gtm/AGENTS.md`, with a fallback rule to record a tooling gap in the run note rather than silently changing research channel.

## Why

The canonical skill must remain portable across runtimes; concrete tool names belong in the runtime's adapter. Recording gaps keeps degraded cycles visible instead of invisible.

## Consequences

`agents/gtm/SKILL.md` and `openclaw/agents/gtm/AGENTS.md` updated. Out of date: any reading that binds GTM's listening to "Claude in Chrome" or to any named tool in the canonical skill.
