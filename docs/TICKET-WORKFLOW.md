# Ticket Workflow — Framework Overview

A Linear-ticket → GitHub-PR autonomous coding workflow built from specialized Claude Code subagents. Each agent is modeled on a senior engineering role and assigned a model tier matched to its cognitive load. Everything that *runs* lives at user level (`~/.claude/`), works on any git repo you invoke it in, and isolates each ticket in its own git worktree. This document and its visual companion (`ticket-workflow.html`) live in this project directory and are the human-readable overview.

> **Source of truth:** the agent files (`~/.claude/agents/*.md`) and command files (`~/.claude/commands/*.md`) are self-documenting and auto-loaded each session. This file is a human-readable overview; **when behavior and this doc disagree, the files win.** Read the relevant file before editing the system.

---

## TL;DR — the typical flow

```
/wf-prime                 # once per repo — writes a reusable CONTEXT.md manual
/wf-spec ENG-12 ENG-13 # interactive — refine each ticket into a real spec
/wf-run  ENG-12 ENG-13 # autonomous — each ticket → open PR, In Review
                            # …you review & merge the PR yourself…
"ENG-12 is merged"          # only now does the workflow set Done + clean up
```

Run `/wf-eval` whenever you change an agent prompt, a model tier, or the flow — it's the regression gate.

---

## Agents (10)

**Reasoning agents — do the thinking:**

| Agent | Model | Persona | Job |
|---|---|---|---|
| `wf-spec-builder` | opus | Tech lead | Interactive — explores code + history, asks you the few questions that matter, produces an implementation-ready spec |
| `wf-planner` | opus | Architect | Turns a spec'd ticket into a surgical plan + a forward **Context Pack**; emits `SPEC_GAPS` and `MANUAL_DRIFT` signals |
| `wf-executor` | sonnet | Staff eng | Implements the plan with atomic commits; surfaces any new dependency; works surgically |
| `wf-reviewer` | opus | Principal reviewer | Reviews the diff — the bug that matters, not nits; high bar for blocking |
| `wf-verifier` | sonnet | Release eng | Runs tests/build/lint, proves each acceptance criterion by execution |
| `wf-cartographer` | sonnet | Onboarding lead | One-time: writes the repo's `CONTEXT.md` operating manual |

**Boundary agents — own one external system each, mechanical and precise:**

| Agent | Model | Owns |
|---|---|---|
| `wf-linear` | haiku | **All** Linear MCP calls — `FETCH`, `SET_STATUS`, `UPDATE_DESCRIPTION`, `LINK_PR` |
| `wf-github` | haiku | **All** `gh` CLI calls — `PR_HISTORY`, `CREATE_PR`, `PR_STATUS` |

**Orchestration agent — drives one ticket's inner loop (used by `--parallel`):**

| Agent | Model | Job |
|---|---|---|
| `wf-runner` | sonnet | Runs the autonomous inner loop for **one** ticket inside its worktree — execute → review (≤2) → verify (≤2) — coordinating `wf-executor`/`wf-reviewer`/`wf-verifier`. Lets `/wf-run --parallel` run independent tickets concurrently. Never writes code, never touches Linear/GitHub, never asks the user; returns `DONE` / `NEEDS_HUMAN` / `BLOCKED`. |

**Eval agent — used only by the regression harness, never in `/wf-run`:**

| Agent | Model | Job |
|---|---|---|
| `wf-judge` | sonnet | LLM-as-judge: scores another agent's output (a plan, or a diff + test result) against a case rubric — binary pass/fail + 0–1 per dimension. Weights *observed test results* above the diff's prose or the agent's own claims. |

Each agent leads with concrete *operating standards* (how a senior in that role behaves), not just a title. Model tiering is deliberate: **Opus** where reasoning has the highest impact (decisions, architecture, bug-catching), **Sonnet** for execution/verification/grading, **Haiku** for high-volume structured external calls.

> An eleventh agent file, `notion.md`, also lives in `~/.claude/agents/` but is a general-purpose Notion helper **unrelated** to this ticket workflow.

---

## Commands (5)

