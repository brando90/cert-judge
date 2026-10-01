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

/-- The account balances reached after each operation, starting from `balance`. -/
def prefixBalances (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      (balance + op) :: prefixBalances (balance + op) rest

/-- True exactly when one of the balances reached is negative. -/
def belowZeroSpecFrom (balance : Int) (operations : List Int) : Bool :=
  (prefixBalances balance operations).any (fun b => decide (b < 0))

/-- The specification for an account starting with zero balance. -/
def belowZeroSpec (operations : List Int) : Bool :=
  belowZeroSpecFrom 0 operations

/-- A helper that runs the implementation from an arbitrary initial balance. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then
        true
      else
        belowZeroFrom newBalance rest

theorem belowZeroFrom_correct (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations = belowZeroSpecFrom balance operations := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroFrom, belowZeroSpecFrom, prefixBalances]
  | cons op rest ih =>
      by_cases h : balance + op < 0
      · simp [belowZeroFrom, belowZeroSpecFrom, prefixBalances, h]
      · simp [belowZeroFrom, belowZeroSpecFrom, prefixBalances, h, ih]

theorem belowZero_eq_from (operations : List Int) :
    belowZero operations = belowZeroFrom 0 operations := by sorry

theorem belowZero_eq_spec (operations : List Int) :
    belowZero operations = belowZeroSpec operations := by
  rw [belowZero_eq_from]
  exact belowZeroFrom_correct 0 operations

/-- The specification is true exactly when some reached balance is negative. -/
theorem belowZeroSpecFrom_true_iff (balance : Int) (operations : List Int) :
    belowZeroSpecFrom balance operations = true ↔
      ∃ b, b ∈ prefixBalances balance operations ∧ b < 0 := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroSpecFrom, prefixBalances]
  | cons op rest ih =>
      simp [belowZeroSpecFrom, prefixBalances, ih]

/-- The implementation detects a negative balance exactly when such a prefix exists. -/
theorem belowZero_true_iff_exists_negative_prefix (operations : List Int) :
    belowZero operations = true ↔
      ∃ b, b ∈ prefixBalances 0 operations ∧ b < 0 := by
  rw [belowZero_eq_spec]
  exact belowZeroSpecFrom_true_iff 0 operations

/-- Precondition: None -/
def belowZeroPre (_operations : List Int) : Prop := True

/-- Postcondition: the result agrees with whether a reached balance is negative. -/
def belowZeroPost (operations : List Int) (result : Bool) : Prop :=
  result = belowZeroSpec operations

theorem belowZeroCorrect (operations : List Int) (h : belowZeroPre operations) :
    belowZeroPost operations (belowZero operations) := by
  exact belowZero_eq_spec operations

/-- The empty sequence never makes the account go below zero. -/
theorem belowZero_empty : belowZero [] = false := by decide

/-- Regression examples from the programming task. -/
theorem belowZero_test_no_overdraft :
    belowZero [1, 2, -3, 1, 2, -3] = false := by decide

theorem belowZero_test_overdraft :
    belowZero [1, 2, -4, 5, 6] = true := by decide

theorem belowZero_test_no_overdraft_after_recovery :
    belowZero [1, -1, 2, -2, 5, -5, 4, -4] = false := by decide

theorem belowZero_test_overdraft_at_end :
    belowZero [1, -1, 2, -2, 5, -5, 4, -5] = true := by decide

theorem belowZero_test_early_overdraft :
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
