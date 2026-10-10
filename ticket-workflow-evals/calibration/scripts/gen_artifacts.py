"""Generate calibration artifacts for wf-judge.

Sources: real outputs from the 2026-10-03 /wf-eval run (Opus 5.5 / Sonnet 5.5), plus
single-defect FAIL variants of those outputs and length-only probe variants.
"""
import pathlib, sys

OUT = pathlib.Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- tickets + rubrics
T_MEDIAN = """**Title:** Add a `median` helper to the math utils

**Description**
We have `sum` and `average` in the math utils but no `median`. Add a `median(arr)` helper so callers can get the middle value of a list of numbers."""

R_SPEC = """- resolves-decisions: spec leaves zero open questions — the empty-array result and the even-length behavior (e.g. average of the two middles) are decided and stated as facts, so the planner won't need to ask (REQUIRED)
- spec-altitude: Implementation notes stay at pointer altitude. FAIL only on one of these three: a pre-written implementation (a function body or full code block), specific line-number anchors, or a numbered/ordered step-by-step build procedure. ALLOWED — do not fail or heavily penalize for these: declarative descriptions of decided behavior (e.g. "even length → mean of the two middles"), pattern/framework pointers (which file to edit, which existing test style to follow), and a brief inline idiom illustrating a named gotcha (e.g. `[...arr].sort((a,b)=>a-b)`). The test is whether an executor still has real "how" to figure out — not whether the prose is maximally terse (REQUIRED)
- verifiable-ac: every acceptance criterion is objectively verifiable — concrete inputs/outputs (e.g. `median([1,2,3])` is `2`) or a runnable command (REQUIRED)
- scoped: explicit in/out scope; no speculative extra helpers, configs, or refactors beyond `median` + its test (REQUIRED)
- concise-honest: spec is tight and high-signal, and any assumption it made (the edge-case choices) is recorded as a fact rather than left implicit (NICE)
- two-block-output: the output carries both sentinel sections in order — `--- TICKET_DESCRIPTION ---` (a Why/What/Success-criteria brief in plain language, free of implementation detail: no file paths, commands, or internal APIs) then `--- SPEC ---` (the full spec); acceptance criteria appear only inside the SPEC block (REQUIRED)"""

T_SPIKE = """**Title:** Spike: decide the empty-input contract for `average`

**Description**
Before we harden the math utils, we need to commit to what `average([])` should do — right now it's unspecified. Candidates: **throw** a `RangeError`, **return `0`**, or **return `null`**. Pick one and record the rationale so the follow-up hardening ticket can just implement it. Timeboxed decision; no code change in this ticket.

**Deliverable**
- [ ] A recorded decision (chosen behavior + why) that unblocks the `average` hardening ticket."""

R_DECISION = """- decides: returns `STATUS: DECISION` and commits to exactly one contract (throw / `0` / `null`) — not `STATUS: NEEDS_INPUT`, and not a hedge that lists options without choosing one (REQUIRED)
- evidence-backed: the rationale cites concrete evidence from the fixture — e.g. the current `NaN` behavior + in-code NOTE, that `sum([])` returns `0` (a consistency anchor), and/or that no existing test or caller constrains it — rather than generic hand-waving (REQUIRED)
- standalone-headline: the `**Decision:**` line is self-contained — it states the chosen contract AND the crux reason, so a dependent ticket reading only that one line knows what was decided and why (REQUIRED)
- preserves-original: the output is the original description preserved with a `## Decision` section appended — not a wholesale rewrite of the ticket, and not a `NEEDS_INPUT` batch (REQUIRED)
- no-code: stays a decision — does NOT write the actual `average` fix (a function body / diff) or a numbered step-by-step implementation procedure; recording the chosen behavior declaratively is expected, pre-writing the code is not (REQUIRED)
- concise-honest: decision is tight and high-signal; any residual scope boundary (e.g. that `sum` is out of scope) is stated rather than left implicit (NICE)"""

T_VAGUE = """**Title:** Make the math utils better

**Description**
The math utilities feel a bit basic. Let's improve them and make them more robust."""

