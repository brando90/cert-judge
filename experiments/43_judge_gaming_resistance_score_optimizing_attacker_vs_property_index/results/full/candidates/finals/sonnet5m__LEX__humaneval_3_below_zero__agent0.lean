import Mathlib
import Mathlib.Tactic

/--
You're given a list of deposit and withdrawal operations on a bank account that starts with
zero balance. Your task is to detect if at any point the balance of account fallls below zero, and
at that point function should return True. Otherwise it should return False.
-/
def belowZero (operations : List Int) : Bool :=
  let rec go (balance : Int) (ops : List Int) : Bool :=
    match ops with
    | [] => false
    | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then true
      else go newBalance rest
  go 0 operations

/-- The balance at each step is the sum of operations up to that point -/
def runningSum (operations : List Int) : List Int :=
  let rec go (acc : Int) (ops : List Int) : List Int :=
    match ops with
    | [] => []
    | op :: rest =>
      let newAcc := acc + op
      newAcc :: go newAcc rest
  go 0 operations

/-- Specification: belowZero returns true iff any element in the running sum is negative -/
def belowZeroSpec (operations : List Int) : Bool :=
  (runningSum operations).any (· < 0)

theorem belowZero_correct (operations : List Int) :
  belowZero operations = belowZeroSpec operations := by sorry

#eval belowZero [] -- false
#eval belowZero [1, 2, 3] -- false
#eval belowZero [1, 2, -4, 5] -- true

/-- Test suite for belowZero -/
def belowZeroTests : List (List Int × Bool) := [
  ([], false),
  ([1, 2, -3, 1, 2, -3], false),
  ([1, 2, -4, 5, 6], true),
  ([1, -1, 2, -2, 5, -5, 4, -4], false),
  ([1, -1, 2, -2, 5, -5, 4, -5], true),
  ([1, -2, 2, -2, 5, -5, 4, -4], true)
]

