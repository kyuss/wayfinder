stage: plan
case: node-bugfix
fixture: fixtures/node-toy

## TICKET
**Title:** `average([])` returns NaN — guard the empty case

## Summary
`average(arr)` in `src/math.js` divides by `arr.length`, so `average([])` returns `NaN`. It should return `0` for an empty array. No test currently covers this.

## Acceptance criteria
- [ ] `average([])` returns `0`
- [ ] `average([2,4])` still returns `3`
- [ ] A regression test covers the empty case and passes

## RUBRIC:plan
- finds-root-cause: plan identifies the divide-by-zero in `average` (REQUIRED)
- minimal-fix: plan guards the empty case (return 0) without rewriting unrelated logic (REQUIRED)
- adds-regression-test: plan adds a test for `average([])` (REQUIRED)
- no-overreach: doesn't also "improve" sum/product or refactor the module (REQUIRED)

## ARTIFACT
GOAL: `average([])` returns 0 (not NaN) without changing other behavior, proven by a test.

CONTEXT_PACK:
- files in play: src/math.js — `average` divides sum by `arr.length`; test/math.test.js — node:test specs
- patterns to follow: guard clauses at function top (see `divide` in src/math.js:12); tests use node:test + node:assert
- commands: test=`node --test`
- gotchas: none

PLAN:
1. src/math.js — in `average`, return 0 when `arr.length === 0` before the division → verify: average([]) === 0
2. test/math.test.js — add a test asserting average([]) === 0 and average([2,4]) === 3 → verify: node --test green

TESTS: add the empty-array case; keep the existing average test
RISKS: none
SPEC_GAPS: none
MANUAL_DRIFT: none
