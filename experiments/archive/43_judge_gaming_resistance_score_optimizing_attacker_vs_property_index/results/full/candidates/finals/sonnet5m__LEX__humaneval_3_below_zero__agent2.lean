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

/-- The balances reached after each operation, starting from `balance`. -/
def prefixBalancesFrom (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      (balance + op) :: prefixBalancesFrom (balance + op) rest

/-- The balances reached after each operation, starting from zero. -/
def prefixBalances (operations : List Int) : List Int :=
  prefixBalancesFrom 0 operations

/-- Whether a negative balance occurs when processing operations from `balance`. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then true
      else belowZeroFrom newBalance rest

/-- The final balance after processing all operations from zero. -/
def balanceAfter (operations : List Int) : Int :=
  operations.foldl (fun balance op => balance + op) 0

/-- A negative balance occurs in the list of balances after operations. -/
def HasNegativePrefix (operations : List Int) : Prop :=
  ∃ balance, balance ∈ prefixBalances operations ∧ balance < 0

/-- The implementation returns true exactly when some prefix balance is negative. -/
theorem belowZero_correct (operations : List Int) :
    belowZero operations = true ↔ HasNegativePrefix operations := by
  sorry

/-- The implementation returns false exactly when every prefix balance is nonnegative. -/
theorem belowZero_false_iff_NeverBelowZero (operations : List Int) :
    belowZero operations = false ↔ NeverBelowZero operations := by
  sorry

/-- The explicit prefix-balance specification agrees with `NeverBelowZero`. -/
theorem NeverBelowZero_iff_all_prefixBalances_nonnegative
    (operations : List Int) :
    NeverBelowZero operations ↔
      ∀ balance, balance ∈ prefixBalances operations → 0 ≤ balance := by
  sorry

/-- Correctness of the negative-balance check for an arbitrary initial balance. -/
theorem belowZeroFrom_correct (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations = true ↔
      ∃ finalBalance, finalBalance ∈ prefixBalancesFrom balance operations ∧
        finalBalance < 0 := by
  sorry

/-- Starting from zero in the generalized check gives the implementation. -/
theorem belowZero_eq_belowZeroFrom (operations : List Int) :
    belowZero operations = belowZeroFrom 0 operations := by
  sorry

/-- Processing a concatenation adds the balances of its two parts. -/
theorem balanceAfter_append (operations₁ operations₂ : List Int) :
    balanceAfter (operations₁ ++ operations₂) =
      balanceAfter operations₁ + balanceAfter operations₂ := by
  sorry

/-- Once a prefix has caused an overdraft, appending more operations cannot undo it. -/
theorem belowZero_append_of_true (operations₁ operations₂ : List Int)
    (h : belowZero operations₁ = true) :
    belowZero (operations₁ ++ operations₂) = true := by
  sorry

/-- An empty sequence performs no overdraft. -/
theorem belowZero_nil : belowZero [] = false := by
  decide

/-- For a single operation, an overdraft occurs exactly when it is negative. -/
theorem belowZero_singleton (op : Int) :
    belowZero [op] = true ↔ op < 0 := by
  sorry

/-- Examples from the task description and tests. -/
example : belowZero [1, 2, 3] = false := by decide
example : belowZero [1, 2, -4, 5] = true := by decide
example : belowZero [1, 2, -3, 1, 2, -3] = false := by decide
example : belowZero [1, 2, -4, 5, 6] = true := by decide
example : belowZero [1, -1, 2, -2, 5, -5, 4, -4] = false := by decide
example : belowZero [1, -1, 2, -2, 5, -5, 4, -5] = true := by decide
example : belowZero [1, -2, 2, -2, 5, -5, 4, -4] = true := by decide