R_VAGUE = """- surfaces-ambiguity: planner does NOT silently invent a concrete feature set; it flags the under-specification (REQUIRED)
- asks-or-gaps: planner asks a clarifying question OR reports a non-empty `SPEC_GAPS` rather than guessing (REQUIRED)
- no-overreach: planner does not produce a sprawling multi-feature plan from a vague prompt (REQUIRED)
- honest: planner is explicit that the ticket isn't implementation-ready (good: recommends /wf-spec) (NICE)"""

T_PRODUCT = """**Title:** Add a `product(arr)` helper to the math utils

## Summary
Add a `product(arr)` function alongside `sum`/`average` in `src/math.js` that returns the product of all numbers in the array.

## Acceptance criteria
- [ ] `product([2,3,4])` returns `24`
- [ ] `product([])` returns `1` (empty product identity)
- [ ] A test in `test/math.test.js` covers both cases and passes
- [ ] `product` is exported from `src/math.js`

## Implementation notes
- Mirror the existing `sum` style (a `reduce`), export via `module.exports`."""

R_PRODUCT_PLAN = """- targets-right-file: plan modifies `src/math.js` and `test/math.test.js`, nothing else (REQUIRED)
- mirrors-pattern: plan says to follow the existing `reduce`/export style (REQUIRED)
- covers-criteria: plan's steps + tests map to all 4 acceptance criteria incl. the empty=1 edge (REQUIRED)
- surgical: no speculative extra functions, configs, or refactors (REQUIRED)"""

T_BUGFIX = """**Title:** `average([])` returns NaN — guard the empty case

## Summary
`average(arr)` in `src/math.js` divides by `arr.length`, so `average([])` returns `NaN`. It should return `0` for an empty array. No test currently covers this.

## Acceptance criteria
- [ ] `average([])` returns `0`
- [ ] `average([2,4])` still returns `3`
- [ ] A regression test covers the empty case and passes"""

R_BUGFIX_EXEC = """- correct: `average([])` === 0 and `average([2,4])` === 3 (REQUIRED)
- regression-test: a test asserts the empty case (REQUIRED)
- tests-pass: `node --test` is green (REQUIRED)
- surgical: only `average` (and the test) changed (REQUIRED)"""

MUTATION = """Simulates a flawed executor diff. Three planted flaws:
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
```"""

R_REVIEW = """- catches-unmet-criterion: flags as BLOCKING that the `if (!arr)` guard doesn't cover `[]`, so `average([])` still returns NaN and the acceptance criterion is unmet (REQUIRED)
- catches-hollow-test: flags as BLOCKING that the empty-case test passes either way (`r === 0 || Number.isNaN(r)`) — a green suite that doesn't prove the criterion (REQUIRED)
- verdict: `CHANGES_REQUIRED` (REQUIRED)
- flags-churn: notes the unrelated `sum` parameter rename as a non-surgical edit (blocking or non-blocking both acceptable) (REQUIRED)
- no-noise: no speculative or style-only BLOCKING items beyond the planted flaws (REQUIRED)"""

# ---------------------------------------------------------------- shared artifact bodies
SPEC_GOOD = """STATUS: SPEC

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
- Gotcha: `Array.prototype.sort()` sorts lexicographically by default and sorts in place. Sort a copy with a numeric comparator, for example `[...arr].sort((a, b) => a - b)`, so you get the correct order and the caller's array is not mutated.
- No validation of element types, because neither `sum` nor `average` validates.

## Verification
- Add `node:test` and `node:assert` cases to `test/math.test.js`, following the existing `sum` test pattern (`assert.strictEqual`, plus `assert.deepStrictEqual` for the non-mutation check, and `Number.isNaN` for the empty case). Cover every acceptance criterion above.
- Run `npm test`, which runs `node --test` with no dependencies and no network. All tests must pass."""

SPEC_TERSE = """STATUS: SPEC

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
- `node:test` cases in `test/math.test.js` for every criterion; run `npm test`."""

DECISION_HEAD = """STATUS: DECISION

Before we harden the math utils, we need to commit to what `average([])` should do — right now it's unspecified. Candidates: **throw** a `RangeError`, **return `0`**, or **return `null`**. Pick one and record the rationale so the follow-up hardening ticket can just implement it. Timeboxed decision; no code change in this ticket.

**Deliverable**
- [ ] A recorded decision (chosen behavior + why) that unblocks the `average` hardening ticket.
"""

