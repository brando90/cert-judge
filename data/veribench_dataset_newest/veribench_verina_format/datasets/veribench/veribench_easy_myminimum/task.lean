-- !benchmark @start import type=solution
import Mathlib
namespace MyMinList
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myMinList_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myMinList (xs : List Nat) (h_precond : myMinList_precond (xs)) : Nat :=
  -- !benchmark @start code
  match xs with
  | [] => 0
  | [x] => x
  | x :: xs => min x (myMinList xs (by simp))
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myMinList_postcond (xs : List Nat) (result : Nat) (h_precond : myMinList_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def empty_list_prop : Prop := myMinList [] (by simp) = 0
@[simp] theorem empty_list_thm : empty_list_prop := by sorry

def single_element_prop (x : Nat) : Prop := myMinList [x] (by simp) = x
@[simp] theorem single_element_thm (x : Nat) : single_element_prop x := by sorry

def minimum_prop (xs : List Nat) : Prop :=
  xs ≠ [] → (myMinList xs (by simp) ∈ xs ∧ ∀ z ∈ xs, myMinList xs (by simp) ≤ z)
@[simp] theorem minimum_thm (xs : List Nat) : minimum_prop xs := by sorry

def membership_prop (xs : List Nat) : Prop :=
  xs ≠ [] → myMinList xs (by simp) ∈ xs
@[simp] theorem membership_thm (xs : List Nat) : membership_prop xs := by sorry

def two_elements_prop (x y : Nat) : Prop := myMinList [x, y] (by simp) = min x y
@[simp] theorem two_elements_thm (x y : Nat) : two_elements_prop x y := by sorry

-- !benchmark @end proof_aux

theorem myMinList_spec_satisfied (xs : List Nat) (h_precond : myMinList_precond (xs)) :
    myMinList_postcond (xs) (myMinList (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof