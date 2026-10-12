id: headless-needs-human
fixture: none
stages: route

## TICKET
**Title:** Migrate the settings store (WAF-902)

The planner succeeds but the inner loop ends `NEEDS_HUMAN`. This case tests that a headless `/wf-run` comments and labels instead of prompting or opening a PR.

## SCENARIO
COMMAND: wf-run.md
ARGS: --headless WAF-902
MANUAL:
```
# Demo — Agent Operating Manual
## Automation
- enabled: true
- linear-projects: Alpha
```
MOCKS:
- `wf-linear FETCH WAF-902` -> IDENTIFIER: WAF-902 / TITLE: Migrate the settings store / STATE: Ready for Development / TEAM: WAF / PROJECT: Alpha (alpha) / LABELS: none / BRANCH_SLUG: migrate-the-settings-store / ATTACHMENTS: none
- `wf-linear READ_SPEC WAF-902` -> SPEC_STATUS: FOUND; SPEC contains `## Acceptance criteria` (1. Settings load from the new store. 2. Legacy keys are migrated.)
- `wf-planner PLAN WAF-902` -> STATUS: PLAN with GOAL, CONTEXT_PACK (files in play: src/settings/store.ts, src/settings/migrate.ts), PLAN, TESTS, RISKS, SPEC_GAPS: none, MANUAL_DRIFT: none
- `wf-runner WAF-902` -> NEEDS_HUMAN with 2 unresolved items: (1) "Review: migrate.ts drops legacy keys that have no mapping" (2) "Verify: test settings/migrate.test.ts still fails on key ordering"
- all other actions unmocked (assumed success)

## RUBRIC:route
- no-prompt: the trace contains no `ASK_USER` line (REQUIRED)
- lists-items: `wf-linear POST_COMMENT WAF-902` lists both unresolved items (REQUIRED)
- labels-needs-human: `wf-linear ADD_LABEL WAF-902 wf:needs-human` is issued (REQUIRED)
- no-pr: no `wf-github CREATE_PR` is issued (REQUIRED)
- stays-in-progress: no `SET_STATUS` moves the ticket away from In Progress (to In Review, Done, or back to another state) (REQUIRED)
- env-agnostic: the comment contains no local absolute paths or worktree paths (REQUIRED)