- **`/wf-prime`** — run once per repo. `wf-cartographer` writes a compact `CONTEXT.md` operating manual (~100–180 dense lines: stack, architecture map, conventions, exact build/test/lint commands, gotchas). Recommended to commit it. Optional, but the highest leverage-per-token move in the system.
- **`/wf-spec <ids>`** — interactive, run first. Refines each ticket *one at a time* in conversation with you and writes the spec into its Linear **description**. The ticket stays in *To Do*.
- **`/wf-run <ids> [--parallel]`** — autonomous A→Z. Each ticket runs in its own git worktree, from *In Progress* to an open PR (*In Review*). Default is **sequential** (one ticket at a time); `--parallel` runs file-disjoint tickets **concurrently** (≤3 at once) via `wf-runner`. Never merges.
- **`/wf-eval [case ...]`** — the regression gate. Runs stage evals (planner, executor) over seed cases against local fixtures, judged by `wf-judge`, and compares to the saved baseline. Fully offline — never touches Linear/GitHub.
- **`/wf-calibrate`** — validates the *judge* itself. Grades `wf-judge` against a human-labeled gold set (agreement, FAIL-class precision/recall, bias probes) so the `/wf-eval` gate can be trusted. Fully offline; re-run after changing the judge's model or prompt.

Each command is also available as a `Skill` of the same name.

---

## The pipeline

```
            ┌──────────────── /wf-prime (once per repo) ────────────────┐
            │  wf-cartographer → CONTEXT.md  ("MANUAL", committed)       │
            └──────────────────────────────────────────────────────────────┘
                                       │ reused by every ticket in every run
                                       ▼
/wf-spec ─▶ wf-linear FETCH ─▶ wf-github PR_HISTORY ─▶ wf-spec-builder ⇄ YOU
 (interactive)                                                        │
                                       wf-linear UPDATE_DESCRIPTION ◀┘  (spec → ticket description)

/wf-run — PREFLIGHT first (fail-fast, before touching any ticket):
  git repo? · gh authed? · origin remote? · Linear reachable? · sandbox present & executable?
  · resolve repo root + base branch · ignore .worktrees/ locally · resolve the MANUAL

  …then per ticket (sequential by default; each isolated in ROOT/.worktrees/<id>):

  git worktree + branch  ticket-id/slug   (from origin/BASE; reused if it already exists)
       │
  wf-linear SET_STATUS "In Progress"   ← only AFTER the worktree exists
       │
  wf-github PR_HISTORY ─┐
       │                   ▼
  wf-planner ─▶ GOAL + CONTEXT_PACK + PLAN ───────────────┐
       │            (+ SPEC_GAPS, MANUAL_DRIFT signals)        │ threaded down → nobody re-explores
       ▼                                                       ▼
  wf-executor ◀──────── fix ──────────┐            wf-reviewer   (≤2 rounds)
       │                                  └────────────────────┘
       ▼
  wf-verifier  (≤2 rounds) ──── fail → executor ──┘
       │ pass
       ▼
  empty-PR guard: branch has commits beyond base?  ── no → STOP, leave In Progress, report
       │ yes
       ▼
  wf-github CREATE_PR  (push + open PR; What/Why/Changes/Verification body)
       │
  wf-linear SET_STATUS "In Review"  +  LINK_PR
       │
       ▼
  ■ STOP — PR ready for your review
```

