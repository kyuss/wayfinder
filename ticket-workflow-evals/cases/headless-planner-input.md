id: headless-planner-input
fixture: none
stages: route

## TICKET
**Title:** Add CSV export to the reports page (WAF-901)

Deliberately under-decided: the spec leaves the export scope open, so the planner returns `NEEDS_INPUT`. This case tests that a headless `/wf-run` parks the ticket with a comment instead of prompting.

## SCENARIO
COMMAND: wf-run.md
ARGS: --headless WAF-901
MANUAL:
```
# Demo — Agent Operating Manual
## Automation
- enabled: true
- linear-projects: Alpha
- trigger-state: Todo
```
MOCKS:
- `wf-linear FETCH WAF-901` -> IDENTIFIER: WAF-901 / TITLE: Add CSV export to the reports page / STATE: Ready for Development / TEAM: WAF / PROJECT: Alpha (alpha) / LABELS: none / BRANCH_SLUG: add-csv-export-to-the-reports-page / ATTACHMENTS: none
- `wf-linear READ_SPEC WAF-901` -> SPEC_STATUS: FOUND; SPEC contains `## Acceptance criteria` (1. Reports page has an Export CSV button. 2. The file contains the visible columns.)
- `wf-planner PLAN WAF-901` -> STATUS: NEEDS_INPUT with 2 question blocks: (1) "Which rows should be exported?" options: "All rows (recommended)", "Only the current page", "Only filtered rows"; (2) "Which delimiter?" options: "Comma (recommended)", "Semicolon"
- all other actions unmocked (assumed success)

## RUBRIC:route
- no-prompt: the trace contains no `ASK_USER` line (REQUIRED)
- parks-with-comment: `wf-linear POST_COMMENT WAF-901` whose first line contains the marker `🤖 Spec questions`, rendering both questions with lettered options and a ✅ on the recommended option (REQUIRED)
- parks-in-needs-answers: `wf-linear SET_STATUS WAF-901 "Needs Answers"` occurs after the POST_COMMENT (REQUIRED)
- keeps-worktree: no worktree removal or deletion is attempted (REQUIRED)
- no-build: no `wf-runner` spawn and no `wf-github CREATE_PR` (REQUIRED)
- env-agnostic: comment text has no local absolute paths or tool paths (NICE)
