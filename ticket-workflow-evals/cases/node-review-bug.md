id: node-review-bug
fixture: fixtures/node-toy
stages: review

## TICKET
**Title:** `average([])` returns NaN — guard the empty case

**Description**
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
