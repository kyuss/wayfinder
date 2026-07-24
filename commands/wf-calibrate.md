---
description: Calibrate wf-judge against your human labels — measures judge↔human agreement, FAIL-class precision/recall, and bias-probe consistency, so the /wf-eval regression gate can be trusted. Re-run after changing the judge's model or prompt.
argument-hint: (no args — runs the whole calibration set)
allowed-tools: Task, Bash, Read, Write
---

# /wf-calibrate

An LLM judge is untrustworthy until it agrees with you. This grades `wf-judge` against a human-labeled gold set and reports whether it's calibrated enough to gate `/wf-eval`. Fully offline: it only reads local calibration fixtures, never runs the pipeline, never touches Linear/GitHub, and never edits the judge or your labels.

## Layout
- `CAL = ~/.claude/ticket-workflow-evals/calibration`
- `CAL/artifacts/*.md` — stored artifacts to judge. Each contains `stage`, `case`/`fixture`, a `## TICKET`, the matching `## RUBRIC:<stage>`, and the `## ARTIFACT` to grade. These are **real past outputs** — deliberately include both PASS and FAIL examples (~50/50), with a few known-bad ones (missed criterion, hollow/mocked test, over-engineering).
- `CAL/gold.md` — your ground-truth labels: one row per artifact (`artifact | human PASS/FAIL | reason | probe-group`).
- `CAL/reports/` — saved calibration reports.

## Preconditions
- `CAL/gold.md` and `CAL/artifacts/` exist with **≥10** labeled artifacts (warn if fewer — agreement on a tiny set is noise). If missing, tell the user to populate them; the scaffold ships the format + two worked examples.

## Run
0. **Capture provenance first.** Run `grep '^model:' ~/.claude/agents/wf-judge.md` and note the model **you** are running as. The judge's `model:` is a floating alias, so the generation behind it can change with no edit here; an agreement number is only evidence for the generation that produced it.
1. Parse `gold.md` into rows: `{artifact, human, reason, probe-group}`.
2. For each artifact named in `gold.md` (process them ≤4 judges at a time to stay cheap):
   - Parse its `stage`, `case`, `## TICKET`, `## RUBRIC:<stage>`, and `## ARTIFACT`.
   - Spawn `wf-judge` with `STAGE`, the `CASE` (TICKET + RUBRIC + fixture path), and `ARTIFACT` — **exactly** the inputs `/wf-eval` gives it. Record its `OVERALL` PASS/FAIL + score.
   - **Blind:** never pass the human label or reason to the judge.
3. Compare each judge verdict to its human label.

## Report
Print:
- **Per-artifact table:** `artifact | human | judge | score | match? | judge's note`.
- **Agreement** = matches / total. **Bar: ≥ 90%** (Hamel). Below it, say loudly that the `/wf-eval` gate is not yet trustworthy.
- **FAIL-class precision/recall** (human FAIL = the positive class): a judge that never says FAIL can still post high agreement while being useless — these expose it. Report both.
- **Bias probes:** for each `probe-group` with >1 member (equivalent in correctness, differing only in length/style/terseness), all members must get the **same** judge verdict. Flag any divergent group as a verbosity/self-preference signal.
- **Disagreements:** list each human↔judge mismatch with both reasons. These are the work items — usually the *rubric in the case is ambiguous*, not the judge.
- **Overall:** `CALIBRATED` (agreement ≥90% AND no probe divergence) or `NOT CALIBRATED — investigate`.

Open the report with a `## PROVENANCE` block (the judge's declared alias from step 0, your active model, the date). Agreement measured under one model generation is not evidence for another.

Save the report to `CAL/reports/calibration-<today>.md` (`mkdir -p` the dir if needed). Never modify `gold.md` or the judge.

## Notes
- Re-calibrate whenever `wf-judge`'s model or prompt changes. **Its model can change without you touching anything:** `model: sonnet` is a floating alias, so a new model generation silently re-points it. Treat a generation change exactly like a prompt change, and check the newest report's `## PROVENANCE` against current before relying on it. A report whose provenance no longer matches is expired, not evidence.
- When agreement < 90%, fix the **rubrics / judge prompt**, never the gold labels (the gold is ground truth by definition).
- This validates the *judge*. It complements `/wf-eval`, which uses the judge to validate the *pipeline*.
