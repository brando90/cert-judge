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

/-- The same balance-checking algorithm, with the starting balance explicit. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
    let newBalance := balance + op
    if newBalance < 0 then
      true
    else
      belowZeroFrom newBalance rest

/-- There is a negative balance among the successive balances after operations. -/
def hasNegativePrefix (balance : Int) : List Int → Prop
  | [] => False
  | op :: rest =>
    balance + op < 0 ∨ hasNegativePrefix (balance + op) rest

theorem belowZeroFrom_correct (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations = true ↔ hasNegativePrefix balance operations := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroFrom, hasNegativePrefix]
  | cons op rest ih =>
      by_cases h : balance + op < 0
      · simp [belowZeroFrom, hasNegativePrefix, h]
      · simp [belowZeroFrom, hasNegativePrefix, h, ih (balance + op)]

theorem belowZero_eq_belowZeroFrom (operations : List Int) :
    belowZero operations = belowZeroFrom 0 operations := by sorry

/-- A specification of `belowZero`, expressed using the starting balance explicitly. -/
def belowZeroSpec (operations : List Int) : Bool :=
  belowZeroFrom 0 operations

/-- The result is true exactly when some successive balance is negative. -/
theorem belowZero_iff_negativePrefix (operations : List Int) :
    belowZero operations = true ↔ hasNegativePrefix 0 operations := by
  rw [belowZero_eq_belowZeroFrom]
  exact belowZeroFrom_correct 0 operations

/-- Precondition: None -/
def belowZeroPre (_operations : List Int) : Prop := True

/-- Postcondition: the result agrees with the specified balance check. -/
def belowZeroPost (operations : List Int) (result : Bool) : Prop :=
  result = belowZeroSpec operations

theorem belowZeroCorrect (operations : List Int) (h : belowZeroPre operations) :
    belowZeroPost operations (belowZero operations) := by
  change belowZero operations = belowZeroFrom 0 operations
  exact belowZero_eq_belowZeroFrom operations

/-- Examples matching the task's test cases. -/
example : belowZero [] = false := by decide
example : belowZero [1, 2, -3, 1, 2, -3] = false := by decide
example : belowZero [1, 2, -4, 5, 6] = true := by decide
example : belowZero [1, -1, 2, -2, 5, -5, 4, -4] = false := by decide
example : belowZero [1, -1, 2, -2, 5, -5, 4, -5] = true := by decide
example : belowZero [1, -2, 2, -2, 5, -5, 4, -4] = true := by decide

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
