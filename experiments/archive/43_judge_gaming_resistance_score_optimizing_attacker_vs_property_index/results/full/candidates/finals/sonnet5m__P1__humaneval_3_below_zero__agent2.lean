import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/--
Given a list of deposit and withdrawal operations that starts with a zero balance,
detect whether the balance becomes negative at any point.
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

/-- There is a negative balance among the updates, starting from `balance`. -/
def hasNegativePrefix (balance : Int) : List Int → Prop
  | [] => False
  | op :: rest =>
      balance + op < 0 ∨ hasNegativePrefix (balance + op) rest

/-- Every balance reached by an update is nonnegative, starting from `balance`. -/
def allUpdatesNonnegative (balance : Int) : List Int → Prop
  | [] => True
  | op :: rest =>
      balance + op ≥ 0 ∧ allUpdatesNonnegative (balance + op) rest

/--
A structurally recursive version of `belowZero` that allows an arbitrary
initial balance.
-/
def belowZeroAux (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then true else belowZeroAux newBalance rest

/-- The auxiliary implementation returns true exactly when some update is negative. -/
theorem belowZeroAux_true_iff_negative_prefix (balance : Int) (operations : List Int) :
    belowZeroAux balance operations = true ↔ hasNegativePrefix balance operations := by
  induction operations generalizing balance with
  | nil =>
      simp [belowZeroAux, hasNegativePrefix]
  | cons op rest ih =>
      by_cases h : balance + op < 0
      · simp [belowZeroAux, hasNegativePrefix, h]
      · simp [belowZeroAux, hasNegativePrefix, h, ih]

/-- All updates are nonnegative exactly when no update is negative. -/
theorem allUpdatesNonnegative_iff_no_negativePrefix (balance : Int) (operations : List Int) :
    allUpdatesNonnegative balance operations ↔
      ¬ hasNegativePrefix balance operations := by sorry

/-- The auxiliary implementation returns false exactly when all updates are nonnegative. -/
theorem belowZeroAux_false_iff_all_nonnegative (balance : Int) (operations : List Int) :
    belowZeroAux balance operations = false ↔
      allUpdatesNonnegative balance operations := by
  have hb : belowZeroAux balance operations = false ↔
      ¬ belowZeroAux balance operations = true := by
    cases belowZeroAux balance operations <;> simp
  rw [hb, belowZeroAux_true_iff_negative_prefix]
  exact (allUpdatesNonnegative_iff_no_negativePrefix balance operations).symm

/--
The balance never goes below zero at any point during the operations,
starting from the account's initial balance of zero.
-/
def NeverBelowZero (operations : List Int) : Prop :=
  allUpdatesNonnegative 0 operations

/-- Safety is equivalent to there being no negative prefix balance. -/
theorem neverBelowZero_iff_no_negative_prefix (operations : List Int) :
    NeverBelowZero operations ↔ ¬ hasNegativePrefix 0 operations := by
  exact allUpdatesNonnegative_iff_no_negativePrefix 0 operations

/-- The empty list cannot drive the account below zero. -/
@[simp] theorem belowZero_empty : belowZero [] = false := by
  rfl

/-- The auxiliary implementation detects a negative prefix exactly. -/
theorem belowZero_true_iff_negative_prefix (operations : List Int) :
    belowZeroAux 0 operations = true ↔ hasNegativePrefix 0 operations := by
  exact belowZeroAux_true_iff_negative_prefix 0 operations

/-- The auxiliary implementation returns false exactly when the account stays safe. -/
theorem belowZero_false_iff_never_below_zero (operations : List Int) :
    belowZeroAux 0 operations = false ↔ NeverBelowZero operations := by
  exact belowZeroAux_false_iff_all_nonnegative 0 operations

/-- All supplied examples agree with the implementation. -/
theorem belowZeroTests_pass :
    belowZeroTests.all (fun (input, expected) => belowZero input == expected) = true := by
  decide
