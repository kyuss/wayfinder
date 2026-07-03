# Eval run — 2026-06-28 (post wf- rename + generalized prompts)

Cases: node-feature (plan, execute), node-bugfix (plan, execute), py-feature (plan, execute), ambiguous-spec (plan)
Context: first full run after renaming all agents/commands to the `wf-` prefix, generalizing the
executor/verifier/run-tickets prompts to be tech-agnostic, and adding the verification-policy/gates mechanism.

| case           | stage   | verdict | score | biggest weakness                                                        |
|----------------|---------|---------|-------|-------------------------------------------------------------------------|
| node-feature   | plan    | PASS    | 1.00  | none — exemplary                                                        |
| node-feature   | execute | PASS    | 1.00  | none                                                                    |
| node-bugfix    | plan    | PASS    | 0.95  | deletes the stale NOTE comment — minor, slightly beyond "surgical"      |
| node-bugfix    | execute | PASS    | 0.96  | stale-comment removal technically exceeds "only average changed"        |
| py-feature     | plan    | PASS    | 1.00  | none                                                                    |
| py-feature     | execute | PASS    | 1.00  | none                                                                    |
| ambiguous-spec | plan    | PASS    | 0.69  | did not explicitly flag "not implementation-ready" / recommend /wf-spec (NICE dim) |

Mean score: 0.94
Pass-rate: 7/7 (100%)

Baseline comparison (vs baselines/baseline.md):
- node-feature plan:    1.00 → 1.00  (no change)
- node-feature execute: 1.00 → 1.00  (no change)
- node-bugfix, py-feature, ambiguous-spec: new cases, not in baseline — recorded, nothing to diff.
- NO REGRESSIONS. The rename + prompt generalization did not degrade the pipeline; agent resolution (wf-*) works end-to-end.

Notes:
- ambiguous-spec correctly refused to invent scope (non-empty SPEC_GAPS, single code-documented fix, no sprawl); only the NICE "honest" dimension (explicitly recommend /wf-spec) was missed — candidate prompt nudge for wf-planner, not a regression.
- Found a wf-exec watchdog bug while capturing results: piping wf-exec output could orphan the timeout `sleep` holding the pipe write-end (downstream `| tail` hangs). Fix tracked separately; not a pipeline-quality issue.