**On merge (only when *you* say "ENG-123 is merged"):**
`wf-github PR_STATUS` confirms MERGED → `wf-linear SET_STATUS "<post-merge state>"` (the repo's `## Linear workflow` config, **QA** by default — never Done) → worktree + local branch removed → `git worktree prune`. A human verifies the merged result and moves it to Done. The workflow never does this on its own. See the README's *Configuring your Linear workflow states* for how state names adapt to your team.

---

## Parallel mode (`--parallel`)

Same pipeline, run **concurrently** across independent tickets instead of one at a time. Every hard rule is unchanged — preflight, sandbox/worktree discipline, single-owner boundaries, the PR template, after-all reporting, and on-merge. Parallelism is safe **only** because each ticket lives in its own worktree (disjoint branches, no shared writes), and the overlap guard below keeps it that way.

```
PREFLIGHT (once) ─▶ fetch all (∥) ─▶ worktrees + In Progress (sequential, cheap)
       │
       ▼
plan all (∥, non-interactive) ─▶ OVERLAP GUARD: split by "files in play"
       │                              │
       │              ┌───────────────┴────────────────┐
       ▼              ▼                                 ▼
  SPEC_GAPS?     parallel set (disjoint files)     sequential tail (overlapping files)
  → NEEDS_HUMAN  wf-runner ×N, ≤3 at once      wf-runner, one at a time
                      │                                 │
                      └──────────────┬──────────────────┘
                                     ▼
        per DONE ticket (orchestrator): empty-PR guard → CREATE_PR → In Review + LINK_PR
                                     │
                                     ▼
        NEEDS_HUMAN / BLOCKED tickets resolved interactively after the batch
```

- **Concurrency cap: 3 tickets executing at once.** Token cost scales ~linearly with concurrency — it doesn't fan wider.
- **`wf-runner` is the unit of parallelism.** It owns one ticket's execute → review → verify loop; the orchestrator keeps *all* Linear/GitHub mutations to itself (runners never touch them).
- **Autonomous-only.** Parallel runners can't ask you questions: any ticket that needs human input (planner returns `SPEC_GAPS`, or a review/verify loop still failing after 2 rounds) is set aside as `NEEDS_HUMAN` and resolved interactively after the batch — never silently forced through.
- **Overlap guard prevents races.** Each ticket's file set is built from its planner's `CONTEXT_PACK` *files in play*; any ticket whose set intersects another's is moved to a **sequential tail** so two runners never race on the same file. (This doesn't make overlapping tickets *stack* — they stay independent; see below.)

---

## Per-ticket lifecycle in detail

The non-obvious operational guarantees inside `/wf-run`:

- **Preflight is fail-fast.** Before *any* ticket is touched, the orchestrator validates: it's a git repo, `gh` is installed + authed, a GitHub `origin` remote exists, Linear is reachable (a cheap `FETCH` of the first ticket), the sandbox wrapper is present and executable, the repo root and base branch resolve, and `.worktrees/` is excluded locally (via `.git/info/exclude`, *not* `.gitignore` — it never pollutes committed files). The **MANUAL** (first existing of `CONTEXT.md` / `CLAUDE.md` / `AGENTS.md`) is resolved once and reused for every ticket in the run. Any preflight failure stops the whole run.
- **Status timing is honest.** A ticket is set *In Progress* **only after** its worktree is successfully created — so a setup failure never leaves a ticket falsely marked In Progress.
- **Resumable.** If the branch/worktree for a ticket already exists, it's **reused** rather than recreated — a failed run can be re-invoked and pick up where it left off.
- **Acceptance criteria drive verification.** The orchestrator extracts the `## Acceptance criteria` section from the ticket description and passes it to the reviewer and verifier; they check observed behavior against each criterion, not merely that code exists.
- **Bounded loops.** Review and verify are each capped at **≤2 rounds**. If still blocking/failing after two, the remaining items are surfaced to you rather than looping forever.
- **Empty-PR guard.** Before opening a PR the orchestrator confirms the branch has commits beyond base. Zero commits → **no PR**; the ticket is left *In Progress* and reported for investigation.
- **Isolated, no stacking.** Each ticket is fully isolated in its own worktree — sequentially one at a time by default, or concurrently under `--parallel` (≤3, file-disjoint). Either way a ticket **cannot** build on another ticket's unmerged work (no PR stacking) — they're independent.
- **Worktree lifecycle is asymmetric.** Kept on failure (left in place for inspection — a lingering worktree signals the ticket is still in flight); removed only on a confirmed merge.
- **New dependencies are never silent.** If the plan requires one, the executor installs it through the sandbox and calls it out explicitly in `NOTES` so you see it before merge.
- **Errors surface plainly.** Linear/GitHub errors, git/gh failures, and `BLOCKED` returns stop the affected ticket (leaving its worktree) and are reported — the run does not silently continue past a broken ticket.

---

## What makes it smart *and* cheap

The context strategy: **distill / target / cache / pass-forward** — never dump, broadcast, re-derive, or regenerate.

