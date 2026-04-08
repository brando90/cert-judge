import Mathlib.Data.Real.Basic

/--
Given a positive floating point number, it can be decomposed into
an integer part (largest integer smaller than given number) and decimals
(leftover part always smaller than 1).

Return the decimal part of the number.
-/
def truncateNumber (number : Float) : Float :=
  number % 1.0

/--
Properties:
- The result is always less than 1.0
- The result is always non-negative
- For any positive number, adding the integer part and decimal part gives the original number
-/
def truncateNumberSpec (number : Float) : Float :=
  number - Float.floor number

theorem truncateNumber_spec (number : Float) :
  truncateNumber number = truncateNumberSpec number := by
  sorry

/-- Tests for truncateNumber -/
def truncateNumberTests : IO Unit := do
  assert! (truncateNumber 3.5 == 0.5)
  assert! ((truncateNumber 1.33 - 0.33).abs < 1e-6)
  assert! ((truncateNumber 123.456 - 0.456).abs < 1e-6)
  IO.println "All tests passed!"
