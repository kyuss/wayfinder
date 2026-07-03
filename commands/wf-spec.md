---
description: Interactively refine one or more Linear tickets into implementation-ready specs (writes the spec back to each ticket's description). Run this BEFORE /wf-run.
argument-hint: <ticket-id> [ticket-id...]
allowed-tools: Task, Bash, Read, Edit, AskUserQuestion
---

# /wf-spec

Refine each ticket in `$ARGUMENTS` into a spec that carries enough information for the autonomous /wf-run workflow to go A→Z without further human input. This phase IS interactive — that's the point.

You are the orchestrator. Do not write specs or touch Linear yourself — delegate. Process tickets **one at a time** (the spec phase is a conversation; don't interleave).

**Up front (once):** if you're in a git repo, resolve the repo manual — first existing of `CONTEXT.md`, `CLAUDE.md`, `AGENTS.md` at the repo root — and call its absolute path `MANUAL` (else `MANUAL=none`; running `/wf-prime` first makes spec-building sharper). Pass `MANUAL` to wf-spec-builder for every ticket. If `MANUAL` has a `## Linear workflow` section, read its `Ready for Development` mapping into `READY_STATE` (else `READY_STATE = "Ready for Development"` and let `wf-linear` resolve it by synonym).

## Per ticket

1. **Fetch.** Spawn `wf-linear` with intent: `FETCH <identifier>`. Capture the returned identifier, title, current state, description, comments, and the `ATTACHMENTS` list.

2. **Ingest design handoffs (if any).** If `ATTACHMENTS` is not `none`, download each **promptly** — the signed hrefs expire ~5 min after the fetch. For each entry, run `~/.claude/bin/wf-fetch-handoff <handoff-dir> "<href>" <size-bytes>` where `<handoff-dir>` is a fresh scratch dir for this ticket (e.g. `$(mktemp -d)/<identifier>-handoff`). The helper validates the host/size, unpacks zips safely, and prints the unpacked path. Collect the printed paths as `HANDOFF` (a dir, or list of dirs/files). If the helper fails (expired link, etc.), note it and continue with `HANDOFF=none` — ingestion is best-effort and never blocks specing.

3. **Gather GitHub context.** Spawn `wf-github`: `PR_HISTORY <keywords from the ticket title/description>` → a digest of how related work was done/merged here.

4. **Refine (the interactive loop — you ask, not the subagent).** Spawn `wf-spec-builder`, passing the full fetched ticket content, the PR_HISTORY digest, `MANUAL`, **and** `HANDOFF` (the local path(s), or `none`). It explores the codebase and reads any handoff as **reference-only** visual/behavioral source of truth. **It cannot reach the user** (`AskUserQuestion` doesn't surface inside a subagent), so it returns one of two things, tagged on its first line:
   - **`STATUS: NEEDS_INPUT`** — followed by question blocks (`header` / `question` / `multiSelect` / `options`, recommended option marked). Put them to the user **yourself** via AskUserQuestion (you're the orchestrator — it works here): map each block to a question, options in the given order with the `(recommended)` one first and labeled "(Recommended)". Then **re-spawn `wf-spec-builder`** with the *same* inputs **plus** an `ANSWERS:` section pairing each question with the user's choice (verbatim, including any "Other" free-text). Repeat until it returns a spec. (Batches are normally 1–2 rounds; if it's still asking after ~3 rounds, surface that to the user and ask whether to push through with current defaults.)
   - **`STATUS: SPEC`** — the finished spec markdown. Strip the status line; this is what you persist. (A clear-enough ticket can return this on the first spawn with no questions — that's fine, not an error.)

5. **Persist.** Show the user the finished spec and confirm with one AskUserQuestion ("Write this spec to <identifier>'s description?" — Yes / Edit / Skip).
   - **Yes** → spawn `wf-linear` with intent `UPDATE_DESCRIPTION <identifier>` and the spec markdown as the new description. Once it confirms the write, spawn `wf-linear` again with intent `SET_STATUS <identifier> "<READY_STATE>"` to mark the ticket spec-ready for `/wf-run`. If the status transition returns `ERROR` (e.g. the team has no such state), surface it but treat the spec write as the success — don't undo it.
   - **Edit** → relay the user's tweaks back to `wf-spec-builder` (re-spawn with the prior spec + requested changes), then re-confirm.
   - **Skip** → leave the ticket unchanged; note it.

6. Status moves to **Ready for Development** only when the spec was written (step 5 → Yes). Tickets that were skipped — or edited but not yet written — keep their current status; don't transition them.

## After all tickets

Print a compact summary: each identifier → `spec written` / `skipped`, and remind the user they can now run `/wf-run <ids>`.

## Notes
- If `wf-linear` returns `ERROR`, surface it plainly and ask the user how to proceed — don't guess ticket data.
- Keep your own prose terse — your job in the loop is to relay the builder's questions to the user and its spec back. Don't editorialize the round-trip (no "the builder couldn't reach you, so…" narration); just ask the questions and move on.
