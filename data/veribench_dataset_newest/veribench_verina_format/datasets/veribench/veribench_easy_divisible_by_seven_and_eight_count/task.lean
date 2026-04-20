-- !benchmark @start import type=solution
import Mathlib
namespace CountDivBy7And8
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Returns true if the natural number is divisible by both 7 and 8. -/
def isDivBy7And8 (n : Nat) : Bool :=
  n % 7 == 0 && n % 8 == 0
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def countDivBy7And8_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def countDivBy7And8 (xs : List Nat) (h_precond : countDivBy7And8_precond (xs)) : Nat :=
  -- !benchmark @start code
  xs.foldl (fun acc x => if isDivBy7And8 x then acc + 1 else acc) 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def countDivBy7And8_postcond (xs : List Nat) (result : Nat) (h_precond : countDivBy7And8_precond (xs)) :=
  -- !benchmark @start postcond
  let empty_list_prop : Prop := countDivBy7And8 ([]) (by simp) = 0
  let divisible_56_prop : Nat → Prop := fun n => n % 56 = 0 → countDivBy7And8 ([n]) (by simp) = 1
  let not_divisible_prop : Nat → Prop := fun n => (n % 7 ≠ 0 ∨ n % 8 ≠ 0) → countDivBy7And8 ([n]) (by simp) = 0
  let non_negative_prop : List Nat → Prop := fun xs => countDivBy7And8 (xs) (by simp) ≥ 0
  let append_additivity_prop : List Nat → List Nat → Prop :=
    fun xs ys => countDivBy7And8 (xs ++ ys) (by simp) = countDivBy7And8 (xs) (by simp) + countDivBy7And8 (ys) (by simp)

  empty_list_prop ∧
    (∀ n, divisible_56_prop n) ∧
    (∀ n, not_divisible_prop n) ∧
    (non_negative_prop xs) ∧
    (∀ ys, append_additivity_prop xs ys) ∧
    (result = countDivBy7And8 (xs) h_precond)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem countDivBy7And8_spec_satisfied (xs : List Nat) (h_precond : countDivBy7And8_precond (xs)) :
    countDivBy7And8_postcond (xs) (countDivBy7And8 (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof