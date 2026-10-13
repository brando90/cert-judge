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

/-- Specification for belowZero -/
def belowZeroSpec (operations : List Int) : Bool :=
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

/-- Precondition: None -/
def belowZeroPre (_operations : List Int) : Prop := True

/-- Postcondition: belowZero returns true if and only if at some point the balance becomes negative -/
def belowZeroPost (operations : List Int) (result : Bool) : Prop :=
  result = belowZeroSpec operations

theorem belowZeroCorrect (operations : List Int) (h : belowZeroPre operations) :
  belowZeroPost operations (belowZero operations) := by sorry

/-- The account balances after each operation, starting from the given balance. -/
def prefixBalancesFrom (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      let nextBalance := balance + op
      nextBalance :: prefixBalancesFrom nextBalance rest

/-- The balances reached after the operations, starting from zero. -/
def prefixBalances (operations : List Int) : List Int :=
  prefixBalancesFrom 0 operations

/-- True when some balance reached after the operations is negative. -/
def dipsBelowZero (operations : List Int) : Prop :=
  ∃ balance, balance ∈ prefixBalances operations ∧ balance < 0

/-- Detect a negative balance while processing operations from an arbitrary starting balance. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      let nextBalance := balance + op
      if nextBalance < 0 then
        true
      else
        belowZeroFrom nextBalance rest

theorem belowZero_eq_belowZeroFrom (operations : List Int) :
    belowZero operations = belowZeroFrom 0 operations := by sorry

theorem belowZeroFrom_iff (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations = true ↔
      ∃ value, value ∈ prefixBalancesFrom balance operations ∧ value < 0 := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroFrom, prefixBalancesFrom]
  | cons op rest ih =>
      simp only [belowZeroFrom, prefixBalancesFrom]
      by_cases h : balance + op < 0
      · simp [h]
      · simp [h, ih]

/-- The implementation reports a dip exactly when a prefix balance is negative. -/
theorem belowZero_iff_dipsBelowZero (operations : List Int) :
    belowZero operations = true ↔ dipsBelowZero operations := by
  rw [belowZero_eq_belowZeroFrom]
  simpa [dipsBelowZero, prefixBalances] using
    (belowZeroFrom_iff 0 operations)

theorem belowZero_empty : belowZero [] = false := by decide

theorem belowZero_example_no_dip :
    belowZero [1, 2, -3, 1, 2, -3] = false := by decide

theorem belowZero_example_dip :
    belowZero [1, 2, -4, 5, 6] = true := by decide

theorem belowZero_example_no_dip_after_cancellations :
    belowZero [1, -1, 2, -2, 5, -5, 4, -4] = false := by decide

theorem belowZero_example_dip_at_end :
    belowZero [1, -1, 2, -2, 5, -5, 4, -5] = true := by decide

theorem belowZero_example_early_dip :
    belowZero [1, -2, 2, -2, 5, -5, 4, -4] = true := by decide

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
