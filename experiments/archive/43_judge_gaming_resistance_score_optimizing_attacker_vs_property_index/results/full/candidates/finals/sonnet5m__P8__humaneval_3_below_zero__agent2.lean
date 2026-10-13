import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/--
Given a list of deposit and withdrawal operations on a bank account that starts with
zero balance, detect if at any point the balance of account falls below zero.
If at any point the balance becomes negative, return `true`. Otherwise return `false`.

Example:
belowZero [1, 2, 3] = false
belowZero [1, 2, -4, 5] = true
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

/-- The balance after the first `n` operations (or all operations if `n` is too large). -/
def prefixBalance (operations : List Int) (n : Nat) : Int :=
  (operations.take n).sum

/-- Some prefix of the operations leaves the account with a negative balance. -/
def GoesBelowZero (operations : List Int) : Prop :=
  ∃ n : Nat, n ≤ operations.length ∧ prefixBalance operations n < 0

/--
The balance is nonnegative after every prefix of the operations, including the
empty prefix.
-/
def NeverBelowZero (operations : List Int) : Prop :=
  ∀ n : Nat, n ≤ operations.length → 0 ≤ prefixBalance operations n

/-- The implementation reports a negative balance exactly when a prefix sum is negative. -/
theorem belowZero_eq_true_iff_prefix_negative (operations : List Int) :
    belowZero operations = true ↔ GoesBelowZero operations := by
  sorry

/-- The implementation reports no negative balance exactly when every prefix is safe. -/
theorem belowZero_eq_false_iff_never_below_zero (operations : List Int) :
    belowZero operations = false ↔ NeverBelowZero operations := by
  sorry

theorem belowZero_empty : belowZero [] = false := by
  rfl

theorem belowZero_examples_pass :
    belowZeroTests.all (fun (input, expected) => belowZero input == expected) = true := by
  decide
