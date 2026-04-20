-- !benchmark @start import type=solution
import Mathlib
namespace MyFibonacci
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myFibonacci_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myFibonacci (n : Nat) (h_precond : myFibonacci_precond (n)) : Nat :=
  -- !benchmark @start code
  match n with
  | 0 => 0
  | 1 => 1
  | n + 2 => myFibonacci n (by simp) + myFibonacci (n + 1) (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myFibonacci_postcond (n : Nat) (result : Nat) (h_precond : myFibonacci_precond (n)) :=
  -- !benchmark @start postcond
  (myFibonacci 0 (by simp) = 0) ∧
    (myFibonacci 1 (by simp) = 1) ∧
    (myFibonacci (n + 2) (by simp) = myFibonacci n (by simp) + myFibonacci (n + 1) (by simp)) ∧
    (myFibonacci n (by simp) ≥ 0) ∧
    (n ≥ 1 → myFibonacci (n + 1) (by simp) > myFibonacci n (by simp))
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def fibonacci_zero_prop : Prop := myFibonacci 0 (by simp) = 0
@[simp] theorem fibonacci_zero_thm : fibonacci_zero_prop := by sorry

def fibonacci_one_prop : Prop := myFibonacci 1 (by simp) = 1
@[simp] theorem fibonacci_one_thm : fibonacci_one_prop := by sorry

def fibonacci_rec_prop (n : Nat) : Prop :=
  myFibonacci (n + 2) (by simp) = myFibonacci n (by simp) + myFibonacci (n + 1) (by simp)
@[simp] theorem fibonacci_rec_thm (n : Nat) : fibonacci_rec_prop n := by sorry

def fibonacci_nonneg_prop (n : Nat) : Prop := myFibonacci n (by simp) ≥ 0
@[simp] theorem fibonacci_nonneg_thm (n : Nat) : fibonacci_nonneg_prop n := by sorry

def fibonacci_increasing_prop (n : Nat) : Prop := n ≥ 1 → myFibonacci (n + 1) (by simp) > myFibonacci n (by simp)
@[simp] theorem fibonacci_increasing_thm (n : Nat) : fibonacci_increasing_prop n := by sorry

-- !benchmark @end proof_aux

theorem myFibonacci_spec_satisfied (n : Nat) (h_precond : myFibonacci_precond (n)) :
    myFibonacci_postcond (n) (myFibonacci (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof