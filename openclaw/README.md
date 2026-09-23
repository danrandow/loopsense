# OpenClaw adapters

This directory contains the repository-owned OpenClaw adapter layer for LoopSense agents. The canonical agent methodologies remain under `agents/`; adapters identify an agent to OpenClaw and tell it how to load those canonical files.

For Loopy, use `openclaw/agents/loopy` as the agent workspace. The full LoopSense repository must be present in the same checkout so the adapter can resolve the repository root and read `agents/loopy/`, `knowledge/`, the active iteration YAML and other project evidence.

Version here:

- agent bootstrap instructions
- identity and behavioural guidance
- links to canonical product instructions

Keep outside Git:

- API keys, gateway tokens and credentials
- OpenClaw databases, sessions, memory and caches
- generated runtime state

Railway should clone the repository into persistent storage. Runtime configuration should point the Loopy agent workspace at `<repo>/openclaw/agents/loopy`; it should not copy these files into a separate, unversioned workspace.
