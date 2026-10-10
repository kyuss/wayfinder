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

GOAL: The objective of this ticket is to introduce a new helper function named `product(arr)` into the existing math utilities module at `src/math.js`. This helper should compute the multiplicative product of every number in the supplied array. Two behaviours are explicitly required by the acceptance criteria: calling `product([2,3,4])` must yield `24`, and calling `product([])` must yield `1`, which is the mathematical identity element for multiplication (the "empty product"). The new function must be exported so that consumers can import it, and both behaviours must be demonstrated by passing tests in `test/math.test.js`.

CONTEXT_PACK:
- files in play: The primary source file is src/math.js. It is a small CommonJS module that currently contains exactly two functions, `sum` and `average`, each written as a single-line function declaration, and it concludes with an export statement of the form `module.exports = { sum, average };`. The corresponding test file is test/math.test.js. It relies only on the Node standard library — specifically `node:test` for test registration and `node:assert` for assertions — currently imports only `{ sum }` from the module, and expresses each test as a single line using `assert.strictEqual`.
- patterns to follow: The established convention in this codebase is the one-line function declaration. The canonical example to mirror is `function sum(arr) { return arr.reduce((a, b) => a + b, 0); }`. All exports are gathered into a single `module.exports` object literal at the bottom of the file, and tests are likewise written as one-liners. Any new code should be indistinguishable in style from what is already there.
- commands: The full test suite is run with `npm test`. For faster, narrower verification of just this file, `node --test test/math.test.js` may be used instead.
- gotchas: Two points deserve attention. First, the file contains a NOTE comment documenting that `average([])` returns NaN; that behaviour is outside the scope of this ticket and both the code and its comment must be left exactly as they are. Second, and importantly, `Array.prototype.reduce` called on an empty array without an initial value throws a TypeError, so the reduce in `product` must be given an explicit initial value of `1` in order for the empty-array case to return the identity.

PLAN:
1. src/math.js — Immediately after the existing `average` function, add a new `product` function written as a single-line `reduce` that multiplies the accumulator by each element, supplying `1` as the initial value. Then extend the existing `module.exports` object literal so that it also includes `product`. → verify: confirm that `product([2,3,4])` evaluates to 24 and that `product([])` evaluates to 1.
2. test/math.test.js — Update the import line so that `product` is imported alongside `sum`. Then add two new one-line tests: the first asserts that `product([2,3,4])` strictly equals 24, and the second asserts that `product([])` strictly equals 1. → verify: running `node --test test/math.test.js` should report three passing tests in total and zero failures.

TESTS: Taken together, the two newly added tests directly exercise acceptance criteria one through three. Criterion four, the export requirement, is demonstrated implicitly but reliably by the fact that the test file obtains `product` through `require('../src/math')`; if it were not exported, the import would yield undefined and the tests would fail.
RISKS: The main risk is scope creep: while editing `src/math.js` it may be tempting to also correct the `average([])` NaN behaviour. This must be resisted, as it falls outside the ticket.
SPEC_GAPS: none
MANUAL_DRIFT: none
