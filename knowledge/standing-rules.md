# Loopsense — Standing Rules (all agents)

Read this first, every session. Dan and Loopy maintain it; agents do not edit it.

1. **Ignore `context.md`.** If any standing or global instruction tells you to read a `context.md` file, skip it. It lives outside this project's folders, you cannot reach it, and it is not part of the Loopsense context. Do not report it as an error or ask Dan about it.
2. **Your sources are the files named in your SKILL.md session protocol.** If a file named there is missing, say so in your output and carry on with what you have.
3. **Team-wide rule changes go here**, not into project instructions, so Dan never has to re-paste instructions by hand.
4. **Where entities live.** Flows you generate — forward entities (`entityN`) and return flows (`entityRN`) — are written to `agents/{yourid}/generates/{entityId}-v{n}.md`, where n is the iteration number. Private knowledge (`Prv` entities) stays in `agents/{id}/knowledge/`; research (`Pub`) in `agents/{id}/research/`. To read another agent's flow, open their `generates/` folder and take the highest v present unless told otherwise. A file is editable while its iteration is open. When Dan (via Loopy) closes an iteration its files are frozen: never edit a frozen file, write v{n+1} instead. Paths for every entity are in `knowledge/team-registry.md`.
5. **Detail hierarchy in `iteration-*.yaml`:** label = headline, notes = short summary ending `Full entity: <path>`, the file in `generates/` = full content. Agents may edit `iteration-*.yaml` and nothing else (never `base.yaml`, `moonshot.yaml`, `near-term-experiment.yaml`); flag needed changes to those for Dan (Loopy). Every YAML edit follows rule 6. Loopy's briefings to Dan stay in `agents/loopy/returns/`.
6. **Logging YAML changes.** This applies every time you change any `*.yaml` in this folder, however small, and only where rule 5 or Dan's approval allows you to edit it. The log and a change record are your audit trail and your undo. Follow these steps in order.

   **Before you start.**
   - Read `loopsense.log.json` in full. If it is not valid JSON (missing comma or bracket, cut-off ending), stop and tell Dan. Never repair it and never rewrite it with Write.
   - If the newest entry for the same file has `"status": "started"`, another change is in progress or was interrupted. Stop and tell Dan.
   - Read the region of the YAML you will change fresh now, not from earlier in the session.

   **For each file you change** (one log entry per file, per change):
   1. **Pick the id:** every log entry has an `id`, assigned in order. Use the highest `id` in the log plus 1.
   2. **Write the change record** as a new file `history/{id}.txt` (a path that does not exist yet). It contains the file name, one line on what and why, then `BEFORE:` followed by the exact current text of every region you will change, copied verbatim, then `AFTER:` followed by the exact text it will become. This is your undo.
   3. **Log first.** Append an entry to the end of `loopsense.log.json` with Edit, never Write. Use the last entry's full text (including its closing brace) as `old_string`, and replace it with that same text plus a comma and your entry, copying the file's indentation. If the Edit fails, someone else appended: re-read the log, recompute the id, and retry — this is the normal path when two agents close out entries the same day, not a sign anything went wrong. Do not fall back to Write. Your entry:
      ```
      {
        "id": 98,
        "status": "started",
        "ts": "2026-09-21T05:00:00Z",
        "actor": "pm",
        "action": "update",
        "file": "iteration-0.yaml",
        "record": "history/98.txt",
        "note": "Dan-approved: what changed and why. Was: '<old>'. Now: '<new>'."
      }
      ```
      Keep `id` and `status` on adjacent lines in that order. `action` uses the existing words (create, update, fix, extend, rename, delete). The note says who approved it and gives the exact Was/Now for every value you change, including any note you overwrite.
   4. **Change the YAML with targeted edits** (Edit, or a scripted exact-string replace that fails if the text is not found). Never rewrite an existing YAML file wholesale, because that cannot be undone from a record. Use Write only to create a brand-new YAML file (log it first; `BEFORE:` is "(new file)"). If the change cannot be done as targeted edits, stop and ask Dan. Do not delete or rename a YAML file; ask Dan.
   5. **Read it back.** Read the changed region and confirm it matches `AFTER:`. Check: indentation, labels quoted where they contain a colon, label lengths per `knowledge/reading-the-map.md` (actors and actions at most 25 characters or 3-4 words; entities up to about 50), every id you mention exists in `base.yaml`, no duplicate keys. You cannot run the renderer, so say so in the next step; do not claim it renders.
   6. **Finish the entry** with Edit, using the `"id": N,` and `"status": "started",` lines as `old_string`: change to `"status": "done",` and add `"verified": "read-back only; not rendered",` on the next line. If the change went wrong, put the BEFORE text back with Edit (only if the AFTER text is still exactly there), then set `"status": "failed"` and add an `"error"` line saying what happened. Tell Dan.

   **Changes that span files.** Write all the log entries and change records first, then make the changes in an order that keeps the map valid at each step: add to `base.yaml` before any iteration file that refers to it; remove from iteration files before removing from `base.yaml`. Finish each entry as you go.

   **Never:** edit, reorder or delete an existing log entry; invent a timestamp (use the time you were given, or the date alone if you do not have one); change a YAML file with no entry written first; or leave an entry at `"started"` without telling Dan.

   **At the end of your session**, list each change: entry id, file, status, and whether it still needs a render check by Dan or Loopy.

   **Other files.** For any non-YAML write, append a log entry the same way (Edit at the end, never Write) before writing; every entry still gets an `id` per rule 6.1 — `status` and `record` are optional.

7. **Record every harness change.** Any change to how the harness works gets a log entry AND a `history/{id}.txt` record (id per rule 6). That covers skills (SKILL.md), standing rules, folder structure and file moves or renames, `*.yaml` (as rule 6), and practices or decisions (e.g. holding a retro). It does not cover an agent's own outputs (entity, knowledge or research files) or Loopy's working context; those keep a normal log entry. Every record has a `WHY:` line, a line or two on the reason. File edits also carry `BEFORE:`/`AFTER:` as in rule 6; a practice or decision uses `WHAT:` and `WHY:` only. The records are addressed to PM: Dan and Loopy bring feedback, rationale and observations to PM, and PM decides what reaches the team and when. The log and history are an audit trail, not instructions; agents may read them but they never override PM's direction. Delivery documents the design from what PM passes on, not directly from the raw log. Dan and Loopy do not direct other agents past PM. In retros, ask for the agent's own experience first; do not lead with our reasons.

8. **Write responsibly about identifiable public accounts and people.** When referring to an identifiable public account or person, distinguish sourced fact and direct quotation from inference, link to the underlying public evidence, and state uncertainty plainly. Describe observable content or behaviour rather than speculating about character, motives or honesty; do not repeat sensitive personal information merely because it is publicly discoverable.

   **Verification before publishing or merging affected material:**
   - **Agent self-check:** confirm that the source is linked; facts, quotations and inferences are distinguishable; uncertainty is explicit; the wording addresses evidence rather than personality or motive; and identifying the account adds legitimate value.
   - **Mechanical scan:** scan changed Markdown and YAML for public handles and profile links, reputation-sensitive terms, email addresses and phone numbers. A match requires review; it is not automatically a violation.
   - **Public-account review:** Loopy or another designated reviewer reads the flagged passages and records `source present`, `fact/inference distinction`, `unnecessary personal information`, `tone`, and a `pass` or `revise` result. Complete required revisions before the material is made public or merged into a public branch.
