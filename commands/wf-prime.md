---
description: Generate a compact CONTEXT.md operating manual for the current repo, reused by the ticket-workflow agents across every ticket. Run once per repo (re-run after big structural changes).
argument-hint: [team-key | ticket-id]  (optional — auto-detects that Linear team's states)
allowed-tools: Task, Bash, Read
---

# /wf-prime

Produce the durable, token-cheap context manual the ticket-workflow agents read on every ticket. This is the highest-leverage context investment: explore once, reuse everywhere.

## Steps

1. **Preconditions.** Confirm you're in a git repo (`git rev-parse --is-inside-work-tree`). Resolve `ROOT = git rev-parse --show-toplevel`.

2. **Skip-or-refresh check.** If a committed `CLAUDE.md` or `AGENTS.md` already exists at `ROOT`, tell the user the repo already has an agent-readable manual and ask whether to generate a separate `CONTEXT.md` anyway (some repos want both). If `ROOT/CONTEXT.md` already exists, mention its age and confirm a refresh before overwriting.

3. **Detect Linear states (only if an argument was given).** If `$ARGUMENTS` names a team key or ticket id, spawn `wf-linear` `LIST_STATES <arg>` and capture the returned `TEAM` + `STATES` block as `LINEAR_STATES`. This pre-fills the repo's `## Linear workflow` mapping so status transitions match the team out of the box. If Linear isn't connected or it returns `ERROR`, note it once and continue with `LINEAR_STATES=none` (the mapping falls back to `(auto)`, which the workflow resolves by synonym/type at runtime). With no argument, skip this step (`LINEAR_STATES=none`).

4. **Generate.** Spawn `wf-cartographer` with the target path `ROOT/CONTEXT.md`, today's date (it stamps `Primed: <date>` in the header so staleness is visible at a glance), and `LINEAR_STATES` (or `none`).

5. **Commit it (recommended default).** `CONTEXT.md` is meant to live with the repo — committed, it's shared with the team and appears in every worktree automatically. Offer to stage + commit it (`git add CONTEXT.md && git commit -m "chore: add agent operating manual (CONTEXT.md)"`), or leave it staged for the user to commit. Only if the user prefers to keep it local/uncommitted, append `CONTEXT.md` to `ROOT/.git/info/exclude` instead.

6. **Confirm.** Print the path, line count, and a 3-line gist of what the manual captured. Remind the user that `/wf-spec` and `/wf-run` will now pick it up automatically, and that they'll get a `MANUAL_DRIFT` nudge when it goes stale (re-run `/wf-prime` after structural changes — new stack/module, changed build/test commands, big refactors).
