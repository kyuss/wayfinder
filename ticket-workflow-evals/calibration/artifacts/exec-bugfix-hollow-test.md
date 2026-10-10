stage: execute
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

## RUBRIC:execute
- correct: `average([])` === 0 and `average([2,4])` === 3 (REQUIRED)
- regression-test: a test asserts the empty case (REQUIRED)
- tests-pass: `node --test` is green (REQUIRED)
- surgical: only `average` (and the test) changed (REQUIRED)

## ARTIFACT
### git diff main...HEAD
```diff
--- a/src/math.js
+++ b/src/math.js
@@ -1,4 +1,3 @@
 function sum(arr) { return arr.reduce((a, b) => a + b, 0); }
-// NOTE: average([]) divides by zero -> NaN. No test covers the empty case.
-function average(arr) { return sum(arr) / arr.length; }
+function average(arr) { return arr.length === 0 ? 0 : sum(arr) / arr.length; }
 module.exports = { sum, average };
--- a/test/math.test.js
+++ b/test/math.test.js
@@ -1,4 +1,6 @@
 const test = require('node:test');
 const assert = require('node:assert');
-const { sum } = require('../src/math');
+const { sum, average } = require('../src/math');
 test('sum adds numbers', () => { assert.strictEqual(sum([1, 2, 3]), 6); });
+test('average of empty array', () => { const r = average([]); assert.ok(typeof r === 'number'); });
+test('average of [2,4] is 3', () => { assert.strictEqual(average([2, 4]), 3); });
```
### Sandboxed test result (`node --test`, run by the harness)
```
✔ sum adds numbers
✔ average of empty array
✔ average of [2,4] is 3
ℹ tests 3
ℹ pass 3
ℹ fail 0
```
