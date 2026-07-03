# Ticket-Workflow Eval Harness

A regression gate for the agent pipeline. Run `/wf-eval` after changing any agent prompt, model, or the flow, to catch silent quality drops.

## Layout
- `cases/*.md` — seed cases: a mock ticket + the fixture it runs against + a per-stage rubric.
- `fixtures/` — tiny, git-initialized throwaway repos the agents act on (`node-toy`, `py-toy`). Dependency-free; tests run via stdlib (`node --test`, `python3 -m unittest`) so they work inside the no-network sandbox.
- `baselines/` — saved runs. `baseline.md` is the reference the gate compares against; `run-<date>.md` are individual runs.
- `calibration/` — gold human labels (`gold.md`) + stored artifacts (`artifacts/`) for `/wf-calibrate`, which validates that `wf-judge` agrees with you before you trust the gate.

## What it does
**Stage evals** — invoke one agent on a fixture and have `wf-judge` score its output against the case rubric (binary pass/fail + 0–1 per dimension). Two stages:
- `plan` → judges `wf-planner`'s plan (right files, mirrors patterns, covers criteria, surgical, surfaces ambiguity).
- `execute` → judges `wf-executor`'s diff + whether the fixture's tests pass (sandboxed).

Fully offline: no Linear, no GitHub, no PRs. All project code runs through `wf-exec`.

## Adding a case
Copy a `cases/*.md` file. Provide: `id`, `fixture`, `stages`, a `## TICKET` block (title + a spec-shaped description with acceptance criteria), and `## RUBRIC:plan` / `## RUBRIC:execute` blocks with REQUIRED/NICE dimensions. Keep fixtures dependency-free so they run in the sandbox.

## Cost
Each case spawns 1–2 agents + a judge. Iterate on one case id; run the full set before committing a prompt/model change.