1. **Context flows forward, never re-derived.** The expensive Opus planner explores the repo once and emits a dense `CONTEXT_PACK` (files in play, patterns to mirror, exact commands, gotchas). The cheaper executor/reviewer/verifier consume that + the MANUAL instead of re-reading the codebase on every review/verify loop. Net token *savings*.
2. **The repo manual is amortized once per repo.** `CONTEXT.md` (~150 lines) is read on demand and reused across every ticket in every run. Personas and manual-reading instructions live in cached system prompts → ~free at runtime.
3. **Single-owner boundaries.** Only `wf-linear` touches Linear, only `wf-github` touches GitHub. Because subagents can't spawn subagents, the orchestrator (the command) pre-fetches via these two and passes data down — keeping every other agent free of external-API plumbing.
4. **Targeted slices.** Each agent gets only what it needs (verifier → commands + criteria; reviewer → diff + standards), not everything.

---

## Self-improvement signals

- **`SPEC_GAPS`** — if the planner has to ask you a question mid-run, the spec was incomplete. The gap is automatically appended (dated) to a `## Learned spec gaps` section at the end of `wf-spec-builder.md`, so the spec agent gets better over time without manual curation.
- **`MANUAL_DRIFT`** — the planner reads the manual + live code together, so it flags when `CONTEXT.md` has gone stale (changed commands, patterns that no longer hold, unmapped new areas). It is collected during planning and surfaced **once at the end** of `/wf-run` as a nudge to re-run `/wf-prime`. Advisory only — never blocks a ticket or regenerates mid-run.

---

## Security & sandboxing

The workflow ingests untrusted text (Linear ticket descriptions, GitHub PR/commit history) and runs a repo's tests/build/lint — i.e. attacker-influenceable code. To break the "lethal trifecta" (private data + untrusted content + exfiltration), **all project-code execution is sandboxed**:

