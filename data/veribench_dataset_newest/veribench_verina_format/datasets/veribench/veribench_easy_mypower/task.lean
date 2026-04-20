-- !benchmark @start import type=solution
import Mathlib
namespace MyPower
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myPower_precond (b : Nat) (e : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myPower : Nat → Nat → Nat
  | _, 0 => 1
  | b, e + 1 => b * myPower b e

def myPower (b : Nat) (e : Nat) (h_precond : myPower_precond (b) (e)) : Nat :=
  -- !benchmark @start code
  myPower b e
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

def power_zero_prop (b : Nat) : Prop := myPower b 0 = 1
@[simp] theorem power_zero_thm (b : Nat) : power_zero_prop b := by sorry

def power_one_prop (b : Nat) : Prop := myPower b 1 = b
@[simp] theorem power_one_thm (b : Nat) : power_one_prop b := by sorry

def power_zero_base_prop (e : Nat) : Prop := e > 0 → myPower 0 e = 0
@[simp] theorem power_zero_base_thm (e : Nat) : power_zero_base_prop e := by sorry

def power_one_base_prop (e : Nat) : Prop := myPower 1 e = 1
@[simp] theorem power_one_base_thm (e : Nat) : power_one_base_prop e := by sorry

def power_succ_prop (b e : Nat) : Prop := myPower b (e + 1) = b * myPower b e
@[simp] theorem power_succ_thm (b e : Nat) : power_succ_prop b e := by sorry

@[reducible, simp]
def myPower_postcond (b : Nat) (e : Nat) (result : Nat) (h_precond : myPower_precond (b) (e)) :=
  -- !benchmark @start postcond
  (power_zero_prop b) ∧
  (power_one_prop b) ∧
  (power_zero_base_prop e) ∧
  (power_one_base_prop e) ∧
  (power_succ_prop b e)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem myPower_spec_satisfied (b : Nat) (e : Nat) (h_precond : myPower_precond (b) (e)) :
    myPower_postcond (b) (e) (myPower (b) (e) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof