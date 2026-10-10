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
The math utils have `sum` and `average` but no `median`, so callers write their own and disagree on edge cases.

## What
- Add a shared `median` helper.
- Odd length → middle value; even length → mean of the two middles; empty → not a number (like `average`).
- The caller's list is not changed.

## Success criteria
- `median` is importable like `sum` and `average`.
- Odd, even, single-item and empty lists all behave as described.

--- SPEC ---
## Summary
Add and export `median(arr)` in `src/math.js`, with tests.

## Acceptance criteria
- [ ] Exported from `src/math.js` alongside `sum` and `average`.
- [ ] `median([3, 1, 2]) === 2`; `median([4, 1, 3, 2]) === 2.5`.
- [ ] Numeric sort: `median([10, 2, 1]) === 2`.
- [ ] `median([7]) === 7`; `Number.isNaN(median([]))`.
- [ ] Input not mutated: `a = [3, 1, 2]` is unchanged after `median(a)`.
- [ ] `npm test` passes.

## Scope
**In:** `median`, its export, its tests. **Out:** changes to `average`, input validation, other helpers, dependencies.

## Implementation notes
- Plain CommonJS function in `src/math.js`, added to the existing `module.exports`.
- Decisions: empty → `NaN` (matches `average([])`); even length → mean of the two middles.
- Gotcha: default `sort()` is lexicographic and in-place — sort a numeric copy (`[...arr].sort((a, b) => a - b)`).

## Verification
- `node:test` cases in `test/math.test.js` for every criterion; run `npm test`.
