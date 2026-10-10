stage: plan
case: node-feature
fixture: fixtures/node-toy

## TICKET
**Title:** Add a `product(arr)` helper to the math utils

## Summary
Add a `product(arr)` function alongside `sum`/`average` in `src/math.js` that returns the product of all numbers in the array.

## Acceptance criteria
- [ ] `product([2,3,4])` returns `24`
- [ ] `product([])` returns `1` (empty product identity)
- [ ] A test in `test/math.test.js` covers both cases and passes
- [ ] `product` is exported from `src/math.js`

## Implementation notes
- Mirror the existing `sum` style (a `reduce`), export via `module.exports`.

## RUBRIC:plan
- targets-right-file: plan modifies `src/math.js` and `test/math.test.js`, nothing else (REQUIRED)
- mirrors-pattern: plan says to follow the existing `reduce`/export style (REQUIRED)
- covers-criteria: plan's steps + tests map to all 4 acceptance criteria incl. the empty=1 edge (REQUIRED)
- surgical: no speculative extra functions, configs, or refactors (REQUIRED)

## ARTIFACT
STATUS: PLAN

GOAL: Add and export `product(arr)` from `src/math.js`, using the same one-line `reduce` style as `sum`. `product([2,3,4])` must return 24 and `product([])` must return 1. Both cases need a passing test in `test/math.test.js`.

CONTEXT_PACK:
- files in play: src/math.js — one-line `sum` and `average`, ending in `module.exports = { sum, average };`; test/math.test.js — `node:test` + `node:assert`, imports `{ sum }`, one-line tests with `assert.strictEqual`
- patterns to follow: one-line function declarations, e.g. `function sum(arr) { return arr.reduce((a, b) => a + b, 0); }`; single `module.exports` object literal; one-line tests
- commands: test=`npm test` (single file: `node --test test/math.test.js`)
- gotchas: `average([])`'s NaN NOTE is out of scope — leave it. The `reduce` needs initial value `1`, otherwise `[].reduce` throws on the empty array.

PLAN:
1. src/math.js — add `product` after `average` as a one-line `reduce` with initial value `1`; add it to `module.exports` → verify: `product([2,3,4])` is 24 and `product([])` is 1
2. test/math.test.js — import `product`; add one test for `[2,3,4]` → 24 and one for `[]` → 1 → verify: `node --test test/math.test.js` reports 3 passing

TESTS: the two new tests cover criteria 1–3; importing `product` from `src/math` proves criterion 4.
RISKS: don't fix `average([])` while in the file.
SPEC_GAPS: none
MANUAL_DRIFT: none
