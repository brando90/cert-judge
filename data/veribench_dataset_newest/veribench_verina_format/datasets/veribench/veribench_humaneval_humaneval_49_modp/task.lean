-- !benchmark @start import type=solution
import Mathlib
namespace ModExp
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def modp_precond (n : Nat) (p : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def modp (n : Nat) (p : Nat) (h_precond : modp_precond (n) (p)) : Nat :=
  -- !benchmark @start code
  let rec loop (i acc : Nat) : Nat :=
    match i with
    | 0 => acc
    | i' + 1 => loop i' ((2 * acc) % p)
  loop n 1
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def modp_postcond (n : Nat) (p : Nat) (result : Nat) (h_precond : modp_precond (n) (p)) : Prop :=
  -- !benchmark @start postcond
  (result = modp (n) (p) h_precond) ∧
  (modp 0 p (by simp) = 1) ∧
  (modp (n + 1) p (by simp) = (2 * modp n p (by simp)) % p) ∧
  (p > 0 → modp n p (by simp) = Nat.pow 2 n % p) ∧
  (p > 0 → modp n p (by simp) < p)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def base_case_prop (p : Nat) : Prop := modp 0 p (by simp) = 1
theorem base_case_thm (p : Nat) : base_case_prop p := by sorry

def recursive_prop (n p : Nat) : Prop := modp (n + 1) p (by simp) = (2 * modp n p (by simp)) % p
theorem recursive_thm (n p : Nat) : recursive_prop n p := by sorry

def modular_equiv_prop (n p : Nat) : Prop := p > 0 → modp n p (by simp) = Nat.pow 2 n % p
theorem modular_equiv_thm (n p : Nat) : modular_equiv_prop n p := by sorry

def result_bound_prop (n p : Nat) : Prop := p > 0 → modp n p (by simp) < p
theorem result_bound_thm (n p : Nat) : result_bound_prop n p := by sorry

-- !benchmark @end proof_aux

theorem modp_spec_satisfied (n : Nat) (p : Nat) (h_precond : modp_precond (n) (p)) :
    modp_postcond (n) (p) (modp (n) (p) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof