stage: spec
case: spec-altitude
fixture: fixtures/node-toy

## TICKET
**Title:** Add a `median` helper to the math utils

**Description**
We have `sum` and `average` in the math utils but no `median`. Add a `median(arr)` helper so callers can get the middle value of a list of numbers.

## RUBRIC:spec
- resolves-decisions: spec leaves zero open questions — the empty-array result and the even-length behavior (e.g. average of the two middles) are decided and stated as facts, so the planner won't need to ask (REQUIRED)
- spec-altitude: Implementation notes stay at pointer altitude. FAIL only on one of these three: a pre-written implementation (a function body or full code block), specific line-number anchors, or a numbered/ordered step-by-step build procedure. ALLOWED — do not fail or heavily penalize for these: declarative descriptions of decided behavior (e.g. "even length → mean of the two middles"), pattern/framework pointers (which file to edit, which existing test style to follow), and a brief inline idiom illustrating a named gotcha (e.g. `[...arr].sort((a,b)=>a-b)`). The test is whether an executor still has real "how" to figure out — not whether the prose is maximally terse (REQUIRED)
- verifiable-ac: every acceptance criterion is objectively verifiable — concrete inputs/outputs (e.g. `median([1,2,3])` is `2`) or a runnable command (REQUIRED)
- scoped: explicit in/out scope; no speculative extra helpers, configs, or refactors beyond `median` + its test (REQUIRED)
- concise-honest: spec is tight and high-signal, and any assumption it made (the edge-case choices) is recorded as a fact rather than left implicit (NICE)
- two-block-output: the output carries both sentinel sections in order — `--- TICKET_DESCRIPTION ---` (a Why/What/Success-criteria brief in plain language, free of implementation detail: no file paths, commands, or internal APIs) then `--- SPEC ---` (the full spec); acceptance criteria appear only inside the SPEC block (REQUIRED)

## ARTIFACT
STATUS: SPEC

--- TICKET_DESCRIPTION ---
## Why
Callers can already get the sum and the average of a list of numbers from the math utils, but not the median. Without a shared helper, each caller has to write its own, and those copies can disagree on edge cases.

## What
- Add a `median` helper next to the existing `sum` and `average` helpers.
- An odd-length list returns its middle value. An even-length list returns the average of the two middle values.
- The caller's list is left unchanged.
- An empty list gives "not a number", which matches what `average` already does.

## Success criteria
- Callers can import `median` from the math utils the same way they import `sum` and `average`.
- Unordered lists, negative numbers, decimals and multi-digit numbers all give the correct middle value.
- Tests cover odd, even, single-item and empty lists.

--- SPEC ---
## Summary
Add `median(arr)` to `src/math.js` and export it with `sum` and `average`, so callers can get the middle value of an array of numbers. Add unit tests for it.

## Acceptance criteria
- [ ] `src/math.js` exports `median` together with `sum` and `average`, using the same `module.exports` object.
- [ ] Odd-length input returns the middle element of the sorted values: `median([3, 1, 2]) === 2`.
- [ ] Even-length input returns the mean of the two middle sorted values: `median([4, 1, 3, 2]) === 2.5`.
- [ ] Sorting is numeric, not lexicographic: `median([10, 2, 1]) === 2` and `median([1, 2, 10, 20]) === 6`.
- [ ] Negatives and decimals work: `median([-5, 0, 5]) === 0` and `median([1.5, 2.5]) === 2`.
- [ ] Single-element input returns that element: `median([7]) === 7`.
- [ ] Empty input returns `NaN` and does not throw: `Number.isNaN(median([]))`.
- [ ] The input array is not mutated. After `const a = [3, 1, 2]; median(a);`, `a` still deep-equals `[3, 1, 2]`.
- [ ] `npm test` passes, including the existing `sum` test.

## Scope
**In:** a `median` function in `src/math.js`, its export, and tests in `test/math.test.js`.
**Out:** changing or fixing `average` (including its empty-array `NaN` behaviour, which the source comment notes), input validation or type checks for non-numbers, other statistics helpers, any dependency, and README or docs changes.

## Implementation notes
- Follow the existing style in `src/math.js`: a small plain CommonJS function, added to the existing `module.exports` object. No new files and no dependencies.
- Decision: empty input returns `NaN`. This matches `average([])` (the comment in `src/math.js` notes it returns `NaN`). It is the conservative, consistent choice, so the function does not throw.
- Decision: even-length input returns the arithmetic mean of the two middle values.
- Implementation — add this to `src/math.js` after `average` (line 3):
```js
function median(arr) {
  if (arr.length === 0) return NaN;
  const s = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}
```
- No validation of element types, because neither `sum` nor `average` validates.

## Verification
- Add `node:test` and `node:assert` cases to `test/math.test.js`, following the existing `sum` test pattern (`assert.strictEqual`, plus `assert.deepStrictEqual` for the non-mutation check, and `Number.isNaN` for the empty case). Cover every acceptance criterion above.
- Run `npm test`, which runs `node --test` with no dependencies and no network. All tests must pass.
