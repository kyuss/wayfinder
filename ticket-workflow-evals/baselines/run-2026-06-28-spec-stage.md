# Eval run — 2026-06-28 (new spec stage + wf-spec-builder altitude tightening)

Scope: spec stage only (new). Added `STAGE=spec` to the harness and a `spec-altitude` case
to validate the wf-spec-builder change that keeps specs at pointer altitude (no planner/executor
overreach) while still resolving every decision. Planner/executor were not touched and not re-run
this pass — see baseline.md / run-2026-06-28.md for the plan/execute verdicts.

Context: wf-spec-builder.md `Implementation notes` shape + `Rules for the spec` rewritten so the
spec records decisions as facts (the lever that keeps the planner from asking) but leaves the
ordered "how" to the planner/executor. Calibrated to a **pragmatic altitude floor** (user decision):
FAIL only on a pre-written implementation, line-number anchors, or a numbered/ordered build
procedure; a brief inline idiom illustrating a named gotcha is allowed.

| case          | stage | verdict | score | biggest weakness                                              |
|---------------|-------|---------|-------|--------------------------------------------------------------|
| spec-altitude | spec  | PASS    | 0.92  | minor verbosity in implementation notes; no FAIL trigger hit |

Mean score: 0.92
Pass-rate: 1/1 (100%)

Discriminator check (negative control, not a permanent case):
- A deliberately over-detailed spec for the same ticket — full function body in a fenced code
  block, line-number anchors ("at line 14/18/22/1"), and a numbered 4-step build procedure —
  scored `spec-altitude` FAIL 0.00, OVERALL FAIL 0.64. Confirms the rubric still hard-fails the
  Montresor-style "spec = full implementation plan" the change targets.

Baseline comparison (vs baselines/baseline.md):
- spec-altitude is a NEW case + NEW stage, not in baseline — recorded, nothing to diff.
- NO REGRESSIONS. Planner/executor unchanged and out of scope for this pass.

Notes:
- Iteration history: the unmodified-altitude spec first FAILed spec-altitude (inline idioms +
  exact assert calls); two prompt tightenings + a rubric calibration to the pragmatic floor landed
  the good spec at PASS while the negative control stays a hard FAIL.
- Follow-up worth considering: a second spec case on a more decision-heavy ticket (where the right
  move is to RESOLVE conservatively rather than punt) would also guard the "planner stays quiet"
  property from the resolves-decisions side.
