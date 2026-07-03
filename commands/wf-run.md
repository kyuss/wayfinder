---
description: Run the autonomous agent workflow for one or more Linear tickets — each in its own git worktree, from In Progress to an open GitHub PR (In Review). Never merges, never sets Done. Add --parallel to run independent tickets concurrently.
argument-hint: <ticket-id> [ticket-id...] [--parallel]
allowed-tools: Task, Bash, Read, Edit, AskUserQuestion
---

# /wf-run

Drive each ticket in `$ARGUMENTS` from a spec'd Linear ticket to a GitHub PR that is ready for review. You are the orchestrator: you own git/worktree/`gh` mechanics and you sequence the agents. Agents do the thinking; `wf-linear` owns every Linear call.

**Hard boundaries (never cross):**
- The workflow ENDS when the PR is open and the ticket is **In Review**. You do **not** merge, you do **not** wait for checks, you do **not** set **Done**. Marking Done + worktree cleanup happen only later, when the user explicitly tells you a PR was merged (see "On merge" below).
- Follow `~/.claude/CLAUDE.md` throughout (simplicity, surgical changes, goal-driven verification).

## Preconditions

Run once, up front. **Fail fast here** — every check below is cheap; do them all before touching any ticket, so the workflow never dies half-built after setting a ticket In Progress.
- Confirm you're inside a git repo: `git rev-parse --is-inside-work-tree`. If not, stop and tell the user to run from the target repo.
- **Preflight the tooling** (stop with a clear message if any fails):
  - `gh auth status` succeeds (GitHub CLI authenticated).
  - `origin` is a GitHub remote: `git remote get-url origin` resolves and points at github.com.
  - Linear is reachable: a cheap `wf-linear` `FETCH <first identifier>` round-trips without `ERROR` (this also pre-validates the ticket ids).
  - The execution sandbox is present: `~/.claude/bin/wf-exec` is executable and `~/.claude/ticket-workflow-sandbox.sb` exists. The executor and verifier run all project code (tests/build/lint/install) through `wf-exec` (no external egress, no credential reads); a `PreToolUse` guard enforces it.
