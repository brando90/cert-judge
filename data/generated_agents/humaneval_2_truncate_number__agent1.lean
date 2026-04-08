```lean
import Mathlib.Data.Real.Basic

/-- Given a positive floating point number, it can be decomposed into
and integer part (largest integer smaller than given number) and decimals
(leftover part always smaller than 1).

Return the decimal part of the number.
-/
def truncateNumber (number : Float) : Float :=
  number % 1.0

/-- The truncateNumber function returns the decimal part of a number,
    which is always in the range [0, 1). -/
theorem truncateNumber_spec (n : Float) (h : n ≥ 0) : 
  0 ≤ truncateNumber n ∧ truncateNumber n < 1 := by
  sorry

/-- The truncateNumber function correctly returns the decimal part of a number -/
theorem truncateNumber_correct (n : Float) (h : n ≥ 0) : 
  truncateNumber n = n - Float.floor n := by
  sorry

def main : IO Unit := do
  let test1 := truncateNumber 3.5
  IO.println s!"truncateNumber 3.5 = {test1}"
  assert! test1 == 0.5
  
  let test2 := truncateNumber 1.33
  IO.println s!"truncateNumber 1.33 = {test2}"
  assert! (test2 - 0.33).abs < 1e-6
  
  let test3 := truncateNumber 123.456
  IO.println s!"truncateNumber 123.456 = {test3}"
  assert! (test3 - 0.456).abs < 1e-6
  
  IO.println "All tests passed!"
```