DECISION_GOOD = DECISION_HEAD + """
## Decision
**Decision:** `average([])` throws `RangeError("average() requires a non-empty array")`. The mean of an empty set is undefined, so failing loudly beats returning a plausible but wrong value.
**Rationale:** Right now `average` in `src/math.js` computes `sum(arr) / arr.length`, so `[]` gives `0/0` = `NaN`. The source comment says so, and no test covers the empty case. Return `0` is rejected: it's indistinguishable from a real zero average such as `average([-1, 1])`, and unlike `sum([])` (0 is the additive identity) division has no identity. Return `null` is rejected: it widens the return type and becomes `0` in arithmetic if a caller forgets to check. No caller in the repo relies on today's `NaN`.
**Scope:** in — the empty-array contract for `average`, error type and message; out — non-array/non-numeric input, any change to `sum` (`sum([])` stays `0`), NaN/Infinity handling for non-empty input.
**Compatibility:** `RangeError` is a standard built-in; the fixture has no dependencies.
**Unblocks:** the `average` hardening ticket."""

PLAN_PRODUCT_GOOD = """STATUS: PLAN

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
MANUAL_DRIFT: none"""

PLAN_PRODUCT_VERBOSE = """STATUS: PLAN

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
MANUAL_DRIFT: none"""

REVIEW_GOOD = """VERDICT: CHANGES_REQUIRED

BLOCKING:
- [src/math.js:5] [high] The guard `if (!arr) return 0;` never fires for `[]`, because an empty array is truthy. So `average([])` still computes `0 / 0` = `NaN`; acceptance criterion 1 is unmet. → Use `if (arr.length === 0) return 0;`.
- [test/math.test.js:7-8] [high] The regression test can't fail: `assert.ok(r === 0 || Number.isNaN(r))` accepts `NaN`, the very bug, so it passes against the broken code. Criterion 3 is unmet — green isn't verified. → `assert.strictEqual(average([]), 0);`.

NON_BLOCKING:
- [src/math.js:1] [high] Scope creep: `sum`'s parameters were renamed (`arr` → `values`, `a, b` → `acc, v`). Same behaviour, not needed for this ticket — revert.
- [src/math.js:2] [med] The `// NOTE: average([]) ... NaN` comment will be stale once fixed — remove it.

SUMMARY: The guard checks existence, not emptiness, so `average([])` is still NaN, and the new test accepts NaN so it hides the bug."""

EXEC_BUGFIX_DIFF_GOOD = """### git diff main...HEAD
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
+test('average of empty array is 0', () => { assert.strictEqual(average([]), 0); });
+test('average of [2,4] is 3', () => { assert.strictEqual(average([2, 4]), 3); });
```
### Sandboxed test result (`node --test`, run by the harness)
```
✔ sum adds numbers
✔ average of empty array is 0
✔ average of [2,4] is 3
ℹ tests 3
ℹ pass 3
ℹ fail 0
```"""

# ---------------------------------------------------------------- the set
# name -> (stage, case, fixture, ticket, rubric, artifact, extra_sections)
A = {}
NODE, PY = "fixtures/node-toy", "fixtures/py-toy"

# --- spec
A["spec-median-good"] = ("spec", "spec-altitude", NODE, T_MEDIAN, R_SPEC, SPEC_GOOD)
A["spec-median-terse"] = ("spec", "spec-altitude", NODE, T_MEDIAN, R_SPEC, SPEC_TERSE)
A["spec-median-code-dump"] = ("spec", "spec-altitude", NODE, T_MEDIAN, R_SPEC, SPEC_GOOD.replace(
"""- Gotcha: `Array.prototype.sort()` sorts lexicographically by default and sorts in place. Sort a copy with a numeric comparator, for example `[...arr].sort((a, b) => a - b)`, so you get the correct order and the caller's array is not mutated.""",
"""- Implementation — add this to `src/math.js` after `average` (line 3):
```js
function median(arr) {
  if (arr.length === 0) return NaN;
  const s = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid - 1] + s[mid]) / 2;
}
```"""))
A["spec-median-open-question"] = ("spec", "spec-altitude", NODE, T_MEDIAN, R_SPEC, SPEC_GOOD
    .replace("- [ ] Even-length input returns the mean of the two middle sorted values: `median([4, 1, 3, 2]) === 2.5`.\n", "")
    .replace(" and `median([1, 2, 10, 20]) === 6`", "")
    .replace(" and `median([1.5, 2.5]) === 2`", "")
    .replace("- Decision: even-length input returns the arithmetic mean of the two middle values.",
             "- Open question: for even-length input, should `median` return the lower middle, the upper middle, or their mean? TBD — the planner should confirm with the ticket owner.")
    .replace("An even-length list returns the average of the two middle values.", "Even-length lists are still to be decided."))

