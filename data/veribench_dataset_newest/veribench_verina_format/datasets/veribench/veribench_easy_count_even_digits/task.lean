-- !benchmark @start import type=solution
import Mathlib
namespace CountEvenDigits
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Check if a character represents an even digit -/
def isEvenDigit (c : Char) : Bool :=
  match c.toNat - '0'.toNat with
  | 0 | 2 | 4 | 6 | 8 => true
  | _ => false
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def countEvenDigits_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def countEvenDigits (n : Nat) (h_precond : countEvenDigits_precond (n)) : Nat :=
  -- !benchmark @start code
  (toString n).toList.foldl (fun acc c => if isEvenDigit c then acc + 1 else acc) 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def countEvenDigits_postcond (n : Nat) (result : Nat) (h_precond : countEvenDigits_precond (n)) : Prop :=
  -- !benchmark @start postcond
  (result = countEvenDigits (n) h_precond) ∧
  (countEvenDigits (0) (by simp) = 1) ∧
  (∀ d, (d < 10 ∧ d % 2 = 0 → countEvenDigits (d) (by simp) = 1)) ∧
  (∀ d, (d < 10 ∧ d % 2 = 1 → countEvenDigits (d) (by simp) = 0)) ∧
  (countEvenDigits (n) h_precond ≥ 0) ∧
  (countEvenDigits (n) h_precond ≤ (toString n).length)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem countEvenDigits_spec_satisfied (n : Nat) (h_precond : countEvenDigits_precond (n)) :
    countEvenDigits_postcond (n) (countEvenDigits (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof