stage: decision
case: spike-decision
fixture: fixtures/node-toy

## TICKET
**Title:** Spike: decide the empty-input contract for `average`

**Description**
Before we harden the math utils, we need to commit to what `average([])` should do — right now it's unspecified. Candidates: **throw** a `RangeError`, **return `0`**, or **return `null`**. Pick one and record the rationale so the follow-up hardening ticket can just implement it. Timeboxed decision; no code change in this ticket.

**Deliverable**
- [ ] A recorded decision (chosen behavior + why) that unblocks the `average` hardening ticket.

## RUBRIC:decision
- decides: returns `STATUS: DECISION` and commits to exactly one contract (throw / `0` / `null`) — not `STATUS: NEEDS_INPUT`, and not a hedge that lists options without choosing one (REQUIRED)
- evidence-backed: the rationale cites concrete evidence from the fixture — e.g. the current `NaN` behavior + in-code NOTE, that `sum([])` returns `0` (a consistency anchor), and/or that no existing test or caller constrains it — rather than generic hand-waving (REQUIRED)
- standalone-headline: the `**Decision:**` line is self-contained — it states the chosen contract AND the crux reason, so a dependent ticket reading only that one line knows what was decided and why (REQUIRED)
- preserves-original: the output is the original description preserved with a `## Decision` section appended — not a wholesale rewrite of the ticket, and not a `NEEDS_INPUT` batch (REQUIRED)
- no-code: stays a decision — does NOT write the actual `average` fix (a function body / diff) or a numbered step-by-step implementation procedure; recording the chosen behavior declaratively is expected, pre-writing the code is not (REQUIRED)
- concise-honest: decision is tight and high-signal; any residual scope boundary (e.g. that `sum` is out of scope) is stated rather than left implicit (NICE)

## ARTIFACT
STATUS: DECISION

Before we harden the math utils, we need to commit to what `average([])` should do — right now it's unspecified. Candidates: **throw** a `RangeError`, **return `0`**, or **return `null`**. Pick one and record the rationale so the follow-up hardening ticket can just implement it. Timeboxed decision; no code change in this ticket.

**Deliverable**
- [ ] A recorded decision (chosen behavior + why) that unblocks the `average` hardening ticket.

## Decision
**Decision:** `average([])` throws `RangeError("average() requires a non-empty array")`. The mean of an empty set is undefined, so failing loudly beats returning a plausible but wrong value.
**Rationale:** Right now `average` in `src/math.js` computes `sum(arr) / arr.length`, so `[]` gives `0/0` = `NaN`. The source comment says so, and no test covers the empty case. Return `0` is rejected: it's indistinguishable from a real zero average such as `average([-1, 1])`, and unlike `sum([])` (0 is the additive identity) division has no identity. Return `null` is rejected: it widens the return type and becomes `0` in arithmetic if a caller forgets to check. No caller in the repo relies on today's `NaN`.
**Scope:** in — the empty-array contract for `average`, error type and message; out — non-array/non-numeric input, any change to `sum` (`sum([])` stays `0`), NaN/Infinity handling for non-empty input.
**Compatibility:** `RangeError` is a standard built-in; the fixture has no dependencies.
**Unblocks:** the `average` hardening ticket.
