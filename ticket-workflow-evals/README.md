# Ticket-Workflow Eval Harness

A regression gate for the agent pipeline. Run `/wf-eval` after changing any agent prompt, model, or the flow, to catch silent quality drops.

## Layout
- `cases/*.md` — seed cases: a mock ticket + the fixture it runs against + a per-stage rubric.
- `fixtures/` — tiny, git-initialized throwaway repos the agents act on (`node-toy`, `py-toy`). Dependency-free; tests run via stdlib (`node --test`, `python3 -m unittest`) so they work inside the no-network sandbox.
- `baselines/` — saved runs. `baseline.md` is the reference the gate compares against; `run-<date>.md` are individual runs.
- `calibration/` — gold human labels (`gold.md`) + stored artifacts (`artifacts/`) for `/wf-calibrate`, which validates that `wf-judge` agrees with you before you trust the gate.

## What it does
**Stage evals** — invoke one agent on a fixture and have `wf-judge` score its output against the case rubric (binary pass/fail + 0–1 per dimension). Five stages:
- `spec` → judges `wf-spec-builder`'s spec (resolves decisions, stays at spec altitude, verifiable criteria).
- `decision` → judges `wf-spec-builder`'s recorded decision on a research/spike ticket (commits, evidence-grounded, no pre-written code).
- `plan` → judges `wf-planner`'s plan (right files, mirrors patterns, covers criteria, surgical, surfaces ambiguity).
- `execute` → judges `wf-executor`'s diff + whether the fixture's tests pass (sandboxed).
- `review` → judges `wf-reviewer` against a planted-flaw diff (case ships a `## MUTATION`): catches the real bug and the hollow test, no noise.

Fully offline: no Linear, no GitHub, no PRs. All project code runs through `wf-exec`.

## Adding a case
Copy a `cases/*.md` file. Provide: `id`, `fixture`, `stages`, a `## TICKET` block (title + a spec-shaped description with acceptance criteria), and a `## RUBRIC:<stage>` block per stage with REQUIRED/NICE dimensions. Review cases also ship a `## MUTATION` (full post-change contents per `### file:` entry — the planted-flaw diff the reviewer sees). Keep fixtures dependency-free so they run in the sandbox.

## Cost
Each case spawns 1–2 agents + a judge. Iterate on one case id; run the full set before committing a prompt/model change.
