# BASELINE — promoted from run-2026-10-03.md (supersedes the 2026-07-24 baseline)

> Current gold reference the `/wf-eval` gate diffs against — a promoted copy of `run-2026-10-03.md` (first Claude 5.5 measurement). Dated `run-*.md` files are the immutable history.

Full set, all stages: spec-altitude (spec), spike-decision (decision), ambiguous-spec (plan),
node-bugfix (plan, execute), node-feature (plan, execute), py-feature (plan, execute),
node-review-bug (review).

Context: first full-set measurement after two coupled changes —
- **Model alias drift (Claude 5.5):** all agents run via aliases; `opus` → Claude Opus 5.5,
  `sonnet` → Claude Sonnet 5.5 (judge included), `haiku` → Haiku 4.5 at run time. The previous
  baseline (2026-07-24) ran on Opus 5 / Sonnet 5.
- **Prompt doctoring for 5.5:** wf-eval plan-stage EVAL flag now forbids `STATUS: NEEDS_INPUT`
  (it previously forbade AskUserQuestion, a tool the planner doesn't have); wf-run / wf-spec
  update-suppressor lines rewritten positively + a per-stage status line in wf-run; wf-executor
  gained a "syntax-only / timed-out check isn't verification" rule.
Judge calibration re-run first (calibration-2026-10-03.md): 2/2 agreement on Sonnet 5.5, gold set
still below the 10-artifact minimum.

| case            | stage    | verdict | score | biggest weakness                                                   |
|-----------------|----------|---------|-------|--------------------------------------------------------------------|
| spec-altitude   | spec     | PASS    | 0.95  | none (minor: brief Success criteria overlap the AC in plain language) |
| spike-decision  | decision | PASS    | 0.93  | Compatibility / caller-impact padding — NICE verbosity debit        |
| ambiguous-spec  | plan     | PASS    | 0.82  | commits to an invented behavior (throw RangeError) for a vague ticket, though flagged reversible + "run /wf-spec" (mean of 0.76 / 0.88, see notes) |
| node-bugfix     | plan     | PASS    | 0.99  | none (removes the stale NOTE comment — judged justified)            |
| node-bugfix     | execute  | PASS    | 0.98  | none — harness ran node --test sandboxed (3/3)                       |
| node-feature    | plan     | PASS    | 1.00  | none                                                               |
| node-feature    | execute  | PASS    | 1.00  | none — harness ran node --test sandboxed (3/3)                       |
| py-feature      | plan     | PASS    | 0.99  | none                                                               |
| py-feature      | execute  | PASS    | 1.00  | none — harness ran unittest sandboxed (2/2)                          |
| node-review-bug | review   | PASS    | 1.00  | none — both planted flaws BLOCKING, churn + stale NOTE non-blocking  |

**Pass rate:** 10/10. **Mean score:** 0.965 (baseline 0.977).

## Regression gate vs baseline (2026-07-24, Opus 5 / Sonnet 5)
No regressions (no PASS→FAIL; no drop > 0.15).
- spec-altitude spec:     0.92 → 0.95 (+0.03)
- spike-decision:         0.95 → 0.93 (−0.02)
- ambiguous-spec plan:    0.91 → 0.82 (−0.09; first run alone was 0.76, exactly −0.15)
- node-bugfix plan:       1.00 → 0.99 · execute 1.00 → 0.98
- node-feature plan/exec: 1.00 → 1.00 / 1.00
- py-feature plan/exec:   1.00 → 0.99 / 1.00
- node-review-bug review: 0.98 → 1.00 (+0.02) — the prior stale-NOTE third BLOCKING item is now
  correctly routed to NON_BLOCKING

## Notes
- **ambiguous-spec was run twice.** Both planner runs made the same call (narrow to the documented
  `average([])` defect, throw RangeError, lead SPEC_GAPS with "run /wf-spec"); the judge scored the
  near-identical artifacts 0.76 and 0.88. So the dip is judge variance on a NICE-heavy case, not a
  behavior change — but this case is the most sensitive in the set and the one to watch. Confound:
  the new EVAL flag ("produce your best STATUS: PLAN") and the Opus 5.5 swap landed together.
- **Executor attribution trailer:** all three executor runs wrote `Co-Authored-By: Claude Sonnet 5.5
  <noreply@anthropic.com>` (from Claude Code's injected attribution reminder) instead of the
  `Co-Authored-By: Claude <noreply@anthropic.com>` that wf-executor.md specifies. Not rubric-gated;
  decide whether to pin the generic trailer harder in the executor prompt or accept the harness one.
- The judge again caught the calibration artifact's fabricated `divide` reference by reading the
  fixture. Several judges this run noted they judged from the artifact without reading the fixture
  (plan/review stages) — acceptable for these cases, but worth watching as the rubric grows.
