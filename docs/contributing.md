# Contributing

Changing LoopSense means changing files that agents treat as instructions. A careless edit
behaves like a bug, so the discipline here plays the role a type checker and CI would play in a
normal codebase.

## 1. Who may write where

| Path (under `loopsense/`) | PM | Exec | Delivery | GTM | Loopy | Owner |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `agents/<own role>/generates/`, `knowledge/`, `research/` | own | own | own | own | own* | yes |
| another role's folder | - | - | - | - | approval | yes |
| `iteration-N.yaml`, own entity entries only | yes | yes | yes | yes | approval | yes |
| `base.yaml`, `moonshot.yaml` | - | - | - | - | approval | yes |
| `knowledge/` (rules, registry, policy) | - | - | - | - | approval | yes |
| `agents/*/SKILL.md`, `workflows/` | - | - | - | - | approval | yes |
| `decisions/` | own decisions | - | - | - | yes | yes |
| `history/`, `loopsense.log.json` | **never** | **never** | **never** | **never** | **never** | **never** |
| frozen `*-v<N>.md` from a closed iteration | **never**: write `v<N+1>` | | | | | |

`*` Loopy writes freely only to `agents/loopy/knowledge/working-context.md`, `research/` and
`returns/`. "approval" means Dan approved **that specific change** in the current conversation:
draft first, write on approval, every time.

Each SKILL.md lists its role's exact boundary. That list is the authority, and the table above
is a summary.

## 2. The change pipeline

This comes from `knowledge/audit-policy.md`. Git is the audit trail, so there are no separate
change logs.

```
  +-----------+   +-----------+   +------------+   +-------------+   +-----------+   +--------+
  | PREFLIGHT |-->|   EDIT    |-->|  VALIDATE  |-->| STAGE EXACT |-->|  COMMIT   |-->|  SYNC  |
  +-----------+   +-----------+   +------------+   +-------------+   +-----------+   +--------+
   status clean    targeted,       diff --check     git add <path>    what + why     pull --ff-only
   pull --ff-only  inside your     YAML/JSON        NEVER -A or .     in message     push (never -f)
   (else STOP)     boundary,       read-back                                          HEAD==origin
                   read back       rule-8 scan                                        status clean
```

Hard rules:

- One commit per coherent change. The message says **what** changed and **why**.
- Never stash, reset, rebase, merge, amend pushed commits or force-push to get unblocked.
  Stop and report instead.
- Do not make a bookkeeping commit that records a previous commit's hash.
- Do not claim a change is stored remotely until the push has succeeded.

Commit message conventions used by the workflows:

```
harness: apply iteration N retro improvements
iteration N: create approved skeleton
iteration N: PM kickoff | Exec review | Delivery pass | GTM pass
retro: complete iteration N retrospective     (or: save partial ...)
map: <change>          loopy: <change>        (seen in history)
```

## 3. Validation snippets

Run these from the repo root. `python3` + PyYAML and `node` are the only dependencies.

**Parse every map file and lint the base map** (label limits and dangling edges):

```bash
python3 - <<'EOF'
import yaml, glob
for f in sorted(glob.glob('loopsense/*.yaml')):
    yaml.safe_load(open(f)); print('ok', f)
b = yaml.safe_load(open('loopsense/base.yaml'))
for k in ('actors', 'actions'):
    for x in b[k]:
        if len(x['label']) > 25: print('LABEL TOO LONG', k, x['id'], x['label'])
nodes = {e['id'] for e in b['entities']} | {a['id'] for a in b['actions']}
for e in b['edges']:
    for end in (e['from'], e['to']):
        if end not in nodes: print('DANGLING EDGE', e['id'], end)
EOF
```

**JSON** (only if you touched a JSON file; note that the legacy log must never change):

```bash
node -e 'JSON.parse(require("fs").readFileSync(process.argv[1]))' path/to/file.json
```

**Whitespace and conflict markers:**

```bash
git diff --check
```

**Rule-8 mechanical scan** of changed Markdown/YAML. A match means *review it*, not that
something is wrong:

```bash
git diff --name-only -- '*.md' '*.yaml' | xargs grep -nEi \
  '@[A-Za-z0-9_]{2,}|https?://(x|twitter|linkedin)\.com/|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}|\+?[0-9][0-9 ()-]{8,}[0-9]'
```

**Privacy:** the repo is public. Never commit credentials, private contact details, runtime
state or session transcripts. `.gitignore` already excludes agent memory and dream files.

## 4. Common changes

### Add or rename a role

```
  1. base.yaml         add actorN + actionN; add generates/used-by edges for its entities
  2. team-registry.md  add a column: IDs, skill file, folders, generates/consumes
                       + rows in the entity file-location table
  3. agents/<role>/    SKILL.md (session protocol, write boundary, read order,
                       trigger, starting question), project-instructions.md stub,
                       knowledge/, generates/
  4. openclaw/agents/<role>/   AGENTS.md, IDENTITY.md, SOUL.md, USER.md (see runtime.md)
  5. workflows/*.md    add the role to the sequential invocation order
  6. decisions/        record it: this is a material harness change
```

### Add a flow (entity)

1. Add the entity to `base.yaml` with `direction: return` if it flows upstream.
2. Add both a `generates` edge (action -> entity) and a `used by` edge (entity -> action).
3. Add a row to the path table in `team-registry.md`.
4. Add the file path to the producer's SKILL.md write boundary, and to the consumer's read
   order.
5. If it is a return, write it **for its reader**: feedback packaged in a form that specific
   actor can act on.

### Change a rule or a skill

This is a material change, so it needs owner approval plus a decision record in `decisions/`
(Context / Decision / Why / Consequences). Team-wide rules go in `knowledge/standing-rules.md`,
never into per-project instructions.

## 5. Gotchas

- **Paths are relative to `loopsense/`**, not the repo root. Adapters resolve it as
  `$(git rev-parse --show-toplevel)/loopsense`.
- **Ignore `context.md`.** Some global instructions mention it. It is not part of this project
  (standing rule 1).
- **`history/` + `loopsense.log.json`** are evidence of what people believed at the time. They
  are not current instructions. Some agent notes cite log IDs such as "log 184"; those point
  into this frozen ledger.
- **Stale references exist.** Frozen outputs and Loopy's working context still mention retired
  paths such as `near-term-experiment.yaml` and `knowledge/pm-v0.md`. Check that a file exists
  before following a pointer.
- **Unquoted colons** in YAML labels break parsing.
- **Duplicating content** is a defect. Entity descriptions live in `base.yaml`, content lives
  in `generates/`, and everything else should link to them.
- `agents/practitioners/` and `agents/gtm/knowledge/signal-ledger-v0.md` are specified but do
  not exist yet.
