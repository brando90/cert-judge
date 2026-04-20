-- !benchmark @start import type=solution
import Mathlib
namespace MySquare
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def mySquare_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def mySquare (n : Nat) (h_precond : mySquare_precond (n)) : Nat :=
  -- !benchmark @start code
  n ^ 2
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def mySquare_postcond (n : Nat) (result : Nat) (h_precond : mySquare_precond (n)) : Prop :=
  -- !benchmark @start postcond
  result = n ^ 2
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def square_mult_equiv_prop (n : Nat) : Prop := mySquare (n) (by simp) = n * n

theorem square_mult_equiv_thm (n : Nat) : square_mult_equiv_prop n := by
  sorry

def square_nonneg_prop (n : Nat) : Prop := mySquare (n) (by simp) ≥ 0

theorem square_nonneg_thm (n : Nat) : square_nonneg_prop n := by
  sorry

-- !benchmark @end proof_aux

theorem mySquare_spec_satisfied (n : Nat) (h_precond : mySquare_precond (n)) :
    mySquare_postcond (n) (mySquare (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof