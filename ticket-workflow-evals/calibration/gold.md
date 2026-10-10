# Judge calibration — gold labels

Ground-truth human verdicts for `/wf-calibrate`. One row per artifact in `artifacts/`.

- **human** — `PASS` or `FAIL`, *your* verdict, decided blind (before seeing what the judge says).
- **reason** — one line; why. Used only in the disagreement report, never shown to the judge.
- **probe-group** — optional tag. Give two+ artifacts the SAME tag when they're equivalent in correctness but differ only in length/style — the judge must rate them identically (verbosity / self-preference probe). Leave blank otherwise.

Aim for **~15–20 artifacts, roughly half PASS / half FAIL**, including deliberate bad ones (missed criterion, hollow or mocked test, over-engineering / scope creep). The two rows below are worked examples — keep or replace them.

| artifact                        | human | reason | probe-group |
|---------------------------------|-------|--------|-------------|
| example-plan-good.md            | PASS  | finds root cause, minimal guard, adds regression test |  |
| example-plan-bad.md             | FAIL  | omits required regression test; over-reaches scope |  |
| spec-median-good.md             | PASS  | real 2026-10-03 output: decisions resolved, pointer altitude, verifiable AC | spec-len |
| spec-median-terse.md            | PASS  | same decisions/AC/scope as spec-median-good, half the words | spec-len |
| spec-median-code-dump.md        | FAIL  | implementation notes embed a full median() body + line anchor (spec-altitude) |  |
| spec-median-open-question.md    | FAIL  | even-length behaviour left as TBD open question (resolves-decisions) |  |
| decision-average-good.md        | PASS  | real output (trimmed): commits to RangeError, evidence from code, standalone headline |  |
| decision-average-hedge.md       | FAIL  | lists all three options, never commits (decides) |  |
| decision-average-with-code.md   | FAIL  | pre-writes the average() fix and test code (no-code) |  |
| plan-vague-narrow.md            | PASS  | real output: narrows to the documented defect, SPEC_GAPS leads with run /wf-spec; the invented throw is flagged reversible — acceptable |
| plan-vague-overreach.md         | FAIL  | invents 8 new helpers + validation + README; SPEC_GAPS none (surfaces-ambiguity, no-overreach) |  |
| plan-product-good.md            | PASS  | real output: right files, reduce with initial 1, both cases tested | plan-len |
| plan-product-verbose.md         | PASS  | identical steps to plan-product-good, ~3x the prose | plan-len |
| plan-product-missed-edge.md     | FAIL  | reduce has no initial value (product([]) throws) and no empty-case test (covers-criteria) |  |
| exec-bugfix-good.md             | PASS  | real output: length guard, strict regression test, 3/3 green |  |
| exec-bugfix-hollow-test.md      | FAIL  | empty-case test asserts typeof number — NaN passes; green proves nothing (regression-test) |  |
| exec-bugfix-red.md              | FAIL  | falsy guard misses []; harness shows 1 failing test (correct, tests-pass) |  |
| exec-bugfix-non-surgical.md     | FAIL  | correct + green but rewrites sum, adds use strict/JSDoc, converts to arrows (surgical) |  |
| review-good.md                  | PASS  | real output: both planted flaws BLOCKING, churn + stale NOTE non-blocking | review-len |
| review-good-long-nonblocking.md | PASS  | same BLOCKING as review-good + 5 low-confidence NON_BLOCKING notes (coverage-first: must not be debited) | review-len |
| review-buries-bug.md            | FAIL  | catches both flaws but adds 4 style/speculative BLOCKING items (no-noise) |  |
| review-misses-hollow-test.md    | FAIL  | calls the hollow test fine; only the guard is BLOCKING (catches-hollow-test) |  |
