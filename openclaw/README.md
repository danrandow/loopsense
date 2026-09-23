# OpenClaw adapters

This directory contains the repository-owned OpenClaw adapter layer for LoopSense agents. The canonical agent methodologies remain under `agents/`; adapters identify an agent to OpenClaw and tell it how to load those canonical files.

Use these directories as the OpenClaw agent workspaces:

- Loopy: `openclaw/agents/loopy`
- PM: `openclaw/agents/pm`
- Exec: `openclaw/agents/exec`
- Delivery: `openclaw/agents/delivery`
- GTM: `openclaw/agents/gtm`

The full LoopSense repository must be present in the same checkout so each adapter can resolve the repository root and read its canonical files under `agents/`, shared rules under `knowledge/`, the active iteration YAML and other project evidence.

Version here:

- agent bootstrap instructions
- identity and behavioural guidance
- links to canonical product instructions

Keep outside Git:

- API keys, gateway tokens and credentials
- OpenClaw databases, sessions, memory and caches
- generated runtime state

Railway should clone the repository into persistent storage. Runtime configuration should point each agent at its adapter directory and set its working directory to `<repo>`; it should not copy these files into a separate, unversioned workspace. Set `agents.defaults.skipBootstrap` to `true` so OpenClaw does not recreate generic workspace instructions above the repository.
