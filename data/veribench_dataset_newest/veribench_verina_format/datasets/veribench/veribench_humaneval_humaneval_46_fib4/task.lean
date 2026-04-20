-- !benchmark @start import type=solution
import Mathlib
namespace Fib4
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def fib4_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def fib4 (n : Nat) (h_precond : fib4_precond (n)) : Nat :=
  -- !benchmark @start code
  let rec loop (i : Nat) (a b c d : Nat) : Nat :=
    match i with
    | 0 => d
    | i' + 1 => loop i' b c d (a + b + c + d)
  match n with
  | 0 => 0
  | 1 => 0
  | 2 => 2
  | 3 => 0
  | n' + 4 => loop n' 0 0 2 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def fib4_postcond (n : Nat) (result : Nat) (h_precond : fib4_precond (n)) :=
  -- !benchmark @start postcond
  (base_cases_prop n) ∧
    (non_negative_prop n) ∧
    (recurrence_prop n) ∧
    (monotonicity_prop n)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Base cases property**: The first four elements of the sequence are correct. -/
def base_cases_prop (n : Nat) : Prop :=
  (n = 0 → fib4 n (by simp) = 0) ∧
    (n = 1 → fib4 n (by simp) = 0) ∧
    (n = 2 → fib4 n (by simp) = 2) ∧
    (n = 3 → fib4 n (by simp) = 0)

/-- **Base cases theorem**: The first four elements of the sequence are correct. -/
@[simp] theorem base_cases_thm (n : Nat) : base_cases_prop n := by
  sorry

/-- **Non-negative property**: All elements of the sequence are non-negative. -/
def non_negative_prop (n : Nat) : Prop :=
  fib4 n (by simp) ≥ 0

/-- **Non-negative theorem**: All elements of the sequence are non-negative. -/
@[simp] theorem non_negative_thm (n : Nat) : non_negative_prop n := by
  sorry

/-- **Recurrence relation property**: Each element is the sum of the previous four for n ≥ 4. -/
def recurrence_prop (n : Nat) : Prop :=
  n ≥ 4 →
    fib4 n (by simp) =
      fib4 (n - 1) (by simp) + fib4 (n - 2) (by simp) + fib4 (n - 3) (by simp) + fib4 (n - 4) (by simp)

/-- **Recurrence relation theorem**: Each element is the sum of the previous four for n ≥ 4. -/
@[simp] theorem recurrence_thm (n : Nat) : recurrence_prop n := by
  sorry

/-- **Monotonicity property**: The sequence is non-decreasing for n ≥ 5. -/
def monotonicity_prop (n : Nat) : Prop :=
  n ≥ 5 → fib4 n (by simp) ≤ fib4 (n + 1) (by simp)

/-- **Monotonicity theorem**: The sequence is non-decreasing for n ≥ 5. -/
@[simp] theorem monotonicity_thm (n : Nat) : monotonicity_prop n := by
  sorry
-- !benchmark @end proof_aux

theorem fib4_spec_satisfied (n : Nat) (h_precond : fib4_precond (n)) :
    fib4_postcond (n) (fib4 (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof

end Fib4