-- !benchmark @start import type=solution
import Mathlib
namespace MyMaxList
-- !benchmark @end import

-- !benchmark @start solution_aux
-- (no additional solution-level auxiliaries)
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- (no additional precondition auxiliaries)
-- !benchmark @end precond_aux

@[reducible, simp]
def myMaxList_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  xs.length > 0
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- (no additional code auxiliaries)
-- !benchmark @end code_aux

def myMaxList : List Nat → Nat
  | [] => 0
  | [x] => x
  | x :: xs => max x (myMaxList xs)
def myMaxList_wrapped (xs : List Nat) (h_precond : myMaxList_precond (xs)) : Nat :=
  -- !benchmark @start code
  myMaxList xs
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- (no additional postcondition auxiliaries)
-- !benchmark @end postcond_aux

@[reducible, simp]
def myMaxList_postcond (xs : List Nat) (result : Nat) (h_precond : myMaxList_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  (myMaxList [] = 0) ∧
    (∀ x, x ∈ xs → x ≤ result) ∧
    (xs ≠ [] → result ∈ xs)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- Property defs/theorems from the original file (kept as auxiliaries for the proof)
def max_empty_prop : Prop := myMaxList [] = 0
theorem max_empty_thm : max_empty_prop := by
  sorry

def max_upper_bound_prop (xs : List Nat) : Prop :=
  ∀ x, x ∈ xs → x ≤ myMaxList xs
theorem max_upper_bound_thm (xs : List Nat) : max_upper_bound_prop xs := by
  sorry

def max_is_member_prop (xs : List Nat) : Prop :=
  xs ≠ [] → myMaxList xs ∈ xs
theorem max_is_member_thm (xs : List Nat) : max_is_member_prop xs := by
  sorry
-- !benchmark @end proof_aux

theorem myMaxList_spec_satisfied (xs : List Nat) (h_precond : myMaxList_precond (xs)) :
    myMaxList_postcond (xs) (myMaxList_wrapped (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof
end MyMaxList