# --- decision
A["decision-average-good"] = ("decision", "spike-decision", NODE, T_SPIKE, R_DECISION, DECISION_GOOD)
A["decision-average-hedge"] = ("decision", "spike-decision", NODE, T_SPIKE, R_DECISION, DECISION_HEAD + """
## Decision
**Decision:** Each option is viable; the choice depends on how callers want to handle empty input.
**Rationale:** Today `average` computes `sum(arr) / arr.length`, so `[]` yields `NaN`, as the source comment notes. Throwing a `RangeError` is loud and keeps the return type a number. Returning `0` is consistent with `sum([])` returning `0` and never crashes callers. Returning `null` makes "no answer" explicit but widens the return type. Any of the three can be implemented in one line; the hardening ticket owner should pick whichever matches caller expectations.
**Scope:** in — the empty-array contract; out — non-array input, changes to `sum`.
**Compatibility:** all three are plain JavaScript with no dependencies.
**Unblocks:** the `average` hardening ticket.""")
A["decision-average-with-code"] = ("decision", "spike-decision", NODE, T_SPIKE, R_DECISION, DECISION_GOOD.replace(
"**Compatibility:**", """**Implementation:** replace `average` in `src/math.js` with:
```js
function average(arr) {
  if (arr.length === 0) throw new RangeError('average() requires a non-empty array');
  return sum(arr) / arr.length;
}
```
and add to `test/math.test.js`:
```js
test('average throws on empty', () => { assert.throws(() => average([]), RangeError); });
```
**Compatibility:**"""))

# --- plan (vague ticket)
A["plan-vague-narrow"] = ("plan", "ambiguous-spec", NODE, T_VAGUE, R_VAGUE, """STATUS: PLAN

GOAL: Make `src/math.js` more robust with the smallest defensible change: give `average([])` defined behaviour instead of silently returning `NaN`, and add the test coverage it lacks. No new features.

CONTEXT_PACK:
- files in play: src/math.js — one-line `sum` (reduce from 0) and `average` (`sum(arr) / arr.length`), NOTE on line 2 that `average([])` is NaN; test/math.test.js — only `sum` is tested
- patterns to follow: CommonJS, one-line functions, one-line `node:test` tests with `assert.strictEqual`
- commands: test=`node --test`
- gotchas: `sum([])` returns 0 and must stay that way. No new functions, no input-type validation.

PLAN:
1. src/math.js — make `average` throw a `RangeError` on an empty array; delete the stale NOTE → verify: `average([2,4])` is 3, `average([])` throws RangeError
2. test/math.test.js — import `average`; add tests: `sum([])` is 0, `average([1,2,3])` is 2, `average([])` throws RangeError → verify: `node --test` shows 4 passing

TESTS: step 2.
RISKS: "better/more robust" is undefined; this narrows it to the one defect the code's own NOTE documents. Throwing is a behaviour change; returning 0 or NaN instead is a one-line swap if the owner prefers.

SPEC_GAPS:
- ticket looks un-spec'd — run /wf-spec first. No acceptance criteria, no scope, no definition of "better" or "robust".
- What does "more robust" cover? → narrowed (eval mode, no questions) to the documented `average([])` defect plus missing tests.
- What should `average([])` do? → throw RangeError; flagged as reversible.

MANUAL_DRIFT: none""")
A["plan-vague-overreach"] = ("plan", "ambiguous-spec", NODE, T_VAGUE, R_VAGUE, """STATUS: PLAN

GOAL: Turn the math utils into a robust, well-rounded statistics module.

CONTEXT_PACK:
- files in play: src/math.js — `sum` and `average`; test/math.test.js — `node:test`
- patterns to follow: CommonJS, one-line functions
- commands: test=`node --test`
- gotchas: none

PLAN:
1. src/math.js — add input validation to every function: throw `TypeError` unless the argument is an array of finite numbers → verify: bad input throws
2. src/math.js — make `average([])` throw a `RangeError` → verify: throws
3. src/math.js — add `median`, `mode`, `min`, `max`, `variance` and `stddev` helpers, exported alongside the existing ones → verify: spot-check values
4. src/math.js — add `clamp(x, lo, hi)` and `round(x, digits)` utilities → verify: spot-check
5. test/math.test.js — add tests for every new function and every validation path → verify: `node --test` green
6. README.md — document the full API → verify: reads cleanly

TESTS: one test per function plus validation cases.
RISKS: none
SPEC_GAPS: none
MANUAL_DRIFT: none""")

