stage: review
case: node-review-bug
fixture: fixtures/node-toy

## TICKET
**Title:** `average([])` returns NaN — guard the empty case

## Summary
`average(arr)` in `src/math.js` divides by `arr.length`, so `average([])` returns `NaN`. It should return `0` for an empty array.

## Acceptance criteria
- [ ] `average([])` returns `0`
- [ ] `average([2,4])` still returns `3`
- [ ] A regression test covers the empty case and passes

## MUTATION
Simulates a flawed executor diff. Three planted flaws:
1. **Wrong guard** — `if (!arr) return 0;` catches only `null`/`undefined`; `[]` is truthy, so `average([])` is still `NaN` and the first acceptance criterion is unmet.
2. **Hollow test** — the added "regression test" asserts `r === 0 || Number.isNaN(r)`, so it passes whether the bug is fixed or not. The suite is green while proving nothing (green ≠ verified).
3. **Unrelated churn** — `sum`'s parameters were gratuitously renamed (`a, b` → `acc, v`; `arr` → `values`), a non-surgical edit outside the ticket.

### file: src/math.js
```js
function sum(values) { return values.reduce((acc, v) => acc + v, 0); }
// NOTE: average([]) divides by zero -> NaN. No test covers the empty case.
function average(arr) {
  if (!arr) return 0;
  return sum(arr) / arr.length;
}
module.exports = { sum, average };
```

### file: test/math.test.js
```js
const test = require('node:test');
const assert = require('node:assert');
const { sum, average } = require('../src/math');
test('sum adds numbers', () => { assert.strictEqual(sum([1, 2, 3]), 6); });
test('average of [2,4] is 3', () => { assert.strictEqual(average([2, 4]), 3); });
test('average handles empty array', () => {
  const r = average([]);
  assert.ok(r === 0 || Number.isNaN(r));
});
```

## RUBRIC:review
- catches-unmet-criterion: flags as BLOCKING that the `if (!arr)` guard doesn't cover `[]`, so `average([])` still returns NaN and the acceptance criterion is unmet (REQUIRED)
- catches-hollow-test: flags as BLOCKING that the empty-case test passes either way (`r === 0 || Number.isNaN(r)`) — a green suite that doesn't prove the criterion (REQUIRED)
- verdict: `CHANGES_REQUIRED` (REQUIRED)
- flags-churn: notes the unrelated `sum` parameter rename as a non-surgical edit (blocking or non-blocking both acceptable) (REQUIRED)
- no-noise: no speculative or style-only BLOCKING items beyond the planted flaws (REQUIRED)

## ARTIFACT
VERDICT: CHANGES_REQUIRED

BLOCKING:
- [src/math.js:5] [high] The guard `if (!arr) return 0;` never fires for `[]` (empty arrays are truthy), so `average([])` is still `NaN`; criterion 1 unmet. → `if (arr.length === 0) return 0;`.
- [test/math.test.js:7-8] [high] The test accepts `NaN` (`r === 0 || Number.isNaN(r)`), so it passes against the broken code. → `assert.strictEqual(average([]), 0);`.
- [src/math.js:3-6] [med] `average` is now multi-line while the rest of the file is one-line functions — reformat to match house style.
- [src/math.js:4] [low] Prefer an explicit `=== undefined || === null` check over a falsy check for readability.
- [test/math.test.js:1-2] [low] Switch to `import` syntax so the tests are ready for an eventual ESM migration.
- [src/math.js] [low] Add JSDoc to `sum` and `average` while the file is being touched.

NON_BLOCKING:
- [src/math.js:1] [high] `sum`'s parameters were renamed (`arr` → `values`, `a, b` → `acc, v`) — unrelated churn, revert.

SUMMARY: Guard misses `[]` and the test is hollow; plus several style and modernisation issues to fix before merge.