- Determine the default base branch: `git symbolic-ref --quiet --short refs/remotes/origin/HEAD | sed 's@^origin/@@'` (fallback to `main`/`master`/current branch). Call it `BASE`. Fetch latest: `git fetch origin`.
- Resolve the repo root: `git rev-parse --show-toplevel` (call it `ROOT`). Worktrees live in `ROOT/.worktrees/`.
- Ensure `.worktrees/` is git-ignored without touching the repo's committed files: if `.worktrees/` isn't already ignored (`git check-ignore -q .worktrees || ...`), add a line `.worktrees/` to `ROOT/.git/info/exclude` (local-only, no diff).
- **Resolve the repo manual** (shared by all tickets in this run): first existing of `ROOT/CONTEXT.md`, `ROOT/CLAUDE.md`, `ROOT/AGENTS.md`. Call its absolute path `MANUAL`. If none exists, set `MANUAL=none` and note once that running `/wf-prime` first would make the agents sharper and cheaper. Agents read `MANUAL` from `ROOT` directly (it's valid even from inside a worktree).
- **Parse the Linear state mapping.** If `MANUAL` contains a `## Linear workflow` section, read it into `STATES` (canonical stage → team state name, plus the `On merge, set →` state). **Translation rule — applies to every `wf-linear SET_STATUS` call below:** when you'd set a canonical stage, pass the team state name `STATES` gives for it; if `STATES` is absent or maps that stage to `(auto)`, pass the canonical name and let `wf-linear`'s synonym/type fallback resolve it. Never pass a `completed`/Done state — `wf-linear` refuses it anyway.

## Per ticket (default — sequential; each fully isolated in its own worktree)

> This is the default mode. If `$ARGUMENTS` contains `--parallel`, skip to **Parallel mode** below instead; it reuses the same preconditions, sandbox/worktree discipline, PR template, and after-all reporting.

### 1. Fetch
- Spawn `wf-linear`: `FETCH <identifier>` → capture title, description (the spec), acceptance criteria, BRANCH_SLUG, current state, and the `ATTACHMENTS` list. (Acceptance criteria are the `## Acceptance criteria` section of the description — extract them; you'll pass them to the reviewer and verifier.)
- **Ingest design handoffs (if any).** If `ATTACHMENTS` is not `none`, download each **immediately** (signed hrefs expire ~5 min after the fetch) into a git-ignored dir **outside** the ticket's worktree: `~/.claude/bin/wf-fetch-handoff "ROOT/.worktrees/.handoffs/<identifier>" "<href>" <size-bytes>`. Collect the printed path(s) as `HANDOFF` (else `HANDOFF=none`). Keeping it outside `.worktrees/<identifier>` (and `.worktrees/` is already git-ignored) means the handoff is readable by every agent but never enters the branch/diff. If the helper fails, note it and proceed with `HANDOFF=none` — ingestion is best-effort and never blocks the ticket.
- If the description looks un-spec'd (no acceptance criteria / clearly thin), warn the user and offer to stop so they can run `/wf-spec` first (AskUserQuestion: Continue anyway / Stop).

### 2. Worktree + branch (resumable)
- Branch name: `<identifier>/<BRANCH_SLUG>` (e.g. `ENG-123/add-oauth-login`). Lowercase the slug; keep the identifier as Linear returns it. Worktree path: `ROOT/.worktrees/<identifier>`.
- **Reuse if it already exists** (a prior run for this ticket): if `ROOT/.worktrees/<identifier>` is already a registered worktree (`git worktree list`) on the matching branch, reuse it as-is — this is a resume; keep its existing commits and continue. Only if the path exists but is stale/mismatched, ask the user before removing it.
- Otherwise create fresh from latest base: `git worktree add "<path>" -b "<branch>" "origin/<BASE>"`. If the branch already exists but no worktree does, attach instead: `git worktree add "<path>" "<branch>"`.
- **Now** set status (after the worktree is in place, so a failed setup never leaves a ticket falsely In Progress): spawn `wf-linear` `SET_STATUS <identifier> "In Progress"` (skip if already In Progress/In Review). Do this silently — don't narrate or justify the transition (no "the status change is authorized…" / "deps warmed offline" asides); it's a routine step.
- **Worktree-path discipline — pass this rule to every agent:** ALL of its file operations must target the absolute worktree path — `Bash` commands `cd "<path>"` first; `Read`/`Edit`/`Write`/`Grep`/`Glob` use absolute paths under `<path>`. Repo-relative paths resolve to `ROOT` (the main checkout — the WRONG tree) and silently corrupt the run. The only exception is reading `MANUAL`, which is at `ROOT` by design.

### 2b. Warm dependencies (offline — once per worktree)
Project code runs with **no network** under `wf-exec`, but most stacks resolve dependencies from a **shared local cache** (`~/.pub-cache`, the npm/pip caches, …) that your normal local builds keep warm. Populate the fresh worktree's dependency dir from that cache, **offline**, before planning — otherwise the first `flutter test` / `dart run` / etc. tries to reach the network and just hangs until the `wf-exec` timeout. Run the stack's install with its **offline flag** through `wf-exec`, from the worktree:
- Flutter/Dart (`pubspec.yaml`): `cd "<path>" && ~/.claude/bin/wf-exec dart pub get --offline`. **Use `dart pub get`, NOT `flutter pub get`** — `flutter pub get` does a plugin-precache that reaches the network and hangs even with `--offline`.
- Node (`package-lock.json` / `pnpm-lock.yaml` / `yarn.lock`): `wf-exec npm ci --offline` (or `--prefer-offline`); pnpm/yarn with their frozen-lockfile + offline flags.
- Python (`requirements.txt` / `pyproject.toml`): only if you keep a local wheel cache (`wf-exec pip install --no-index --find-links <cache> ...`); otherwise skip.

The offline flag is **required** — without it the tool probes the network first and the sandbox makes it hang. **Don't loop on failure:** if offline resolution fails (a package isn't cached — typically because the ticket adds a *new* dependency), note it once and either ask the user to warm the cache (build the project normally outside the workflow), or proceed and let the executor flag the missing dep in `NOTES`. **Skip** this step when there's no recognizable manifest, or on a resume where the worktree's dependency dir is already populated. Code generation and all tests stay with the executor/verifier under `wf-exec` — they need no network once deps are cached. **Resolution caveat:** many toolchains re-resolve dependencies over the network *before* each run (e.g. `flutter test` triggers an implicit pub get; some test runners auto-install), so downstream commands must use the offline / skip-resolution form (`--offline`, `--no-pub`, `--frozen-lockfile`, …). The repo manual should document those forms; if it only lists bare commands, note it so the executor/verifier add the offline flag.

### 3. Plan
- Spawn `wf-github`: `PR_HISTORY <keywords/paths from the ticket>` → a digest of how related work was done/merged here.
- Spawn `wf-planner` with: the enriched ticket, BASE, the worktree path, `MANUAL`, the PR_HISTORY digest, and `HANDOFF` (reference-only design handoff path, or `none`). It returns one of two things, tagged on its first line:
  - **`STATUS: NEEDS_INPUT`** — the planner is blocked (the spec left a real decision open). It can't reach the user, so **you** ask via AskUserQuestion: map each returned question block (`header`/`question`/`multiSelect`/`options`) to a question, options in order with the `(recommended)` one first and labeled "(Recommended)". Then **re-spawn `wf-planner`** with the *same* inputs **plus** an `ANSWERS:` section pairing each question with the user's choice (verbatim, including any "Other" free-text). Loop until it returns a plan. (Normally 0–1 rounds; a well-spec'd ticket asks nothing. If still asking after ~3 rounds, surface that to the user and ask whether to push through with current defaults.)
  - **`STATUS: PLAN`** — the plan: `GOAL`, a `CONTEXT_PACK`, `PLAN`, `TESTS`, `RISKS`, `SPEC_GAPS`, and `MANUAL_DRIFT`. Strip the status line. **Keep the CONTEXT_PACK** — it's threaded into every downstream agent so they don't re-explore. (Thread `HANDOFF` to the executor too.)
- **Manual freshness:** if `MANUAL_DRIFT` is not `none`, collect it. Don't act on it mid-ticket — surface it once in the final summary as a nudge: "CONTEXT.md looks stale: <drift> — re-run `/wf-prime`."
- **Spec self-improvement:** if `SPEC_GAPS` is not `none`, append each gap to the `## Learned spec gaps` section of `~/.claude/agents/wf-spec-builder.md` (create the section at the end of the file if absent), as a dated bullet: `- (<identifier>) <question> → <resolution>`. This makes the spec agent better next time. Use today's date.

### 4. Execute
- Spawn `wf-executor` with the PLAN, CONTEXT_PACK, MANUAL, `HANDOFF` (reference-only, or `none`), and worktree path. It makes atomic commits on the branch and returns what it changed.
- If it returns `BLOCKED`, surface to the user and stop this ticket.

### 5. Review loop (max 2 iterations)
- Spawn `wf-reviewer` with: the `GOAL` + **acceptance criteria** + the `PLAN` (so it can judge whether the diff satisfies them), the diff base `origin/<BASE>`, CONTEXT_PACK, MANUAL, and worktree path.
- If `CHANGES_REQUIRED`: spawn `wf-executor` with the BLOCKING list (+ CONTEXT_PACK, MANUAL) to fix, then re-review. After 2 rounds still blocking, surface the remaining items to the user via AskUserQuestion (Fix manually / Continue anyway / Stop).

### 6. Verify loop (max 2 iterations)
- Spawn `wf-verifier` with the acceptance criteria, CONTEXT_PACK (for the exact commands), MANUAL, and worktree path.
- If `FAIL`: spawn `wf-executor` with the FAILURES (+ CONTEXT_PACK, MANUAL) to fix, then re-verify. After 2 rounds still failing, surface to the user (same three options).
- **Collect any `GATE REQUIRED` lines** the verifier emits — warranted-but-sandbox-infeasible suites (integration/e2e/device tests) it decided are needed but couldn't run here. These do **not** block PASS or the PR; carry them into the PR body's **Pre-merge gates** section (step 7) and into the final report, so review/CI runs them before merge.

### 7. PR
- **Guard against an empty PR:** confirm the branch actually has commits beyond base — `git -C "<path>" rev-list --count "origin/<BASE>..HEAD"` must be > 0. If it's 0 (executor made no changes), do NOT open a PR — stop this ticket, leave it In Progress, and report it so the user can investigate.
- Build the PR title and body from the template below.
- Spawn `wf-github`: `CREATE_PR` with the worktree path, BASE, HEAD (`<branch>`), title, and body. It pushes the branch and opens the PR. Capture the returned `PR_URL`.

### 8. Hand off to review
- Spawn `wf-linear`: `SET_STATUS <identifier> "In Review"`.
- Spawn `wf-linear`: `LINK_PR <identifier> <pr-url>`.
- Record: `<identifier> → <branch> → <pr-url> → In Review`.

## Parallel mode (`--parallel`)

Run independent tickets **concurrently** instead of one at a time. Everything else is unchanged — the hard boundaries, preconditions, sandbox/worktree discipline, PR template, after-all reporting, and on-merge all still apply. Parallelism is safe **only** because each ticket lives in its own worktree (disjoint branches, no shared writes); the rules below keep it that way.

- **Concurrency cap: 3 tickets executing at once.** Token cost scales ~linearly with concurrency — don't fan wider.
- **Autonomous-only.** Parallel runners cannot ask you questions. Any ticket needing human input (planner blocked, or a review/verify loop still failing after 2 rounds) is set aside as `NEEDS_HUMAN` and resolved interactively after the batch — never silently forced through.
- Run the preconditions once, up front, exactly as above (fail fast before touching any ticket).

### P1. Fetch all (parallel)
Spawn `wf-linear FETCH <id>` for every ticket; capture title/description/criteria/BRANCH_SLUG/state/`ATTACHMENTS`. **Immediately** after each fetch, ingest its handoffs (signed hrefs expire ~5 min): for any `ATTACHMENTS`, run `~/.claude/bin/wf-fetch-handoff "ROOT/.worktrees/.handoffs/<identifier>" "<href>" <size-bytes>` and record `HANDOFF` per ticket (else `none`). Don't batch this for later — download as you fetch. Warn on any un-spec'd ticket and offer to drop just that one (don't block the others).

### P2. Worktrees + In Progress (sequential, cheap)
For each ticket, create/reuse its worktree+branch exactly as in sequential step 2, then set it In Progress. Do these one at a time — `git worktree add` is fast and serializing avoids any index race.

### P3. Plan all (parallel) — also the overlap signal
For each ticket, spawn `wf-github PR_HISTORY` + `wf-planner` (pass the planner that ticket's `HANDOFF`). Planning is read-only, so running all planners at once is safe — and a blocked planner simply returns `STATUS: NEEDS_INPUT` and stops without wasting an execute pass (you can't answer it mid-batch in parallel mode). Route on the returned status:
- **`STATUS: NEEDS_INPUT`** → mark that ticket `NEEDS_HUMAN`, **carry its question blocks** with it, and exclude it from parallel execute. You'll put the questions to the user and re-plan in P8.
- **`STATUS: PLAN`** → collect its `GOAL`, `CONTEXT_PACK`, `PLAN`, and `files in play`. Apply the same `SPEC_GAPS` → `wf-spec-builder.md` self-improvement append and `MANUAL_DRIFT` collection as sequential step 3.

### P4. Overlap guard
Build each ticket's file set from its `CONTEXT_PACK` `files in play`. Any ticket whose set **intersects another ticket's set** is not parallel-safe → move it to a **sequential tail**. The tickets with sets disjoint from all others form the **parallel set**. This stops two concurrent runners from racing on the same file. (It does **not** make overlapping tickets stack — see Known limitations.)

### P5. Execute the parallel set (concurrent, ≤3 at a time)
For each parallel-set ticket, spawn `wf-runner` with its `PLAN`, `CONTEXT_PACK`, `MANUAL`, `HANDOFF` (reference-only, or `none`), acceptance criteria, base `origin/<BASE>`, and worktree path. Run up to 3 at once. Each returns `DONE`, `NEEDS_HUMAN` (with unresolved items), or `BLOCKED`.

### P6. Execute the sequential tail
Run the tail tickets one at a time, each via `wf-runner` the same way — overlapping tickets must never run together.

### P7. PR + hand-off (orchestrator, per `DONE` ticket)
For every ticket that returned `DONE`, do sequential steps 7–8 unchanged: empty-PR guard → `wf-github CREATE_PR` → `wf-linear SET_STATUS "In Review"` + `LINK_PR`. **All Linear/GitHub mutations stay with you** (the orchestrator); `wf-runner` never touches them.

### P8. Resolve the set-asides (interactive)
For each `NEEDS_HUMAN`/`BLOCKED` ticket, now handle it interactively, reusing its worktree. These keep their worktree and stay **In Progress** until resolved. Two cases:
- **Set aside at planning (P3 returned `STATUS: NEEDS_INPUT`):** put the carried question blocks to the user via AskUserQuestion (map them as in sequential step 3), then re-spawn `wf-planner` with the same inputs plus the `ANSWERS:` section to get a `STATUS: PLAN` (apply the `SPEC_GAPS` append + `MANUAL_DRIFT` collection). Then run the inner loop for that ticket via `wf-runner` exactly as in P5.
- **Set aside in the loop (review/verify still failing, or `BLOCKED`):** surface the unresolved items via AskUserQuestion (Fix manually / Continue anyway / Stop), exactly like the sequential review/verify loops.

Then take resolved ones through P7.

Finish with the shared **After all tickets** reporting.

## PR description template (concise, high-fidelity — no filler)

```
## What
<1–2 lines: the change, in plain terms>

## Why
<1 line: the ticket goal. Reference the Linear ticket: <identifier>>

## Changes
- <terse bullet per meaningful change>

## Verification
- <tests run + result; build/lint status>

## Pre-merge gates
- <each `GATE REQUIRED` from the verifier — suite + why it's needed (e.g. integration tests for the X flow, run via CI/`-d device`)>
(omit this whole section if the verifier reported no gates)

Linear: <identifier> — <ticket url>
```

Title: `<identifier>: <ticket title>`. Keep the whole body tight — every line must carry information. No "this PR introduces…" padding, no restating the diff line by line.

## After all tickets

Print a table: identifier → branch → PR URL → status. Remind the user:
- Review/merge happen on GitHub by them.
- When a PR is merged, tell me ("ENG-123 is merged") and I'll run the "On merge" steps — I never do it on my own. On merge I set the ticket to its **post-merge state** (QA by default, or whatever the repo's `## Linear workflow` config names — never Done) and clean up the worktree; the human then verifies the merged result and moves it → **Done** themselves.
- If any ticket reported `MANUAL_DRIFT`, list the distinct drift items once here and suggest re-running `/wf-prime`.

## On merge (only when the user says a specific ticket's PR was merged)

This often runs in a **later session** that doesn't remember the slug, so resolve everything from the identifier — don't rely on memory.

For each merged `<identifier>`:
1. **Resolve the branch + worktree** from the identifier (don't assume the slug): branch = `git branch --list "<identifier>/*"` (the one match); worktree path = the entry in `git worktree list` whose branch matches. If neither is found, it was likely already cleaned up — just do steps 2 and report.
2. Spawn `wf-github`: `PR_STATUS <identifier-or-branch>` to confirm `STATE: MERGED`. If it's not actually merged, stop and tell the user — do not change status or remove anything.
3. Move the ticket to the **post-merge state** — `STATES`' `On merge, set →` value if `MANUAL` defined one, else `QA`. Spawn `wf-linear`: `SET_STATUS <identifier> "<post-merge state>"`. Merge means the code is in, **not** that it's verified — a human verifies the merged result and then moves the ticket to **Done** themselves; never set Done here. **No QA-equivalent state?** If the post-merge state is `In Review` (the no-QA default) or `wf-linear` returns `ERROR: no workflow state matches` (the team lacks that state), leave the ticket where it is, still do the cleanup in step 4, and say so in step 5 (`left In Review — no QA state`). A missing post-merge state must never block worktree cleanup.
4. Clean up, from `ROOT`:
   - `git worktree remove "<resolved-worktree-path>"` (add `--force` only if it reports uncommitted changes AND the user confirms).
   - `git branch -d "<resolved-branch>"` (the merge means it's safe; use `-D` only if git refuses and the user confirms the branch is fully merged).
   - `git worktree prune`.
   - `rm -rf "ROOT/.worktrees/.handoffs/<identifier>"` (remove any ingested design handoff; no-op if there was none).
5. Confirm: `<identifier> → <post-merge state> (awaiting human verification), worktree + branch removed`.

Never clean up a worktree whose PR has not been confirmed merged.

## Failure handling
- Any `wf-linear` or `wf-github` `ERROR`: surface plainly, don't fabricate data.
- If a `git`/`gh` step fails, stop that ticket, report the exact error, and leave the worktree in place for inspection (don't auto-delete worktrees).
- A ticket that stops mid-run stays **In Progress** with its worktree intact — that's deliberate (it reflects reality and lets you resume by re-running `/wf-run <id>`, which reuses the worktree). It is not auto-reverted to To Do.

## Known limitations
- **Tickets are independent.** Each ticket branches from `origin/<BASE>`; a ticket cannot build on another ticket's unmerged work (no PR stacking). If two tickets depend on each other, run and merge the first before the second.
- **Parallel mode prevents racing, not stacking.** The overlap guard (P4) serializes tickets that touch the same files so they don't clobber each other concurrently — but they still each branch from base, so an overlapping pair can still conflict at *merge*. That's the pre-existing no-stacking limitation, unchanged.
- **Parallel mode's overlap guard is only as good as the planner's `files in play`.** A file the planner didn't foresee can still collide. The empty-PR guard and merge conflicts are the backstops.
- **`wf-runner` is the canonical inner loop** (execute → review → verify) for parallel mode; the sequential path (steps 4–6) still inlines the same loop. They share the same 2-round policy deliberately; if you change one, mirror the other (or later unify sequential onto `wf-runner`).
- **`## Learned spec gaps`** in `wf-spec-builder.md` is append-only; prune it occasionally if it grows large.
