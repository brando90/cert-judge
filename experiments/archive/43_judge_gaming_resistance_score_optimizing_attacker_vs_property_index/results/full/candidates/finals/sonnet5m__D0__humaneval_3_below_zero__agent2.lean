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

/-- The running balances after each operation, in order. -/
def belowZeroPrefixBalances (operations : List Int) : List Int :=
  let rec go (balance : Int) : List Int → List Int
    | [] => []
    | op :: rest =>
      let next := balance + op
      next :: go next rest
  go 0 operations

/--
The result is true exactly when one of the running balances is negative.
-/
theorem belowZero_eq_any_negative_prefix (operations : List Int) :
    belowZero operations =
      (belowZeroPrefixBalances operations).any
        (fun balance => decide (balance < 0)) := by
  sorry

/--
The account never goes below zero exactly when `belowZero` returns false.
-/
theorem belowZero_false_iff_NeverBelowZero (operations : List Int) :
    belowZero operations = false ↔ NeverBelowZero operations := by
  sorry

/--
The account goes below zero exactly when `belowZero` returns true, equivalently
when it is not the case that all running balances are nonnegative.
-/
theorem belowZero_true_iff_not_NeverBelowZero (operations : List Int) :
    belowZero operations = true ↔ ¬ NeverBelowZero operations := by
  sorry

/-- An empty sequence of operations leaves the balance nonnegative. -/
theorem belowZero_empty : belowZero ([] : List Int) = false := by
  rfl

/-- The balance after the first `n` operations, or after all operations if fewer remain. -/
def belowZeroBalanceAfter (operations : List Int) (n : Nat) : Int :=
  (operations.take n).sum

/--
The function returns true precisely when some prefix of the operations has
negative total balance.
-/
theorem belowZero_true_iff_negative_prefix_sum (operations : List Int) :
    belowZero operations = true ↔
      ∃ n, n ≤ operations.length ∧ belowZeroBalanceAfter operations n < 0 := by
  sorry

/--
The function returns false precisely when every prefix has nonnegative total
balance.
-/
theorem belowZero_false_iff_nonnegative_prefix_sums (operations : List Int) :
    belowZero operations = false ↔
      ∀ n, n ≤ operations.length → 0 ≤ belowZeroBalanceAfter operations n := by
  sorry

/-- The prefix-sum specification is equivalent to the running-balance predicate. -/
theorem NeverBelowZero_iff_prefix_sums (operations : List Int) :
    NeverBelowZero operations ↔
      ∀ n, n ≤ operations.length → 0 ≤ belowZeroBalanceAfter operations n := by
  sorry

/-- A negative first operation immediately makes the account go below zero. -/
theorem belowZero_cons_of_negative (op : Int) (operations : List Int)
    (h : op < 0) : belowZero (op :: operations) = true := by
  sorry

/-- A single operation causes an overdraft exactly when it is negative. -/
theorem belowZero_singleton (op : Int) :
    belowZero [op] = decide (op < 0) := by
  sorry

/-- Once an overdraft has occurred, appending more operations cannot undo it. -/
theorem belowZero_append_of_prefix_true (operations rest : List Int)
    (h : belowZero operations = true) :
    belowZero (operations ++ rest) = true := by
  sorry

/-- Example with only deposits: the account never goes below zero. -/
theorem belowZero_example_deposits :
    belowZero [1, 2, 3] = false := by
  decide

/-- Example where a withdrawal makes the balance negative. -/
theorem belowZero_example_withdrawal :
    belowZero [1, 2, -4, 5] = true := by
  decide

/-- The supplied regression tests all agree with the implementation. -/
theorem belowZero_tests_pass : belowZeroTests.all
    (fun (input, expected) => belowZero input == expected) = true := by
  decide
