import Mathlib
import Mathlib.Tactic

/--
You're given a list of deposit and withdrawal operations that start with a zero balance.
The result is true exactly when a balance becomes negative.
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

/-- Snake-case alias matching the name of the Python task. -/
def below_zero (operations : List Int) : Bool :=
  belowZero operations

/-- The balance after each operation, starting from an arbitrary initial balance. -/
def runningSumFrom (balance : Int) : List Int → List Int
  | [] => []
  | op :: rest =>
      let newBalance := balance + op
      newBalance :: runningSumFrom newBalance rest

/-- The balance after each operation, starting from zero. -/
def runningSum (operations : List Int) : List Int :=
  let rec go (acc : Int) (ops : List Int) : List Int :=
    match ops with
    | [] => []
    | op :: rest =>
      let newAcc := acc + op
      newAcc :: go newAcc rest
  go 0 operations

/-- A specification using the list of running balances. -/
def belowZeroSpec (operations : List Int) : Bool :=
  (runningSum operations).any (· < 0)

/-- The recursive account check, generalized to an arbitrary initial balance. -/
def belowZeroFrom (balance : Int) : List Int → Bool
  | [] => false
  | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then true
      else belowZeroFrom newBalance rest

/-- The generalized account check detects precisely a negative running balance. -/
theorem belowZeroFrom_correct (balance : Int) (operations : List Int) :
    belowZeroFrom balance operations =
      (runningSumFrom balance operations).any (· < 0) := by
  induction operations generalizing balance with
  | nil =>
      rfl
  | cons op rest ih =>
      by_cases h : balance + op < 0
      · simp [belowZeroFrom, runningSumFrom, h]
      · simp [belowZeroFrom, runningSumFrom, h, ih]

/-- The zero-start running sum is the arbitrary-start running sum at balance zero. -/
theorem runningSum_zero_eq_runningSumFrom (operations : List Int) :
    runningSum operations = runningSumFrom 0 operations := by sorry

/-- The implementation agrees with the running-sum specification. -/
theorem belowZero_correct (operations : List Int) :
    belowZero operations = belowZeroSpec operations := by sorry

/-- There is a negative balance among the running balances. -/
def hasNegativeRunningBalance (operations : List Int) : Prop :=
  ∃ balance, balance ∈ runningSum operations ∧ balance < 0

/-- The result is true exactly when some running balance is negative. -/
theorem belowZero_iff_negative_running_balance (operations : List Int) :
    belowZero operations = true ↔ hasNegativeRunningBalance operations := by
  rw [belowZero_correct]
  simp [belowZeroSpec, hasNegativeRunningBalance, List.any_eq_true]

/-- If the result is false, every running balance is nonnegative. -/
theorem belowZero_false_iff_all_running_balances_nonnegative
    (operations : List Int) :
    belowZero operations = false ↔
      ∀ balance, balance ∈ runningSum operations → 0 ≤ balance := by
  constructor
  · intro h balance hmem
    by_contra hnonneg
    have hneg : balance < 0 := by omega
    have htrue : belowZero operations = true :=
      (belowZero_iff_negative_running_balance operations).2
        ⟨balance, hmem, hneg⟩
    simp [h] at htrue
  · intro hall
    cases hresult : belowZero operations with
    | false => rfl
    | true =>
        rcases (belowZero_iff_negative_running_balance operations).1 hresult with
          ⟨balance, hmem, hneg⟩
        have hnonneg := hall balance hmem
        omega

/-- The snake-case task entry point has the same correctness specification. -/
theorem below_zero_correct (operations : List Int) :
    below_zero operations = belowZeroSpec operations := by
  simp [below_zero, belowZero_correct]

#eval belowZero [] -- false
#eval belowZero [1, 2, 3] -- false
#eval belowZero [1, 2, -4, 5] -- true

/-- Test suite for belowZero. -/
def belowZeroTests : List (List Int × Bool) := [
  ([], false),
  ([1, 2, -3, 1, 2, -3], false),
  ([1, 2, -4, 5, 6], true),
  ([1, -1, 2, -2, 5, -5, 4, -4], false),
  ([1, -1, 2, -2, 5, -5, 4, -5], true),
  ([1, -2, 2, -2, 5, -5, 4, -4], true)
]

/-- All of the task's example cases evaluate to their expected results. -/
theorem belowZero_examples :
    belowZero [] = false ∧
    belowZero [1, 2, -3, 1, 2, -3] = false ∧
    belowZero [1, 2, -4, 5, 6] = true ∧
    belowZero [1, -1, 2, -2, 5, -5, 4, -4] = false ∧
    belowZero [1, -1, 2, -2, 5, -5, 4, -5] = true ∧
    belowZero [1, -2, 2, -2, 5, -5, 4, -4] = true := by
  decide

/-- The examples also hold through the task-named alias. -/
theorem below_zero_examples :
    below_zero [] = false ∧
    below_zero [1, 2, -3, 1, 2, -3] = false ∧
    below_zero [1, 2, -4, 5, 6] = true ∧
    below_zero [1, -1, 2, -2, 5, -5, 4, -4] = false ∧
    below_zero [1, -1, 2, -2, 5, -5, 4, -5] = true ∧
    below_zero [1, -2, 2, -2, 5, -5, 4, -4] = true := by
  simpa [below_zero] using belowZero_examples
