import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/--
Given a list of deposit and withdrawal operations on a bank account that starts with
zero balance, detect if at any point the balance of account falls below zero.
If at any point the balance becomes negative, return `true`. Otherwise return `false`.

Example:
below_zero [1, 2, 3] = false
below_zero [1, 2, -4, 5] = true
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

/-- Tests for belowZero -/
def belowZeroTests : List (List Int × Bool) := [
  ([], false),
  ([1, 2, -3, 1, 2, -3], false),
  ([1, 2, -4, 5, 6], true),
  ([1, -1, 2, -2, 5, -5, 4, -4], false),
  ([1, -1, 2, -2, 5, -5, 4, -5], true),
  ([1, -2, 2, -2, 5, -5, 4, -4], true)
]

/- Run tests for belowZero -/
#eval belowZeroTests.all (fun (input, expected) => belowZero input == expected)

/--
Predicate that holds when the balance never goes below zero at any point
during the operations.
-/
def NeverBelowZero (operations : List Int) : Prop :=
  let rec prefixSums (acc : Int) : List Int → List Int
    | [] => []
    | x :: xs => (acc + x) :: prefixSums (acc + x) xs
  
  (0 :: prefixSums 0 operations).all (· ≥ 0)

/-- The balance after each operation, in the same order as the operations. -/
def prefixBalancesFrom (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      (balance + op) :: prefixBalancesFrom (balance + op) rest

/-- All balances reached after each operation, starting from zero. -/
def prefixBalances (operations : List Int) : List Int :=
  prefixBalancesFrom 0 operations

/-- There is a point in the operation sequence at which the balance is negative. -/
def BelowZeroSpec (operations : List Int) : Prop :=
  ∃ balance, balance ∈ prefixBalances operations ∧ balance < 0

/--
The program returns `true` exactly when some balance reached after an operation
is negative.
-/
theorem belowZero_correct (operations : List Int) :
    belowZero operations = true ↔ BelowZeroSpec operations := by
  sorry

/--
The program returns `false` exactly when every balance reached after an operation
is nonnegative.
-/
theorem belowZero_false_iff_all_prefix_balances_nonnegative
    (operations : List Int) :
    belowZero operations = false ↔
      ∀ balance, balance ∈ prefixBalances operations → 0 ≤ balance := by
  sorry

/-- The executable result agrees with the `NeverBelowZero` predicate. -/
theorem belowZero_false_iff_NeverBelowZero (operations : List Int) :
    belowZero operations = false ↔ NeverBelowZero operations := by
  sorry

/-- A negative prefix balance guarantees that `belowZero` returns `true`. -/
theorem belowZero_true_of_negative_prefix (operations : List Int)
    (h : ∃ balance, balance ∈ prefixBalances operations ∧ balance < 0) :
    belowZero operations = true := by
  sorry

/-- Once a sequence has gone below zero, appending more operations cannot undo it. -/
theorem belowZero_true_append (operations suffix : List Int)
    (h : belowZero operations = true) :
    belowZero (operations ++ suffix) = true := by
  sorry

@[simp] theorem belowZero_nil : belowZero ([] : List Int) = false := by
  rfl
