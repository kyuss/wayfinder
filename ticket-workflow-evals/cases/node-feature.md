id: node-feature
fixture: fixtures/node-toy
stages: plan, execute

## TICKET
**Title:** Add a `product(arr)` helper to the math utils

**Description**
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

## RUBRIC:execute
- correct: `product` returns the product; `product([])` === 1 (REQUIRED)
- tested: a test covers both the normal and empty case (REQUIRED)
- tests-pass: `node --test` is green (REQUIRED)
- surgical: diff touches only the two files; no unrelated edits (REQUIRED)