# --- plan (product)
A["plan-product-good"] = ("plan", "node-feature", NODE, T_PRODUCT, R_PRODUCT_PLAN, PLAN_PRODUCT_GOOD)
A["plan-product-verbose"] = ("plan", "node-feature", NODE, T_PRODUCT, R_PRODUCT_PLAN, PLAN_PRODUCT_VERBOSE)
A["plan-product-missed-edge"] = ("plan", "node-feature", NODE, T_PRODUCT, R_PRODUCT_PLAN, """STATUS: PLAN

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
MANUAL_DRIFT: none""")

# --- execute (bugfix)
A["exec-bugfix-good"] = ("execute", "node-bugfix", NODE, T_BUGFIX, R_BUGFIX_EXEC, EXEC_BUGFIX_DIFF_GOOD)
A["exec-bugfix-hollow-test"] = ("execute", "node-bugfix", NODE, T_BUGFIX, R_BUGFIX_EXEC, EXEC_BUGFIX_DIFF_GOOD
    .replace("+test('average of empty array is 0', () => { assert.strictEqual(average([]), 0); });",
             "+test('average of empty array', () => { const r = average([]); assert.ok(typeof r === 'number'); });")
    .replace("✔ average of empty array is 0", "✔ average of empty array"))
A["exec-bugfix-red"] = ("execute", "node-bugfix", NODE, T_BUGFIX, R_BUGFIX_EXEC, """### git diff main...HEAD
```diff
--- a/src/math.js
+++ b/src/math.js
@@ -1,4 +1,3 @@
 function sum(arr) { return arr.reduce((a, b) => a + b, 0); }
-// NOTE: average([]) divides by zero -> NaN. No test covers the empty case.
-function average(arr) { return sum(arr) / arr.length; }
+function average(arr) { return !arr ? 0 : sum(arr) / arr.length; }
 module.exports = { sum, average };
--- a/test/math.test.js
+++ b/test/math.test.js
@@ -1,4 +1,6 @@
 const test = require('node:test');
 const assert = require('node:assert');
-const { sum } = require('../src/math');
+const { sum, average } = require('../src/math');
 test('sum adds numbers', () => { assert.strictEqual(sum([1, 2, 3]), 6); });
+test('average of empty array is 0', () => { assert.strictEqual(average([]), 0); });
+test('average of [2,4] is 3', () => { assert.strictEqual(average([2, 4]), 3); });
```
### Sandboxed test result (`node --test`, run by the harness)
```
✔ sum adds numbers
✖ average of empty array is 0
  AssertionError [ERR_ASSERTION]: Expected values to be strictly equal:
  NaN !== 0
✔ average of [2,4] is 3
ℹ tests 3
ℹ pass 2
ℹ fail 1
```""")
A["exec-bugfix-non-surgical"] = ("execute", "node-bugfix", NODE, T_BUGFIX, R_BUGFIX_EXEC, """### git diff main...HEAD
```diff
--- a/src/math.js
+++ b/src/math.js
@@ -1,4 +1,15 @@
-function sum(arr) { return arr.reduce((a, b) => a + b, 0); }
-// NOTE: average([]) divides by zero -> NaN. No test covers the empty case.
-function average(arr) { return sum(arr) / arr.length; }
-module.exports = { sum, average };
+'use strict';
+
+/** Adds every number in `values`. */
+const sum = (values) => values.reduce((total, value) => total + value, 0);
+
+/** Mean of `values`; 0 for an empty array. */
+const average = (values) => {
+  if (values.length === 0) return 0;
+  return sum(values) / values.length;
+};
+
+module.exports = { sum, average };
--- a/test/math.test.js
+++ b/test/math.test.js
@@ -1,4 +1,6 @@
 const test = require('node:test');
 const assert = require('node:assert');
-const { sum } = require('../src/math');
+const { sum, average } = require('../src/math');
 test('sum adds numbers', () => { assert.strictEqual(sum([1, 2, 3]), 6); });
+test('average of empty array is 0', () => { assert.strictEqual(average([]), 0); });
+test('average of [2,4] is 3', () => { assert.strictEqual(average([2, 4]), 3); });
```
### Sandboxed test result (`node --test`, run by the harness)
```
✔ sum adds numbers
✔ average of empty array is 0
✔ average of [2,4] is 3
ℹ tests 3
ℹ pass 3
ℹ fail 0
```""")

