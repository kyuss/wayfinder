# Judge calibration report — 2026-10-03

Judge: `wf-judge` (model alias `sonnet` → now Claude Sonnet 5.5; first calibration since the alias moved off Sonnet 5). Judge prompt unchanged since 2026-07-24.
Gold set: 2 artifacts (scaffold examples only).

## Per-artifact results

| artifact             | human | judge | score | match? | judge's note |
|----------------------|-------|-------|-------|--------|--------------|
| example-plan-good.md | PASS  | PASS  | 0.94  | ✅     | context pack cites a nonexistent `divide` at src/math.js:12 — hallucinated pattern reference (not rubric-gated) |
| example-plan-bad.md  | FAIL  | FAIL  | 0.15  | ✅     | no regression test; refactors sum/product + JSDoc — violates no-overreach |

Score drift vs 2026-07-24 (Sonnet 5): good 0.89 → 0.94, bad 0.13 → 0.15. Verdicts identical; the judge again independently caught the fabricated `divide` reference by reading the fixture.

## Metrics

- **Agreement:** 2/2 = 100% (bar ≥90% — met, but see caveat)
- **FAIL-class precision:** 1/1 = 100% · **FAIL-class recall:** 1/1 = 100%
- **Bias probes:** none — no `probe-group` tags with >1 member in `gold.md`
- **Disagreements:** none

## Overall: NOT CALIBRATED — gold set insufficient

Mechanics check passes on Sonnet 5.5 and verdicts are stable across the model change, but **n=2 is far below the ≥10 minimum**. The work items from the 2026-07-24 report still stand unchanged: populate `gold.md` to 15–20 artifacts (~50/50, incl. hollow-test / missed-criterion / over-engineering FAILs), add review-stage artifacts (currently zero — the coverage-first review rules remain unvalidated), and add probe groups.
