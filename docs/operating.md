# Operating LoopSense

How an iteration runs end to end, what triggers each step, and where it is allowed to stop. The
canonical specs are in `loopsense/workflows/` and each `agents/<role>/SKILL.md`. This doc is a
map of those specs and does not replace them.

## 1. The iteration lifecycle

```
                      "Loopy, start the next iteration"
                                     |
                                     v
   +-----------------------------------------------------------------+
   | PHASE A - prepare (read-only)                                   |
   |  read retro synthesis for M, current outputs                    |
   |  git preflight: clean tree + pull --ff-only                     |
   |  present ONE proposal: direction, retro fixes, carry-forward,   |
   |  intent, execution sequence                                     |
   +--------------------------------+--------------------------------+
                                    |
                        [ OWNER CHECKPOINT ]   <- nothing is written before an explicit yes
                                    |
   +--------------------------------v--------------------------------+
   | PHASE B - execute                                               |
   |  apply ONLY approved harness changes    -> commit "harness: .." |
   |  create iteration-N.yaml skeleton       -> commit "iteration N: |
   |                                            create approved      |
   |                                            skeleton"            |
   |  forward pass (below)                                           |
   +--------------------------------+--------------------------------+
                                    |
                                    v
                    iteration OPEN: evidence runs, flows update
                                    |
                           "Loopy, run the retro"
                                    |
                                    v
   +-----------------------------------------------------------------+
   | RETRO                                                           |
   |  each role writes retro-iterationN.md (<= half a page, about    |
   |  its own experience in the harness)                             |
   |  Loopy writes retro-synthesis-iterationN.md                     |
   |  NO recommendations are implemented here                        |
   +--------------------------------+--------------------------------+
                                    |
                                    v
                   next "start the next iteration" (loop)
```

Keep these four facts **separate**. Never let one stand in for another:

```
   workflow completed  !=  experiment ran  !=  hypothesis held  !=  iteration formally closed
```

Iteration 1 is the cautionary example: its workflow completed but its ten-post experiment never
ran.

## 2. The forward pass

Roles run **sequentially** in one checkout, and never two writing roles at once. Each role runs
in its own **visible, persistent, named session** (e.g. `Iteration 2 kickoff — PM`). Hidden
subagents are not acceptable for role work.

```
  for role in PM, Exec, Delivery, GTM:

     clean tree? --no--> STOP
        | yes
     git pull --ff-only --fail--> STOP
        |
     send trigger "start iteration N" + approved direction + retro pointer
        |
     role reads (canonical order) -> acts -> writes inside its boundary
        |
     verify: every changed path is inside the role's boundary
             YAML/JSON read-back, git diff --check, rule-8 scan if public
        |
     stage EXACT paths -> commit "iteration N: <Role> ..." -> pull --ff-only -> push
        |
     canonical outcome allows continuing? --no--> STOP and report
        | yes
     next role
```

### Stop conditions

| Situation | Result |
|---|---|
| PM decides **stop** or **pivot** | Keep PM's output and push it. Stop. |
| Exec **returns** the bet | Keep the return and push it. Stop. Do not invoke Delivery. |
| Delivery reports a missing certified input or an upstream blocker | Keep the output and push it. Stop. Do not invoke GTM. |
| GTM barred from an external action | It may still produce listening returns and pre-release drafts. Gates are never waived. |
| A role fails | Retry the same bounded task once. If it fails again, stop. Never impersonate the role. |
| Commit/push fails, or the pull can't fast-forward | Keep the working tree and report `git status --short`. Stop for the owner. |

## 3. Inside one role session

Every SKILL.md has the same session protocol:

```
  1. knowledge/standing-rules.md            (always first)
  2. the role's read order from SKILL.md    (registry, map guide, own knowledge,
                                             upstream entity, all return flows to it)
  3. State & inputs block in iteration-N.yaml (live facts + required inputs, dated)
  4. starting question                      e.g. PM: "Why are we still doing this?"
  5. act; write ONLY inside the write boundary
  6. set own entity overrides in iteration-N.yaml (label / notes / "Full entity: <path>")
  7. handoff check (rule 9): is what I ask of the next role executable NOW?
     If not, name the blockage.
```

The trigger phrases for each role:

| Trigger | Who | Effect |
|---|---|---|
| `start iteration N` | PM, Exec, Delivery, GTM | Role kickoff. PM needs the `iteration-N.yaml` skeleton to exist first. |
| `Loopy, start the next iteration` | Loopy | Runs `workflows/start-next-iteration.md` |
| `Loopy, run the retro` | Loopy | Runs `workflows/retro.md` on the highest `iteration-N.yaml` |

Casual discussion of a retro or an iteration is **not** a trigger.

## 4. Getting work into the world: the publishing gate

Only GTM publishes. Agent-authored public posts go through three stages
(`knowledge/social-agent-publishing-standard.md`):

```
  Stage 1 DRAFT                 Stage 2 HUMAN REVIEW               Stage 3 PUBLISH
  +------------------+          +---------------------+           +------------------+
  | GTM drafts post  |  ----->  | Dan or designated   |  approved | official platform|
  | + change note    |          | reviewer; logged    | --------> | APIs only        |
  | claims labelled  |          | with reason:        |           | URL -> publica-  |
  | [Verified] etc.  |          | safety-brand /      |           | tion-ledger.md   |
  +------------------+          | quality / none      |           +--------+---------+
                                +---------------------+                    |
                                                                           v
                                                         read metrics at 24h / 72h / 7d
                                                         one ledger row per post
```

This gate controls **exposure**. It does not grade quality. The number of overrides tagged
`quality` is the metric to watch. If it falls while outputs keep improving on world response,
that supports the thesis. If it does not fall, that counts against it.

Anything that names an identifiable public account or person also needs a **standing rule 8**
review before it merges to a public branch: self-check, a mechanical scan, and a
public-account review that records `pass` or `revise`.

## 5. The evidence loop: what "it worked" looks like

```
   pre-register verdict rule  ->  baseline phase (loop OFF)  ->  verdict phase (loop ON)
          (before data)             posts 1-5, no ledger          posts 6-10, each change
                                    reads acted on                note cites ledger rows
                                                                          |
                                                                          v
                                           compare phases; report the numbers AND the
                                           single posts that drive any difference
```

An iteration counts as moved only when:

- every return flow has a filed entry
- ledger rows exist for real outputs, and gaps are recorded as gaps, never estimated
- at least one change note cites rows, and the next output differs in the named way
- PM has updated the bet and can point to the rows that forced the update

If output changed but no rows were cited, **the loop did not run**. The agent just changed its
mind.

## 6. Owner authority, in short

The owner (Dan) approves: iteration direction and harness changes, public posting, account use,
spending, and anything consequential. Having access to a tool is **never** permission to use it.
Owner feedback goes to PM, and PM decides what reaches the team.
