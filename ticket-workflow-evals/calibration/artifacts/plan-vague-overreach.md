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
MANUAL_DRIFT: none
