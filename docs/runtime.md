# Runtime and harness

LoopSense is **runtime-neutral**. The workflows define *what* must happen: role boundaries,
gates, outputs and stop conditions. A harness decides *how* roles are invoked, whether as chat
projects, subagents, API calls, scheduled jobs or a human copy-pasting between tabs.

## 1. The harness contract

Any runtime that runs the included workflows must be able to do all of the following:

```
  [x] give Loopy access to the repository
  [x] invoke PM / Exec / Delivery / GTM as ISOLATED contexts, each loading its
      canonical agents/<role>/SKILL.md
  [x] return each role's result to Loopy
  [x] run roles sequentially when they share a checkout
  [x] preserve each role's write boundary
  [x] git status / pull / commit / push when an owner-invoked workflow authorises it
  [x] stop safely on dirty state, conflicts, missing authority or failed agents
  [x] keep role sessions VISIBLE and PERSISTENT (named, grouped per iteration)
```

If the runtime cannot provide one of these, Loopy stops and names the missing capability. It
must never impersonate a role.

## 2. Layering

```
  +-------------------------------------------------------------+
  |  RUNTIME (OpenClaw on Railway, Claude projects, your own)   |   not versioned:
  |  sessions, memory, API keys, gateway tokens, databases      |   secrets + state
  +------------------------------+------------------------------+
                                 |
  +------------------------------v------------------------------+
  |  ADAPTER  loopsense/openclaw/agents/<role>/                 |   versioned, thin:
  |   AGENTS.md    bootstrap: resolve source root, read rules,  |   "who am I and
  |                read SKILL.md, read active iteration YAML    |    what do I load"
  |   IDENTITY.md  SOUL.md  USER.md   identity + behaviour      |
  +------------------------------+------------------------------+
                                 |
  +------------------------------v------------------------------+
  |  CANONICAL  loopsense/agents/<role>/SKILL.md                |   versioned, owns
  |             loopsense/knowledge/  loopsense/workflows/      |   ALL behaviour
  +-------------------------------------------------------------+
```

Adapters **point at** canonical files. They never redefine workflows or boundaries. If you are
tempted to put behaviour in an adapter, put it in the SKILL.md.

## 3. OpenClaw deployment shape

```
   Railway persistent volume
   `-- <repo>/                          full git checkout (cloned, not copied)
       `-- loopsense/
           |-- openclaw/agents/loopy     <- workspace for agent "loopy"
           |-- openclaw/agents/pm        <- workspace for agent "pm"
           |-- openclaw/agents/exec      <- workspace for agent "exec"
           |-- openclaw/agents/delivery  <- workspace for agent "delivery"
           `-- openclaw/agents/gtm       <- workspace for agent "gtm"

   per agent:  workspace = its adapter dir
               working directory = <repo>
   global:     agents.defaults.skipBootstrap = true
               (stops OpenClaw from writing generic workspace instructions over the repo)
```

The adapter bootstrap (e.g. `openclaw/agents/pm/AGENTS.md`) does this on every session:

```
  1. SOURCE_ROOT = $(git rev-parse --show-toplevel)/loopsense
  2. read knowledge/standing-rules.md
  3. read agents/<role>/SKILL.md          (boundary, read order, handoff wording)
  4. read agents/<role>/project-instructions.md + active iteration-N.yaml
  5. read the files the skill requires, THEN analyse or write
```

Kept out of git by `.gitignore`: `.openclaw/`, `openclaw-state/`, `loopsense/openclaw/**/memory/`,
`MEMORY.md`, `DREAMS.md`, `*.db`, `*.sqlite*`, `.env*`, keys and certificates.

## 4. Running without a platform

The minimum setup is one chat or coding-agent session per role, with file access to a clone:

```
  session "Iteration N kickoff — PM"
     context:  loopsense/agents/pm/SKILL.md + knowledge/standing-rules.md
     prompt:   "start iteration N"  (+ owner direction, retro synthesis pointer)
     output:   agents/pm/generates/entity0-vN.md, pm.md log, iteration-N.yaml entries
  -> commit, then open the Exec session with the same pattern
```

`agents/<role>/project-instructions.md` is the short stub you paste into a Claude project (or
equivalent). The real protocol lives in the SKILL.md, so the stub never needs re-pasting when a
rule changes.

## 5. Known runtime constraints (as of 2026-09-29)

- From the headless cloud environment, x.com returns HTTP 403. That blocks GTM's X listening
  and per-post metric capture. Non-X findings are never reported as X evidence.
- Publishing must go through official platform APIs only (Stage 3 of the publishing standard).
- Operational failures, retries and aborted runs are recorded in the runtime's own task and
  session logs, not in git.
