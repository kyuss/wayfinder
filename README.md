# 🧭 Wayfinder

**An agent crew that turns Linear tickets into GitHub PRs — built on Claude Code.**

Wayfinder is a **Linear-ticket → GitHub-PR autonomous coding pipeline** built entirely from
[Claude Code](https://claude.com/claude-code) subagents, slash commands, a macOS
sandbox, and an eval harness. Each agent is modeled on a senior engineering role
and assigned a model tier matched to its cognitive load. Every ticket runs in its
own git worktree and ends as an open PR you review and merge yourself — the
workflow **never merges, waits on checks, or marks a ticket Done on its own.**

```
/wf-prime                 # once per repo — writes a reusable CONTEXT.md manual
/wf-spec  ENG-12 ENG-13   # interactive — refine each ticket into a real spec
/wf-run   ENG-12 ENG-13   # autonomous — each ticket → open PR (In Review)
                          # …you review & merge the PR yourself…
"ENG-12 is merged"        # only now does the workflow move it to QA + clean up
```

See [`docs/TICKET-WORKFLOW.md`](docs/TICKET-WORKFLOW.md) for the full framework
overview and [`docs/ticket-workflow.html`](docs/ticket-workflow.html) for a visual
explainer. **The agent and command files are the source of truth** — the docs are
an overview; when they disagree, the files win.

## What's in the box

| Path | What |
|---|---|
| `agents/wf-*.md` | 10 subagents — spec-builder, planner, executor, reviewer, verifier, cartographer, runner, the Linear/GitHub boundary agents, and an eval judge |
| `commands/wf-*.md` | 6 slash commands — `/wf-prime`, `/wf-spec`, `/wf-run`, `/wf-quick`, `/wf-eval`, `/wf-calibrate` |
| `bin/wf-exec` | Runs a repo's tests/build/lint inside a no-network, no-secrets sandbox |
| `bin/wf-fetch-handoff` | Safely downloads a Linear design-handoff embed (allowlisted, size-capped, zip-slip-guarded) |
| `hooks/` | Two guard hooks: sandbox enforcement + boundary-agent tool-call enforcement |
| `ticket-workflow-sandbox.sb.template` | macOS seatbelt profile (installer fills in your `$HOME`) |
| `ticket-workflow-evals/` | The regression gate — fixtures, cases, rubrics, baselines, judge calibration |

## Design principles

- **Context flows forward, never re-derived.** The Opus planner explores the repo
  once and emits a dense Context Pack; cheaper downstream agents consume that plus a
  per-repo `CONTEXT.md` manual instead of re-reading the codebase each loop.
- **Single-owner boundaries.** Only `wf-linear` touches Linear; only `wf-github`
  touches GitHub. A `SubagentStop` hook blocks either from finishing without a real
  tool call (no fabricated answers).
- **Sandboxed execution.** All project code runs through `wf-exec` — no network
  egress, no credential-file reads, and secret-shaped env vars (`*TOKEN*`, `*_KEY`,
  `AWS_*`, …) are stripped before it runs. A `PreToolUse` hook blocks unwrapped
  project-code *and* raw network binaries (`curl`/`wget`/`ssh`/…) inside worktrees,
  and the Opus planner/spec-builder have `WebFetch` removed (they ingest untrusted
  ticket text). This breaks the "lethal trifecta" (untrusted ticket text + repo
  secrets + exfiltration path).
- **Never autonomous on irreversible steps.** No merging, no waiting on checks, no
  setting Done — a human always closes the loop.
- **Model tiering is deliberate.** Opus for decisions/architecture/bug-catching,
  Sonnet for execution/verification, Haiku for high-volume structured API calls.

## Prerequisites

- **macOS** — the execution sandbox uses `sandbox-exec` (seatbelt). See
  [Platform support](#platform-support).
- **Claude Code** with a Claude subscription or API key.
- **[Linear MCP](https://linear.app/docs/mcp)** connected in Claude Code (`/mcp`).
- **`gh` CLI**, installed and authenticated (`gh auth status`).
- **`jq`** (used by the guard hooks).
- **`node`** and **`python3`** to run the eval fixtures (stdlib only; no deps).
- Git repos with an `origin` remote and a default branch.

## Install

```bash
git clone https://github.com/kyuss/wayfinder
cd wayfinder
./install.sh
```

The installer copies the `wf-*` files into `~/.claude/`, generates the sandbox
profile for your machine, and sets up the eval fixtures. It **does not modify your
`settings.json`** — instead it prints one manual step: merging the two hook entries
from [`settings.hooks.json`](settings.hooks.json) into your `~/.claude/settings.json`.
Those hooks enforce the sandbox and the boundary guard, so the security model
depends on them.

Then, in Claude Code: connect Linear (`/mcp`), run `/wf-prime` in a repo, and try
`/wf-spec <TICKET-ID>` → `/wf-run <TICKET-ID>`.

## Configuring your Linear workflow states

The workflow moves tickets through **In Progress → In Review → (post-merge)**, and
marks a spec'd ticket **Ready for Development**. Your team's state *names* almost
certainly differ — that's fine, and there are two layers of adaptation:

- **Zero config** — `wf-linear` never assumes a state; it lists your team's real
  states and matches by name (case-insensitive), a synonym table, then Linear's
  state `type`. Common variants (`Doing`, `Backlog`, `Code Review`, …) just work.
- **Explicit config** — each repo's `CONTEXT.md` (written by `/wf-prime`) carries a
  `## Linear workflow` block mapping each canonical stage to your exact state name:

  ```markdown
  ## Linear workflow
  - Ready for Development → Ready
  - In Progress → Doing
  - In Review → Code Review
  - On merge, set → QA        # or `In Review` if your team has no QA state
  ```

  Run **`/wf-prime <TEAM-KEY>`** (or a ticket id) and it auto-detects the team's live
  states and pre-fills this block for you. Edit it anytime — it's just a repo doc.

**No QA state?** Set `On merge, set → In Review` (or leave it — the workflow detects a
missing QA state and simply leaves the ticket In Review after merge, then cleans up).

**Done is never automatic.** Whatever you configure, the workflow refuses to set a
`completed`/Done-type state on its own — a human always closes the loop.

## Developing / testing changes

There's no build step — **the eval harness is the test suite.** After changing any
agent prompt, model tier, or the flow:

```
/wf-eval                 # full seed set vs the saved baseline
/wf-eval node-feature    # iterate on one case (cheaper)
```

`wf-judge` scores each stage against a rubric and the runner flags regressions.
Run `/wf-calibrate` after changing the judge's model or prompt to keep the gate
trustworthy.

## Platform support

The sandbox is **macOS-only** (`sandbox-exec` / seatbelt). On other platforms the
agents and commands still install and most of the flow works, but `/wf-run` will
run project tests/build **without the sandbox** — meaning untrusted ticket/PR
content and dependency code run unconfined. Don't run it against untrusted tickets
on non-macOS until a Linux sandbox backend (e.g. bubblewrap) is wired in.
Contributions welcome.

## Security

This runs autonomous agents against your repos. The threat model and mitigations
(sandbox, boundary guards, read-only handoff ingestion, never-merge policy) are
described in [`docs/TICKET-WORKFLOW.md`](docs/TICKET-WORKFLOW.md). The sandbox is
defense-in-depth, not a guarantee — review PRs before merging.

**Audit the sandbox deny-list against your own secrets.** The seatbelt profile is
`(allow default)` with carve-outs, so it blocks reads of the *standard* credential
stores (`~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.config/gh`, `~/.config/git`, `~/.netrc`).
If you keep secrets elsewhere — `.env` files in repos, a custom `$CLOUDSDK_CONFIG` or
other cloud-CLI cache, tokens outside `$HOME` — add matching `deny file-read*` entries
to `ticket-workflow-sandbox.sb.template` before installing.

## License

[MIT](LICENSE)
