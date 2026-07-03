# Judge calibration — gold labels

Ground-truth human verdicts for `/wf-calibrate`. One row per artifact in `artifacts/`.

- **human** — `PASS` or `FAIL`, *your* verdict, decided blind (before seeing what the judge says).
- **reason** — one line; why. Used only in the disagreement report, never shown to the judge.
- **probe-group** — optional tag. Give two+ artifacts the SAME tag when they're equivalent in correctness but differ only in length/style — the judge must rate them identically (verbosity / self-preference probe). Leave blank otherwise.

Aim for **~15–20 artifacts, roughly half PASS / half FAIL**, including deliberate bad ones (missed criterion, hollow or mocked test, over-engineering / scope creep). The two rows below are worked examples — keep or replace them.

| artifact              | human | reason                                                | probe-group |
|-----------------------|-------|-------------------------------------------------------|-------------|
| example-plan-good.md  | PASS  | finds root cause, minimal guard, adds regression test |             |
| example-plan-bad.md   | FAIL  | omits required regression test; over-reaches scope    |             |