# --- review
REV = ("review", "node-review-bug", NODE, T_BUGFIX.replace(" No test currently covers this.", ""), R_REVIEW)
A["review-good"] = REV + (REVIEW_GOOD,)
A["review-good-long-nonblocking"] = REV + (REVIEW_GOOD.replace("\nSUMMARY:", """- [src/math.js:4] [low] `average(null)` now returns 0 rather than throwing; the ticket doesn't ask for null handling — possibly unintended, worth confirming.
- [src/math.js:3-6] [low] `average` is now multi-line while `sum` stays one-line; consider matching the file's one-line style.
- [test/math.test.js:6] [low] Consider a test with a negative or fractional mean (e.g. `average([-1, 2]) === 0.5`) for extra confidence.
- [test/math.test.js] [low] No test pins `sum([])` === 0, which `average`'s fix now implicitly depends on.
- [src/math.js:7] [low] `module.exports` is unchanged — fine, just confirming no export was dropped.

SUMMARY:"""),)
A["review-buries-bug"] = REV + ("""VERDICT: CHANGES_REQUIRED

BLOCKING:
- [src/math.js:5] [high] The guard `if (!arr) return 0;` never fires for `[]` (empty arrays are truthy), so `average([])` is still `NaN`; criterion 1 unmet. → `if (arr.length === 0) return 0;`.
- [test/math.test.js:7-8] [high] The test accepts `NaN` (`r === 0 || Number.isNaN(r)`), so it passes against the broken code. → `assert.strictEqual(average([]), 0);`.
- [src/math.js:3-6] [med] `average` is now multi-line while the rest of the file is one-line functions — reformat to match house style.
- [src/math.js:4] [low] Prefer an explicit `=== undefined || === null` check over a falsy check for readability.
- [test/math.test.js:1-2] [low] Switch to `import` syntax so the tests are ready for an eventual ESM migration.
- [src/math.js] [low] Add JSDoc to `sum` and `average` while the file is being touched.

NON_BLOCKING:
- [src/math.js:1] [high] `sum`'s parameters were renamed (`arr` → `values`, `a, b` → `acc, v`) — unrelated churn, revert.

SUMMARY: Guard misses `[]` and the test is hollow; plus several style and modernisation issues to fix before merge.""",)
A["review-misses-hollow-test"] = REV + ("""VERDICT: CHANGES_REQUIRED

BLOCKING:
- [src/math.js:5] [high] The guard `if (!arr) return 0;` never fires for `[]`, because an empty array is truthy, so `average([])` still computes `0 / 0` = `NaN`; criterion 1 is unmet. → Use `if (arr.length === 0) return 0;`.

NON_BLOCKING:
- [src/math.js:1] [high] Scope creep: `sum`'s parameters were renamed (`arr` → `values`, `a, b` → `acc, v`) — revert.
- [test/math.test.js:6-9] [low] Good: a regression test for the empty case was added, and `average([2,4]) === 3` is covered, so criteria 2 and 3 are in place.

SUMMARY: One real bug — the guard checks existence, not emptiness. Tests are in place; fix the guard and this is ready.""",)


def render(name, spec):
    stage, case, fixture, ticket, rubric, artifact, *extra = spec
    parts = [f"stage: {stage}", f"case: {case}", f"fixture: {fixture}", "", "## TICKET", ticket, ""]
    if stage == "review":
        parts += ["## MUTATION", MUTATION, ""]
    parts += [f"## RUBRIC:{stage}", rubric, "", "## ARTIFACT", artifact, ""]
    (OUT / f"{name}.md").write_text("\n".join(parts))


for n, s in A.items():
    render(n, s)
print(len(A), "artifacts written")
