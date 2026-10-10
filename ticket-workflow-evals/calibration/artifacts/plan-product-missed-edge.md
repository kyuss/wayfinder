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

GOAL: Add and export `product(arr)` from `src/math.js` in the same one-line `reduce` style as `sum`.

CONTEXT_PACK:
- files in play: src/math.js — one-line `sum` and `average`, `module.exports = { sum, average };`; test/math.test.js — `node:test`, one-line tests
- patterns to follow: `function sum(arr) { return arr.reduce((a, b) => a + b, 0); }`; single `module.exports` literal
- commands: test=`npm test`
- gotchas: leave `average([])`'s NOTE alone

PLAN:
1. src/math.js — add `function product(arr) { return arr.reduce((a, b) => a * b); }` after `average`; add it to `module.exports` → verify: `product([2,3,4])` is 24
2. test/math.test.js — import `product`; add `test('product multiplies numbers', () => { assert.strictEqual(product([2, 3, 4]), 24); });` → verify: `npm test` green

TESTS: the new test covers the product case; importing it proves the export.
RISKS: none
SPEC_GAPS: none
MANUAL_DRIFT: none
