import Mathlib
import Lean.Data.Array

namespace BelowZero

/--
You're given a list of deposit and withdrawal operations on a bank account that starts with
zero balance. Your task is to detect if at any point the balance of account falls below zero, and
at that point function should return true. Otherwise it should return false.
-/
def belowZero (operations : List Int) : Bool :=
  let rec loop (balance : Int) (ops : List Int) : Bool :=
    match ops with
    | [] => false
    | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then
        true
      else
        loop newBalance rest
  loop 0 operations

/-- The balances after each operation, starting from an arbitrary initial balance. -/
def balancesAfter (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      let newBalance := balance + op
      newBalance :: balancesAfter newBalance rest

/--
The specification: the result is true exactly when at least one balance reached
after an operation is negative.
-/
def belowZeroSpec (operations : List Int) : Bool :=
  decide (∃ b, b ∈ balancesAfter 0 operations ∧ b < 0)

/-- Precondition: None. -/
def belowZeroPre (_operations : List Int) : Prop := True

/-- Postcondition expressed using the independent prefix-balance specification. -/
def belowZeroPost (operations : List Int) (result : Bool) : Prop :=
  result = belowZeroSpec operations

theorem belowZeroCorrect (operations : List Int) (h : belowZeroPre operations) :
    belowZeroPost operations (belowZero operations) := by
  sorry

/-- The implementation returns true exactly when a prefix balance is negative. -/
theorem belowZero_iff_exists_negative_prefix (operations : List Int) :
    belowZero operations = true ↔
      ∃ b, b ∈ balancesAfter 0 operations ∧ b < 0 := by
  sorry

/-- The implementation returns false exactly when every prefix balance is nonnegative. -/
theorem belowZero_eq_false_iff_all_prefixes_nonnegative (operations : List Int) :
    belowZero operations = false ↔
      ∀ b, b ∈ balancesAfter 0 operations → 0 ≤ b := by
  sorry

theorem belowZero_empty : belowZero [] = false := by sorry

/-- Tests for belowZero -/
def tests : IO Unit := do
  IO.println s!"Test 1: {belowZero []}"
  IO.println s!"Test 2: {belowZero [1, 2, -3, 1, 2, -3]}"
  IO.println s!"Test 3: {belowZero [1, 2, -4, 5, 6]}"
  IO.println s!"Test 4: {belowZero [1, -1, 2, -2, 5, -5, 4, -4]}"
  IO.println s!"Test 5: {belowZero [1, -1, 2, -2, 5, -5, 4, -5]}"
  IO.println s!"Test 6: {belowZero [1, -2, 2, -2, 5, -5, 4, -4]}"

  assert! belowZero [] == false
  assert! belowZero [1, 2, -3, 1, 2, -3] == false
  assert! belowZero [1, 2, -4, 5, 6] == true
  assert! belowZero [1, -1, 2, -2, 5, -5, 4, -4] == false
  assert! belowZero [1, -1, 2, -2, 5, -5, 4, -5] == true
  assert! belowZero [1, -2, 2, -2, 5, -5, 4, -4] == true

  IO.println "All tests passed!"

end BelowZero