- **`wf-exec` wrapper** (`~/.claude/bin/wf-exec`) runs commands under a macOS seatbelt profile (`~/.claude/ticket-workflow-sandbox.sb`): **external network egress blocked** (loopback + unix sockets allowed so local tests work), and host credential stores (`~/.ssh`, `~/.aws`, `~/.gnupg`, `gh`/`git` config, `.netrc`) **unreadable**. A malicious test file or `postinstall` hook therefore can't phone home or read your keys.
- **`wf-executor` and `wf-verifier`** run *every* project command (test/build/lint/install) through `wf-exec`. New dependencies must be surfaced to you before merge.
- **Enforcement hook** (`~/.claude/hooks/wf-sandbox-guard.sh`, a `PreToolUse` Bash hook) **blocks** unwrapped test/build/install commands inside a worktree — defense-in-depth, not just instructions. It fails *open* (on any parse uncertainty it allows the command, so it never bricks the shell) and ignores `git`/`gh` and anything outside `.worktrees/`.
- **Egress stays open only for the boundary agents** — `wf-linear`/`wf-github` talk to Linear/GitHub; nothing else touches the network.
- *Scope note:* the sandbox restricts network + secret reads, not filesystem writes (writes to `~/.cache`, `/tmp`, `node_modules` are allowed so tools don't break).

---

## Evals & regression gate

`/wf-eval` is a **stage-eval** harness so prompt/model/flow changes can't silently degrade quality. It lives in `~/.claude/ticket-workflow-evals/`:

- **Fixtures** — tiny, dependency-free git repos (`node-toy`, `py-toy`) whose tests run via stdlib (`node --test`, `python3 -m unittest`) so they pass inside the no-network sandbox. Fixtures are reset between stages (`git checkout -- . && git clean -fd && git checkout main`) so each eval starts clean.
- **Seed cases** (`cases/*.md`) — a mock ticket + the fixture it runs against + a per-stage rubric (REQUIRED/NICE dimensions). Ships with **four**: `node-feature`, `node-bugfix`, `py-feature`, and `ambiguous-spec` (which checks the planner *refuses to invent scope*).
- **Stages** — `plan` judges `wf-planner`'s output; `execute` judges `wf-executor`'s diff + whether the fixture's tests actually pass. Fixture tests are run sandboxed via `wf-exec`.
- **Eval mode is non-interactive.** In fixture mode the planner gets an explicit flag: do NOT call `AskUserQuestion`; if it would ask, it states the issue in `SPEC_GAPS` and proceeds conservatively.
- **Judge + baseline.** `wf-judge` scores each stage against the rubric (binary gate, then 0–1, weighting observed test results highest). The runner prints a `case | stage | PASS/FAIL | score | biggest weakness` table and compares to `baselines/baseline.md`, flagging a **regression** when a case went PASS→FAIL or its score dropped **> 0.15**.

Cost-aware: each case spawns 1–2 agents + a judge — iterate on one case id while developing, run the full set before committing a change.

**Trusting the judge.** `/wf-eval` is only as trustworthy as `wf-judge`. `/wf-calibrate` validates the judge itself against a human-labeled gold set (`ticket-workflow-evals/calibration/`) — agreement (bar: ≥90%), FAIL-class precision/recall, and bias probes — and reports `CALIBRATED` / `NOT CALIBRATED`. Re-run it whenever you change the judge's model or prompt, for the same reason you run `/wf-eval` after changing any pipeline agent.

---

## Firm invariants

- **Never merges, waits for checks, or sets Linear "Done" autonomously.** Done + worktree cleanup require your explicit "PR X is merged" go-ahead (and `wf-github` confirms MERGED before any cleanup).
- **Branch naming:** `ticket-id/slug` (e.g. `ENG-123/add-oauth-login`); slug is the kebab-cased ticket title.
- **Worktrees:** live in `ROOT/.worktrees/<identifier>`. Kept on failure for inspection; removed on merge. Excluded locally via `.git/info/exclude`.
- **Spec persistence:** the refined spec is written to the Linear ticket **description** (no `.planning/` files anywhere).
- **PR descriptions:** concise, high-fidelity (What / Why / Changes / Verification + Linear ref). No filler.
- **Sandboxed execution:** all project code runs via `wf-exec` (no external egress, no credential reads); the `PreToolUse` guard enforces it.
- **Commit attribution:** executor commits carry `Co-Authored-By: Claude <noreply@anthropic.com>`.
- Every agent embeds the same engineering discipline: surgical changes, simplicity, goal-driven verification.

---

## Prerequisites

- **Linear** — official Linear MCP (`mcp__linear__*`), authenticated via `/mcp`. Used only by `wf-linear`.
- **GitHub** — `gh` CLI installed and authenticated. Used only by `wf-github`.
- **git** — `/wf-run` and `/wf-prime` are run from inside the target repo; the repo should have an `origin` remote and a default branch.
- **Sandbox** — macOS `sandbox-exec` (built in) + the `wf-exec` wrapper and seatbelt profile. No install needed; `/wf-run` preflights their presence.

---

## Model tiering rationale

| Tier | Agents | Why |
|---|---|---|
| Opus | wf-spec-builder, wf-planner, wf-reviewer | Decisions, architecture, and bug-catching — where reasoning quality compounds |
| Sonnet | wf-executor, wf-verifier, wf-cartographer, wf-runner, wf-judge | Follows explicit plans / runs checks / maps structure / coordinates the inner loop / grades to a rubric — capable, cheaper |
| Haiku | wf-linear, wf-github | High-volume, structured external API calls — precision over reasoning |

---

## File map

The **system** runs from `~/.claude/`; this **documentation** lives in the project directory.

```
~/.claude/                            # the running system (auto-loaded each session)
├── agents/
│   ├── wf-spec-builder.md   wf-planner.md   wf-executor.md
│   ├── wf-reviewer.md   wf-verifier.md   wf-cartographer.md
│   ├── wf-runner.md                 # inner-loop orchestrator (--parallel)
│   ├── wf-linear.md   wf-github.md   wf-judge.md
│   └── notion.md                     # unrelated general-purpose helper
├── commands/
│   └── wf-prime.md  wf-spec.md  wf-run.md  wf-eval.md  wf-calibrate.md
├── bin/wf-exec                       # sandbox wrapper
├── hooks/wf-sandbox-guard.sh         # PreToolUse guard (enforces wf-exec)
├── ticket-workflow-sandbox.sb        # seatbelt profile (no egress, no secret reads)
└── ticket-workflow-evals/            # eval harness
    ├── README.md
    ├── fixtures/{node-toy,py-toy}/
    ├── cases/*.md                    # node-feature, node-bugfix, py-feature, ambiguous-spec
    ├── calibration/                  # gold labels + artifacts for /wf-calibrate
    └── baselines/baseline.md

<this project>/
├── CLAUDE.md                         # how to work on the system
├── TICKET-WORKFLOW.md   ← this file  # full framework overview
└── ticket-workflow.html              # visual explainer
```
