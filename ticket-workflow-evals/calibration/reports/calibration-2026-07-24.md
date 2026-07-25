# Judge calibration report — 2026-07-24

Judge: `wf-judge` (model alias `sonnet` → currently Claude Sonnet 5; prompt includes the 2026-07-24 coverage-first review-stage change).
Gold set: 2 artifacts (scaffold examples only).

## Per-artifact results

| artifact             | human | judge | score | match? | judge's note |
|----------------------|-------|-------|-------|--------|--------------|
| example-plan-good.md | PASS  | PASS  | 0.89  | ✅     | context pack cites a nonexistent `divide` function at src/math.js:12 — fabricated reference (not rubric-gated) |
| example-plan-bad.md  | FAIL  | FAIL  | 0.13  | ✅     | scope-creeps into refactoring/documenting the module while omitting the required regression test |

## Metrics

- **Agreement:** 2/2 = 100% (bar ≥90% — met, but see caveat)
- **FAIL-class precision:** 1/1 = 100% · **FAIL-class recall:** 1/1 = 100%
- **Bias probes:** none — no `probe-group` tags with >1 member exist in `gold.md`
- **Disagreements:** none

## Overall: NOT CALIBRATED — gold set insufficient

Agreement is perfect, but **n=2 is far below the ≥10 minimum** (target 15–20, ~50/50 PASS/FAIL). Two scaffold examples cannot establish that the `/wf-eval` gate is trustworthy — treat this run as a mechanics check only (parse → blind spawn → compare all worked).

### Work items to reach a real calibration

1. **Populate `gold.md` to 15–20 artifacts**, roughly half FAIL, including deliberate bad ones: missed criterion, hollow/mocked test, over-engineering/scope creep.
2. **Add review-stage artifacts — currently zero.** This is the highest-priority gap: the judge's review-stage rules changed on 2026-07-24 (coverage-first — `no-noise` now judged on the BLOCKING section only; long NON_BLOCKING lists must not be debited). That change is completely unvalidated. Include at least: a reviewer output that catches planted flaws with a long-but-clean NON_BLOCKING list (human PASS — probes the new no-debit rule), one that buries the real bug under speculative BLOCKING items (human FAIL), and one that misses a planted flaw (human FAIL).
3. **Add probe groups** — pairs equivalent in correctness differing only in length/terseness, to expose verbosity/self-preference bias.
4. Positive observation worth keeping: on example-plan-good the judge independently caught a fabricated context-pack reference (nonexistent `divide` at src/math.js:12) without being prompted — evidence it reads the fixture rather than trusting artifact prose.

Re-run `/wf-calibrate` after populating the gold set, and again after any future judge model/prompt change (note: the `sonnet` alias makes judge model changes silent — recalibrate whenever Claude Code's alias moves).
