id: py-feature
fixture: fixtures/py-toy
stages: plan, execute

## TICKET
**Title:** Add a `multiply` function to calc

**Description**
## Summary
Add `multiply(a, b)` to `calc.py` next to `add`, returning `a * b`.

## Acceptance criteria
- [ ] `multiply(3, 4)` returns `12`
- [ ] `multiply(-2, 5)` returns `-10`
- [ ] A `unittest` test in `test_calc.py` covers it and passes

## Implementation notes
- Match the style of `add`. Tests use stdlib `unittest` (`python3 -m unittest`).

## RUBRIC:plan
- targets-right-file: modifies `calc.py` + `test_calc.py` only (REQUIRED)
- covers-criteria: steps + tests map to both example cases (REQUIRED)
- right-test-framework: uses stdlib `unittest`, not pytest (REQUIRED — pytest isn't available)
- surgical: no extra helpers or refactor (REQUIRED)

## RUBRIC:execute
- correct: `multiply` returns the product incl. the negative case (REQUIRED)
- tested: a unittest test covers it (REQUIRED)
- tests-pass: `python3 -m unittest` is green (REQUIRED)
- surgical: only the two files changed (REQUIRED)
