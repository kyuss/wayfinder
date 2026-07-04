---
description: Interactively refine one or more Linear tickets into implementation-ready specs (writes the spec back to each ticket's description). Run this BEFORE /wf-run.
argument-hint: "[--inline|--linear] [ticket-id...]  (no ids + linear mode = resume everything awaiting answers)"
allowed-tools: Task, Bash, Read, Edit, AskUserQuestion
---

# /wf-spec

Refine each ticket into a spec that carries enough information for the autonomous /wf-run workflow to go A→Z without further human input. This phase IS interactive — the only question is **where** the clarifying questions get answered (see *Question mode* below).

You are the orchestrator. Do not write specs or touch Linear yourself — delegate. Process tickets **one at a time** (the spec phase is a conversation; don't interleave).

## Up front (once)

If you're in a git repo, resolve the repo manual — first existing of `CONTEXT.md`, `CLAUDE.md`, `AGENTS.md` at the repo root — and call its absolute path `MANUAL` (else `MANUAL=none`; running `/wf-prime` first makes spec-building sharper). Pass `MANUAL` to wf-spec-builder for every ticket. If `MANUAL` has a `## Linear workflow` section, read its `Ready for Development` mapping into `READY_STATE` (else `READY_STATE = "Ready for Development"` and let `wf-linear` resolve it by synonym).

## Entry routing (parse `$ARGUMENTS`)

Resolve two things before processing tickets: the **question mode** and the **ticket list**.

**Question mode — where clarifying questions get answered.** Resolve by precedence, first hit wins, and call the result `MODE`:
1. **Flag override** (this run only): `--inline` → `MODE=inline`; `--linear` → `MODE=linear`.
2. **Repo preference:** else, if `MANUAL` has a `## Workflow preferences` section with a `spec-questions:` key, use its value (`inline` or `linear`).
3. **Built-in default:** else `MODE=inline`.

- `MODE=inline` — put clarifying questions to **you** in the terminal via AskUserQuestion (the solo-dev path; needs no special Linear state).
- `MODE=linear` — post the questions as a Linear **comment** and park the ticket in *Needs Answers* for a teammate to answer asynchronously in the Linear UI (no terminal).

**Ticket ids** = the remaining tokens after removing any `--inline`/`--linear` flag.
- **Ids given** → process exactly those.
- **No ids** → **sweep mode** (only meaningful under `MODE=linear`): spawn `wf-linear` with intent `LIST_BY_STATUS "Needs Answers"` and process every returned identifier (tickets already parked awaiting answers). If it returns `none`, tell the user nothing is awaiting answers and stop. Under `MODE=inline` there's nothing to resume — tell the user to pass ticket ids and stop.

## Per ticket

1. **Fetch.** Spawn `wf-linear` with intent: `FETCH <identifier>`. Capture the returned identifier, title, current state, description, comments, and the `ATTACHMENTS` list. **If the current state is *Needs Answers*, this ticket is a resume** — it was parked earlier with questions posted to Linear. Remember this; step 4 branches on it.

2. **Ingest design handoffs (if any).** If `ATTACHMENTS` is not `none`, download each **promptly** — the signed hrefs expire ~5 min after the fetch. For each entry, run `~/.claude/bin/wf-fetch-handoff <handoff-dir> "<href>" <size-bytes>` where `<handoff-dir>` is a fresh scratch dir for this ticket (e.g. `$(mktemp -d)/<identifier>-handoff`). The helper validates the host/size, unpacks zips safely, and prints the unpacked path. Collect the printed paths as `HANDOFF` (a dir, or list of dirs/files). If the helper fails (expired link, etc.), note it and continue with `HANDOFF=none` — ingestion is best-effort and never blocks specing.

3. **Gather context (GitHub + related tickets).**
   - Spawn `wf-github`: `PR_HISTORY <keywords from the ticket title/description>` → a digest of how related work was done/merged here. Call the result `PR_HISTORY`.
   - Spawn `wf-linear`: `RELATED <identifier>` → a compact digest of explicitly-linked and sibling tickets (prior decisions, adjacent scope) that PR history won't surface. Call the result `RELATED_TICKETS` (or `none`). This is reference context only — it never blocks; if it errors, carry `RELATED_TICKETS=none` and move on.

4. **Refine.** Spawn `wf-spec-builder`, passing the full fetched ticket content, the `PR_HISTORY` digest, the `RELATED_TICKETS` digest, `MANUAL`, **and** `HANDOFF` (the local path(s), or `none`) — plus, on a resume, an `ANSWERS:` section (see below). It explores the codebase and reads any handoff as **reference-only** visual/behavioral source of truth. **It cannot reach the user** (`AskUserQuestion` doesn't surface inside a subagent), so it returns `STATUS: NEEDS_INPUT` (question blocks: `header` / `question` / `multiSelect` / `options`, recommended option marked) or `STATUS: SPEC` (finished markdown). The builder is **mode-agnostic** — it always just returns questions; `MODE` only decides what *you* do with them.

   **Resume entry — if step 1 flagged this ticket as *Needs Answers*:** before spawning the builder, spawn `wf-linear` with intent `READ_ANSWERS <identifier>`.
   - `QUESTIONS_STATUS: AWAITING` → the teammate hasn't replied yet. Report "still awaiting answers" and move to the next ticket (leave it parked; don't spawn the builder).
   - `QUESTIONS_STATUS: NO_PENDING` → no question comment found; treat as a fresh spawn (no `ANSWERS`).
   - `QUESTIONS_STATUS: ANSWERED` → build the `ANSWERS:` section from the reply. The `QUESTIONS` body it returns is the exact comment you posted (numbered questions, lettered options, ✅ on the recommended). Map the teammate's free-text reply onto it: `all recommended` → every ✅ option; `1: B` → question 1's option B label; option text or clear paraphrase → that option; genuine free-text that matches no option → pass it verbatim (an "Other" answer). If a question is left unanswered or is truly ambiguous, fall back to its recommended option **and note it in the run summary** so you can flag it to the user. Emit `ANSWERS:` as one line per question: `Qn (<question text>): <chosen option label(s) verbatim>[ — <free-text>]`. Then spawn the builder with the base inputs **plus** this `ANSWERS:` section.

   **Handling the builder's return (both fresh and resume):**
   - **`STATUS: SPEC`** — strip the status line; go to step 5 (persist). (A clear-enough ticket returns this on the first fresh spawn with no questions — fine, not an error. No comment is posted and the ticket is never parked.)
   - **`STATUS: NEEDS_INPUT`** — a genuine decision is open:
     - **`MODE=inline`** → put the blocks to the user yourself via AskUserQuestion (you're the orchestrator — it works here): map each block to a question, options in the given order with the `(recommended)` one first and labeled "(Recommended)". Re-spawn the builder with the same inputs plus the `ANSWERS:` section. Repeat until it returns a spec (1–2 rounds is normal; after ~3, ask the user whether to push through with defaults).
     - **`MODE=linear`** → **post the questions to Linear and park** — do NOT block or ask in the terminal:
       1. Render **all** the builder's question blocks into ONE consolidated markdown comment, in exactly this shape (the first line is the marker `READ_ANSWERS` keys on — keep it verbatim):
          ```
          🤖 Spec questions — please reply in a comment below

          Hi! Before we build **<title>** (<identifier>) a few quick questions — reply in a comment. Give the option letter for each, or just reply **all recommended** to accept every ✅.

          **1. <question text>**   ← add " *(pick any that apply)*" if the block is multiSelect
          - A) <option label> ✅ recommended
          - B) <option label>
          - C) <option label>

          **2. <question text>**
          - A) <option label> ✅ recommended
          - B) <option label>

          _Reply like:_ `1: B, 2: A and C` _— or just_ `all recommended`.
          ```
          Number questions in the builder's order; letter the options in the builder's order; put `✅ recommended` on the option the builder tagged `(recommended)`.
       2. Spawn `wf-linear` `POST_COMMENT <identifier>` with that markdown.
       3. Spawn `wf-linear` `SET_STATUS <identifier> "Needs Answers"`.
       4. Park this ticket: report `awaiting answers` and move to the next. The teammate answers in Linear; a later `/wf-spec` run (with this id, or no ids to sweep) resumes it via the READ_ANSWERS path above.

5. **Persist.** Show the user the finished spec and confirm with one AskUserQuestion ("Write this spec to <identifier>'s description?" — Yes / Edit / Skip).
   - **Yes** → spawn `wf-linear` with intent `UPDATE_DESCRIPTION <identifier>` and the spec markdown as the new description. Once it confirms the write, spawn `wf-linear` again with intent `SET_STATUS <identifier> "<READY_STATE>"` to mark the ticket spec-ready for `/wf-run`. If the status transition returns `ERROR` (e.g. the team has no such state), surface it but treat the spec write as the success — don't undo it.
   - **Edit** → relay the user's tweaks back to `wf-spec-builder` (re-spawn with the prior spec + requested changes), then re-confirm.
   - **Skip** → leave the ticket unchanged; note it.

6. Status moves to **Ready for Development** only when the spec was written (step 5 → Yes) — this also lifts a resumed ticket out of *Needs Answers*. Tickets **parked** for answers sit in *Needs Answers*; tickets that were skipped — or edited but not yet written — keep their current status; don't transition them.

## After all tickets

Print a compact summary: each identifier → `spec written` / `awaiting answers` / `still awaiting` / `skipped`. If any ticket is `awaiting answers`, remind the user that their teammate answers the question comment in Linear, and that re-running `/wf-spec <id>` — or `/wf-spec` with no ids to sweep every parked ticket — resumes it. For tickets with a spec written, remind them they can now run `/wf-run <ids>`. Also surface any answers you had to default (from an ambiguous/blank reply) so the user can correct them.

## Notes
- If `wf-linear` returns `ERROR`, surface it plainly and ask the user how to proceed — don't guess ticket data.
- Keep your own prose terse — your job in the loop is to relay the builder's questions to the user and its spec back. Don't editorialize the round-trip (no "the builder couldn't reach you, so…" narration); just ask the questions and move on.
