# Draft proposal — GTM tooling wording split (retro item 6)

**Status:** DRAFT for Dan's review. Not implemented. Responds to owner instruction 2026-09-23:
the GTM tooling correction is necessary, but the canonical instruction must remain
runtime-neutral; runtime-specific OpenClaw guidance belongs in the OpenClaw adapter.

## The problem

`agents/gtm/SKILL.md` scheduled listening cycle step 3 says "Search X through Claude in Chrome" —
a Claude Code CLI capability. GTM's iteration-1 retro reported that this runtime (OpenClaw) has
no such capability, so listening cycles fell back to whatever browser access happened to be
available that day, with inconsistent results. The fix must not simply swap one runtime's name
for another's in the canonical skill.

## Proposed canonical wording (`agents/gtm/SKILL.md`, runtime-neutral)

Step 3 currently begins:

> 3. Search X through Claude in Chrome for each term: ...

Proposed replacement (term list unchanged):

> 3. Search X using the web search and browsing tools your runtime provides for each term: ...

Nothing else in the step changes. The canonical skill names no runtime, no vendor and no tool.

## Proposed OpenClaw-adapter wording (`openclaw/agents/gtm/AGENTS.md`, runtime-specific)

New bullet for the adapter's "Operating safeguards" (or its own short section):

> **Listening tooling.** "Claude in Chrome" in the canonical skill means: use `web_search` for
> the term sweeps and the `browser` tool for opening result threads and capturing verbatims with
> URLs. If neither is available in a session, record the gap in the run note rather than
> substituting a different research channel silently.

This is the only place the concrete tool names appear; the canonical instruction stays portable
to any runtime with search and browse capability.

## Not implemented

Per the owner's instruction, both wordings are returned for approval only. On approval: the
canonical edit to `agents/gtm/SKILL.md` is a rule-7 harness change (log entry + history record);
the adapter edit to `openclaw/agents/gtm/AGENTS.md` likewise.
