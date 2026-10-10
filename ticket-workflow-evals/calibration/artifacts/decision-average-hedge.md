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
**Decision:** Each option is viable; the choice depends on how callers want to handle empty input.
**Rationale:** Today `average` computes `sum(arr) / arr.length`, so `[]` yields `NaN`, as the source comment notes. Throwing a `RangeError` is loud and keeps the return type a number. Returning `0` is consistent with `sum([])` returning `0` and never crashes callers. Returning `null` makes "no answer" explicit but widens the return type. Any of the three can be implemented in one line; the hardening ticket owner should pick whichever matches caller expectations.
**Scope:** in — the empty-array contract; out — non-array input, changes to `sum`.
**Compatibility:** all three are plain JavaScript with no dependencies.
**Unblocks:** the `average` hardening ticket.
