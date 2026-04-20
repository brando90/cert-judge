-- !benchmark @start import type=solution
import Mathlib
namespace MyAdd
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myAdd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  (0 ≤ a) ∧ (0 ≤ b)
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myAdd (a : Nat) (b : Nat) (h_precond : myAdd_precond (a) (b)) : Nat :=
  -- !benchmark @start code
  Nat.add a b
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myAdd_postcond (a : Nat) (b : Nat) (result : Nat) (h_precond : myAdd_precond (a) (b)) :=
  -- !benchmark @start postcond
  (result = a + b)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def right_identity_prop (n : Nat) : Prop := myAdd n 0 (by simp) = n
@[simp] theorem right_identity_thm (n : Nat) : right_identity_prop n := by
  sorry

def left_identity_prop (n : Nat) : Prop := myAdd 0 n (by simp) = n
@[simp] theorem left_identity_thm (n : Nat) : left_identity_prop n := by
  sorry

def commutativity_prop (a b : Nat) : Prop := myAdd a b (by simp) = myAdd b a (by simp)
@[simp] theorem commutativity_thm (a b : Nat) : commutativity_prop a b := by
  sorry

def associativity_prop (a b c : Nat) : Prop :=
  myAdd (myAdd a b (by simp)) c (by simp) = myAdd a (myAdd b c (by simp)) (by simp)
@[simp] theorem associativity_thm (a b c : Nat) : associativity_prop a b c := by
  sorry

-- !benchmark @end proof_aux

theorem myAdd_spec_satisfied (a : Nat) (b : Nat) (h_precond : myAdd_precond (a) (b)) :
    myAdd_postcond (a) (b) (myAdd (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof
end MyAdd