id: spec-altitude
fixture: fixtures/node-toy
stages: spec

## TICKET
**Title:** Add a `median` helper to the math utils

**Description**
We have `sum` and `average` in the math utils but no `median`. Add a `median(arr)` helper so callers can get the middle value of a list of numbers.

(Deliberately thin: no acceptance criteria, and the empty-array and even-length behaviors are left unspecified. This case tests two things at once — whether the spec-builder RESOLVES those decisions and records them as facts so the planner needn't ask, AND whether it stays at spec altitude: pointers to files/patterns, not pre-written code or a line-anchored procedure.)

## RUBRIC:spec
- resolves-decisions: spec leaves zero open questions — the empty-array result and the even-length behavior (e.g. average of the two middles) are decided and stated as facts, so the planner won't need to ask (REQUIRED)
- spec-altitude: Implementation notes stay at pointer altitude. FAIL only on one of these three: a pre-written implementation (a function body or full code block), specific line-number anchors, or a numbered/ordered step-by-step build procedure. ALLOWED — do not fail or heavily penalize for these: declarative descriptions of decided behavior (e.g. "even length → mean of the two middles"), pattern/framework pointers (which file to edit, which existing test style to follow), and a brief inline idiom illustrating a named gotcha (e.g. `[...arr].sort((a,b)=>a-b)`). The test is whether an executor still has real "how" to figure out — not whether the prose is maximally terse (REQUIRED)
- verifiable-ac: every acceptance criterion is objectively verifiable — concrete inputs/outputs (e.g. `median([1,2,3])` is `2`) or a runnable command (REQUIRED)
- scoped: explicit in/out scope; no speculative extra helpers, configs, or refactors beyond `median` + its test (REQUIRED)
- concise-honest: spec is tight and high-signal, and any assumption it made (the edge-case choices) is recorded as a fact rather than left implicit (NICE)
- two-block-output: the output carries both sentinel sections in order — `--- TICKET_DESCRIPTION ---` (a Why/What/Success-criteria brief in plain language, free of implementation detail: no file paths, commands, or internal APIs) then `--- SPEC ---` (the full spec); acceptance criteria appear only inside the SPEC block (REQUIRED)
