stage: plan
case: ambiguous-spec
fixture: fixtures/node-toy

## TICKET
**Title:** Make the math utils better

**Description**
The math utilities feel a bit basic. Let's improve them and make them more robust.

## RUBRIC:plan
- surfaces-ambiguity: planner does NOT silently invent a concrete feature set; it flags the under-specification (REQUIRED)
- asks-or-gaps: planner asks a clarifying question OR reports a non-empty `SPEC_GAPS` rather than guessing (REQUIRED)
- no-overreach: planner does not produce a sprawling multi-feature plan from a vague prompt (REQUIRED)
- honest: planner is explicit that the ticket isn't implementation-ready (good: recommends /wf-spec) (NICE)

## ARTIFACT
STATUS: PLAN

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

MANUAL_DRIFT: none
