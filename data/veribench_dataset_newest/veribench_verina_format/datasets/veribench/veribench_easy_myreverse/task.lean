-- !benchmark @start import type=solution
import Mathlib
namespace MyReverse
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myReverse_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myReverse (xs : List Nat) (h_precond : myReverse_precond (xs)) : List Nat :=
  -- !benchmark @start code
  match xs with
  | [] => []
  | x :: xs => myReverse xs (by simp) ++ [x]
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp] def reverse_involution_prop (xs : List Nat) : Prop := myReverse (myReverse xs (by simp)) (by simp) = xs
@[simp] theorem reverse_involution_thm (xs : List Nat) : reverse_involution_prop xs := by
  sorry

@[reducible, simp] def reverse_length_prop (xs : List Nat) : Prop := (myReverse xs (by simp)).length = xs.length
@[simp] theorem reverse_length_thm (xs : List Nat) : reverse_length_prop xs := by
  sorry

@[reducible, simp]
def reverse_append_prop (xs ys : List Nat) : Prop :=
  myReverse (xs ++ ys) (by simp) = myReverse ys (by simp) ++ myReverse xs (by simp)

@[simp] theorem reverse_append_thm (xs ys : List Nat) : reverse_append_prop xs ys := by
  sorry

@[reducible, simp] def reverse_mem_prop (xs : List Nat) (x : Nat) : Prop := x ∈ xs ↔ x ∈ myReverse xs (by simp)
@[simp] theorem reverse_mem_thm (xs : List Nat) (x : Nat) : reverse_mem_prop xs x := by
  sorry

@[reducible, simp]
def myReverse_postcond (xs : List Nat) (result : List Nat) (h_precond : myReverse_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  (reverse_involution_prop xs) ∧
    (reverse_length_prop xs) ∧
    (∀ ys, reverse_append_prop xs ys) ∧
    (∀ x, reverse_mem_prop xs x)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem myReverse_spec_satisfied (xs : List Nat) (h_precond : myReverse_precond (xs)) :
    myReverse_postcond (xs) (myReverse (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof