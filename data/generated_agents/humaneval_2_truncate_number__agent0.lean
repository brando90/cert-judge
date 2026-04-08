import Std.Data.Float
import Std.Tactic.Basic
import Std.Tactic.RCases

/--
Given a positive floating point number, it can be decomposed into
an integer part (largest integer smaller than given number) and decimals
(leftover part always smaller than 1).

Return the decimal part of the number.
-/
def truncate_number (number : Float) : Float :=
  number % 1.0

/-- Specification for truncate_number -/
def truncate_number_spec (number : Float) : Float :=
  number - Float.floor number

/-- Precondition for truncate_number: input must be a positive float -/
def truncate_number_pre (number : Float) : Prop :=
  number > 0

/-- Postcondition for truncate_number: result is the decimal part of the number -/
def truncate_number_post (number : Float) (result : Float) : Prop :=
  result ≥ 0 ∧ result < 1 ∧ ∃ n : Int, number = n.toFloat + result

/-- Correctness theorem for truncate_number -/
theorem truncate_number_correct (number : Float) :
  truncate_number_pre number → truncate_number_post number (truncate_number number) :=
  fun h =>
    sorry

/-- Test cases -/
def test_truncate_number : IO Unit := do
  assert! (truncate_number 3.5 == 0.5)
  assert! ((truncate_number 1.33 - 0.33).abs < 1e-6)
  assert! ((truncate_number 123.456 - 0.456).abs < 1e-6)
  IO.println "All tests passed!"

/-- Run tests -/
#eval test_truncate_number
