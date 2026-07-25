# BASELINE — promoted from run-2026-07-24.md (supersedes the 2026-07-03 baseline)

> This is the current gold reference the `/wf-eval` gate diffs against. It is a promoted copy
> of `run-2026-07-24.md`. Every run is also kept immutably as `run-<date>.md` — this file is
> just the moving pointer; the dated files are the history. Promote a newer run here only after
> it is clean (no regressions) and you want it to become the reference.


Full set, all stages: spec-altitude (spec), spike-decision (decision), ambiguous-spec (plan),
node-bugfix (plan, execute), node-feature (plan, execute), py-feature (plan, execute),
node-review-bug (review).

Context: gate after two coupled changes —
- **Model alias drift (Claude 5 family):** all agents run via aliases; `opus` → Claude Opus 5,
  `sonnet` → Claude Sonnet 5 at run time. This run is the first full-set measurement on the
  5-family models (baseline was measured on the pre-5 aliases).
- **Coverage-first reviewer:** `wf-reviewer` rewritten (report every finding with a
  `[high|med|low]` confidence tag; precision moved from omission to BLOCKING routing;
  conservatism lines removed), `wf-judge` review-stage `no-noise` now judged on the BLOCKING
  section only (long NON_BLOCKING lists are correct, never debited), `wf-runner` told to never
  pass NON_BLOCKING items to fix rounds.
- Judge calibration status: mechanics-only (n=2 gold set, 100% agreement) — see
  `calibration/reports/calibration-2026-07-24.md`. Gold set needs population, esp. review-stage.

| case            | stage    | verdict | score | biggest weakness                                                   |
|-----------------|----------|---------|-------|--------------------------------------------------------------------|
| spec-altitude   | spec     | PASS    | 0.92  | implementation notes run long for pointer altitude (NICE debit)     |
| spike-decision  | decision | PASS    | 0.95  | verbosity beyond "tight" (e.g. typed-language aside) — NICE debit   |
| ambiguous-spec  | plan     | PASS    | 0.91  | none — honest dim now passes (SPEC_GAPS leads with "run /wf-spec")  |
| node-bugfix     | plan     | PASS    | 1.00  | none                                                               |
| node-bugfix     | execute  | PASS    | 1.00  | none — judge independently reran node --test (3/3)                  |
| node-feature    | plan     | PASS    | 1.00  | none                                                               |
| node-feature    | execute  | PASS    | 1.00  | none — judge independently reran (3/3)                              |
| py-feature      | plan     | PASS    | 1.00  | none                                                               |
| py-feature      | execute  | PASS    | 1.00  | none — judge independently reran unittest (2/2)                     |
| node-review-bug | review   | PASS    | 0.98  | third BLOCKING item (stale NOTE comment) — judge accepted as legit  |

Mean score: 0.976
Pass-rate: 10/10 (100%)

## Regression gate vs baseline.md (promoted 2026-07-03; 8 comparable entries)
- spec-altitude spec:    0.88 → 0.92 (+0.04)
- ambiguous-spec plan:   0.78 → 0.91 (+0.13) — the standing "honest (NICE)" miss is closed:
  planner now explicitly recommends /wf-spec via the SPEC_GAPS first-line convention
- node-bugfix plan:      0.99 → 1.00 (+0.01)
- node-bugfix execute:   1.00 → 1.00
- node-feature plan:     1.00 → 1.00
- node-feature execute:  1.00 → 1.00
- py-feature plan:       1.00 → 1.00
- py-feature execute:    1.00 → 1.00
- spike-decision decision: NEW — 0.95 (no baseline entry)
- node-review-bug review:  NEW — 0.98 (no baseline entry; first run of the coverage-first reviewer)
- **NO REGRESSIONS.**

## Notes
- **Coverage-first reviewer, first judged run:** caught all 3 planted flaws (wrong guard,
  hollow test, unrelated churn), verified the guard failure by sandboxed execution, routed the
  churn to NON_BLOCKING with a `[high]` tag, and surfaced two `[low]`-confidence observations
  (single-element boundary test, `!arr`→0 semantics) that the old "few high-confidence findings"
  prompt would likely have suppressed. BLOCKING stayed clean — judge scored no-noise 0.90,
  accepting the third BLOCKING item (stale NOTE comment) as legitimate, not noise.
- Reviewer added a stale-comment BLOCKING item beyond the planted flaws; judge deemed it real.
  Watch across future review cases: if stale-comment-style items start crowding BLOCKING, tighten
  the routing bar in wf-reviewer; one occurrence is signal, not noise.
- 5-family models measurably improved the two weakest baseline entries (ambiguous-spec +0.13,
  spec-altitude +0.04); everything else held at ceiling. Both new-stage entries (decision,
  review) lose points only on NICE verbosity dims — consistent with Claude 5 verbosity shifts;
  candidate one-line length nudges for wf-spec-builder if it drifts further.
- This run is a candidate baseline: it isolates the model-drift + reviewer-change delta so the
  next prompt change diffs against 5-family behavior, and it extends coverage to all 10
  case/stage pairs (old baseline covered 8).
