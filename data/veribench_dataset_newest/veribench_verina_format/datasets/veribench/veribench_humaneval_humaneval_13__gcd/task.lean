-- !benchmark @start import type=solution
import Mathlib
namespace MyGcd
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def gcd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def gcd (a : Nat) (b : Nat) (h_precond : gcd_precond (a) (b)) : Nat :=
  -- !benchmark @start code
  if b = 0 then a else gcd b (a % b) (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def gcd_postcond (a : Nat) (b : Nat) (result : Nat) (h_precond : gcd_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  (result = gcd (a) (b) h_precond) ∧
  (gcd a a (by simp) = a) ∧
  (gcd a 0 (by simp) = a ∧ gcd 0 a (by simp) = a) ∧
  (gcd a b (by simp) = gcd b a (by simp)) ∧
  (let g := gcd a b (by simp); (a % g = 0) ∧ (b % g = 0)) ∧
  (∀ d, (a % d = 0 ∧ b % d = 0) → d ≤ gcd a b (by simp))
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def gcd_self_prop (a : Nat) : Prop := gcd a a (by simp) = a
@[simp] theorem gcd_self_thm (a : Nat) : gcd_self_prop a := by sorry

def gcd_zero_prop (a : Nat) : Prop := gcd a 0 (by simp) = a ∧ gcd 0 a (by simp) = a
@[simp] theorem gcd_zero_thm (a : Nat) : gcd_zero_prop a := by sorry

def commutativity_prop (a b : Nat) : Prop := gcd a b (by simp) = gcd b a (by simp)
@[simp] theorem commutativity_thm (a b : Nat) : commutativity_prop a b := by sorry

def divisibility_prop (a b : Nat) : Prop :=
  let g := gcd a b (by simp)
  (a % g = 0) ∧ (b % g = 0)
@[simp] theorem divisibility_thm (a b : Nat) : divisibility_prop a b := by sorry

def maximality_prop (a b : Nat) : Prop :=
  ∀ d, (a % d = 0 ∧ b % d = 0) → d ≤ gcd a b (by simp)
@[simp] theorem maximality_thm (a b : Nat) : maximality_prop a b := by sorry

-- !benchmark @end proof_aux

theorem gcd_spec_satisfied (a : Nat) (b : Nat) (h_precond : gcd_precond (a) (b)) :
    gcd_postcond (a) (b) (gcd (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof