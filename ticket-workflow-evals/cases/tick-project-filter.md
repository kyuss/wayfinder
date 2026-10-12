id: tick-project-filter
fixture: none
stages: route

## TICKET
**Title:** /wf-tick project and label filtering

No single ticket: this case tests that a tick only touches tickets in the repo's listed Linear projects, skips excluded labels, reports an unknown project, and runs the phases in order.

## SCENARIO
COMMAND: wf-tick.md
ARGS: (none)
MANUAL:
```
# Demo — Agent Operating Manual
## Automation
- enabled: true
- linear-projects: Alpha, Betta
- trigger-state: Todo
- max-runs-per-tick: 3
```
MOCKS:
- every `wf-linear LIST_BY_STATUS` response ends with `PROJECT_ERRORS: Betta — no project matches` and has `PROJECTS: Alpha`
- `wf-linear LIST_BY_STATUS "Needs Answers"` -> ISSUES: none
- `wf-linear LIST_BY_STATUS "Todo"` -> ISSUES: `A-1 | Alpha | - | Add widget`; `A-2 | Alpha | wf:hold | Tune cache`; `A-3 | Alpha | - | Fix typo`
- `wf-linear FETCH A-3` -> PROJECT: Gamma (gamma), LABELS: none, STATE: Todo
- `wf-linear FETCH A-1` -> PROJECT: Alpha (alpha), LABELS: none, STATE: Todo
- `wf-linear LIST_BY_STATUS "Ready for Development"` -> ISSUES: none
- all other actions unmocked (assumed success)

## RUBRIC:route
- phase-order: LIST for Needs Answers, then Todo, then Ready for Development, in that order (REQUIRED)
- projects-passed: every `LIST_BY_STATUS` call carries `PROJECTS` naming Alpha and Betta (REQUIRED)
- reports-missing-project: `project not found: Betta` is reported, and the tick still processes Alpha (REQUIRED)
- excluded-untouched: A-2 (`wf:hold`) receives zero writes (no comment, status, or label change) (REQUIRED)
- out-of-project-untouched: A-3 (project Gamma, not listed) receives zero writes (REQUIRED)
- specs-a1: A-1 is passed to `/wf-spec --linear --headless` (REQUIRED)
- no-prompt: the trace contains no `ASK_USER` line (REQUIRED)
- summary-by-project: the final summary is grouped by phase and project (NICE)
