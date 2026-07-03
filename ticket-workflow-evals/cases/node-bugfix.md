id: node-bugfix
fixture: fixtures/node-toy
stages: plan, execute

## TICKET
**Title:** `average([])` returns NaN — guard the empty case

**Description**
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

## RUBRIC:execute
- correct: `average([])` === 0 and `average([2,4])` === 3 (REQUIRED)
- regression-test: a test asserts the empty case (REQUIRED)
- tests-pass: `node --test` is green (REQUIRED)
- surgical: only `average` (and the test) changed (REQUIRED)
