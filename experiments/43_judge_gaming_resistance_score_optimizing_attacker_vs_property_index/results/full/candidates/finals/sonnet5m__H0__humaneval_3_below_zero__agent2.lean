import Mathlib
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

/-- The balances reached after each operation, in their original order. -/
def balancesFrom (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      let nextBalance := balance + op
      nextBalance :: balancesFrom nextBalance rest

/-- The balances reached after each prefix of the operations. -/
def prefixBalances (operations : List Int) : List Int :=
  balancesFrom 0 operations

/-- There is a prefix of the operations whose balance is negative. -/
def HasNegativePrefix (operations : List Int) : Prop :=
  ∃ balance, balance ∈ prefixBalances operations ∧ balance < 0

/-- A Boolean executable version of the negative-prefix specification. -/
def belowZeroSpec (operations : List Int) : Bool :=
  (prefixBalances operations).any (fun balance => decide (balance < 0))

/-- The result of running the account check from an arbitrary initial balance. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      if balance + op < 0 then true
      else belowZeroFrom (balance + op) rest

/-- The recursive checker detects exactly a negative balance in the resulting list. -/
theorem belowZeroFrom_true_iff (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations = true ↔
      ∃ b, b ∈ balancesFrom balance operations ∧ b < 0 := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroFrom, balancesFrom]
  | cons op rest ih =>
      simp [belowZeroFrom, balancesFrom, ih]

/-- The implementation is the arbitrary-balance checker started at zero. -/
theorem belowZero_eq_belowZeroFrom (operations : List Int) :
    belowZero operations = belowZeroFrom 0 operations := by sorry

/--
The implementation returns true exactly when a balance reached after some
prefix of the operations is negative.
-/
theorem belowZero_true_iff_hasNegativePrefix (operations : List Int) :
    belowZero operations = true ↔ HasNegativePrefix operations := by
  rw [belowZero_eq_belowZeroFrom]
  simpa [HasNegativePrefix, prefixBalances] using
    (belowZeroFrom_true_iff 0 operations)

/-- The implementation agrees with the executable prefix-balance specification. -/
theorem belowZero_eq_belowZeroSpec (operations : List Int) :
    belowZero operations = belowZeroSpec operations := by sorry

/-- No balance reached after an operation is negative. -/
def NeverBelowZero (operations : List Int) : Prop :=
  ∀ balance, balance ∈ prefixBalances operations → 0 ≤ balance

/-- The account never goes below zero exactly when no prefix has a negative balance. -/
theorem neverBelowZero_iff_no_negative_prefix (operations : List Int) :
    NeverBelowZero operations ↔ ¬ HasNegativePrefix operations := by
  constructor
  · intro h hneg
    rcases hneg with ⟨balance, hmem, hlt⟩
    have hnonneg := h balance hmem
    omega
  · intro h balance hmem
    by_contra hnonneg
    apply h
    exact ⟨balance, hmem, by omega⟩

/-- The function returns false exactly when the account never goes below zero. -/
theorem belowZero_false_iff_neverBelowZero (operations : List Int) :
    belowZero operations = false ↔ NeverBelowZero operations := by
  constructor
  · intro hfalse balance hmem
    by_contra hnonneg
    have hneg : balance < 0 := by omega
    have hhas : HasNegativePrefix operations := ⟨balance, hmem, hneg⟩
    have htrue := (belowZero_true_iff_hasNegativePrefix operations).2 hhas
    rw [hfalse] at htrue
    contradiction
  · intro hnever
    cases h : belowZero operations with
    | false => rfl
    | true =>
        have hhas := (belowZero_true_iff_hasNegativePrefix operations).1 h
        rcases hhas with ⟨balance, hmem, hneg⟩
        have hnonneg := hnever balance hmem
        have hbad : False := by omega
        exact hbad.elim

/-- An empty sequence of operations never takes the balance below zero. -/
theorem belowZero_empty : belowZero ([] : List Int) = false := by
  rfl

/-- A negative first operation immediately takes the balance below zero. -/
theorem belowZero_negative_head (op : Int) (rest : List Int) (h : op < 0) :
    belowZero (op :: rest) = true := by sorry

/-- Nonnegative operations preserve a nonnegative balance at every prefix. -/
theorem balancesFrom_nonnegative (balance : Int) (operations : List Int)
    (hbalance : 0 ≤ balance) (hops : ∀ op ∈ operations, 0 ≤ op) :
    ∀ b ∈ balancesFrom balance operations, 0 ≤ b := by sorry

/-- Nonnegative operations cannot make an initially zero balance negative. -/
theorem belowZero_of_all_nonnegative (operations : List Int)
    (h : ∀ op ∈ operations, 0 ≤ op) :
    belowZero operations = false := by
  apply (belowZero_false_iff_neverBelowZero operations).2
  intro b hb
  exact balancesFrom_nonnegative 0 operations (by omega) h b hb

#eval belowZeroSpec ([1, 2, 3] : List Int)
#eval belowZeroSpec ([1, 2, -4, 5] : List Int)
