id: headless-spec-default
fixture: none
stages: route

## TICKET
**Title:** Add retry to the webhook sender (WAF-903)

A parked ticket whose questions were only partly answered. This case tests that headless `/wf-spec` defaults the unanswered question, still writes the spec, and holds the build with a label.

## SCENARIO
COMMAND: wf-spec.md
ARGS: --headless WAF-903
MANUAL:
```
# Demo — Agent Operating Manual
## Linear workflow
- Ready for Development → Ready for Development
## Workflow preferences
- spec-questions: inline
```
MOCKS:
- `wf-linear FETCH WAF-903` -> IDENTIFIER: WAF-903 / TITLE: Add retry to the webhook sender / STATE: Needs Answers / TEAM: WAF / PROJECT: Alpha (alpha) / LABELS: none / ATTACHMENTS: none
- `wf-linear READ_ANSWERS WAF-903` -> QUESTIONS_STATUS: ANSWERED; QUESTIONS: `🤖 Spec questions` comment with Q1 "Max attempts?" (A) 3 ✅ recommended (B) 5; Q2 "Backoff?" (A) Exponential ✅ recommended (B) Fixed; ANSWERS: `1: B` (Q2 not answered)
- `wf-spec-builder WAF-903` -> STATUS: SPEC with the two sentinels, TICKET_DESCRIPTION and SPEC (max 5 attempts, exponential backoff)
- all other actions unmocked (assumed success)

## RUBRIC:route
- no-prompt: the trace contains no `ASK_USER` line (REQUIRED)
- defaults-q2: the builder is given `ANSWERS` with Q1 = B (5 attempts) and Q2 defaulted to the recommended option (Exponential) (REQUIRED)
- persists-spec: in order, `POST_COMMENT` (spec comment, first line `🤖 Implementation spec`), `UPDATE_DESCRIPTION`, then `SET_STATUS WAF-903 "Ready for Development"` (REQUIRED)
- holds-build: `wf-linear ADD_LABEL WAF-903 wf:hold` is issued after the persist calls (REQUIRED)
- names-default: a `POST_COMMENT` starting `🤖 Spec defaults applied` names Q2 and its defaulted option, and its first line does not start with `🤖 Spec questions` or `🤖 Implementation spec` (REQUIRED)
- env-agnostic: comment bodies contain no local absolute paths (NICE)
