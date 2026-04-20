-- !benchmark @start import type=solution
import Mathlib
namespace AllEven

open List
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def allEven_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def allEven (xs : List Nat) (h_precond : allEven_precond (xs)) : Bool :=
  -- !benchmark @start code
  xs.all (fun x => x % 2 = 0)
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


-- Property props/theorems used by the postcondition
def empty_list_prop : Prop := allEven [] (by simp) = true

@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

def all_even_prop (xs : List Nat) : Prop :=
  allEven xs (by simp) = true → ∀ x ∈ xs, x % 2 = 0

@[simp] theorem all_even_thm (xs : List Nat) : all_even_prop xs := by
  sorry

def single_even_prop (x : Nat) : Prop := x % 2 = 0 → allEven [x] (by simp) = true

@[simp] theorem single_even_thm (x : Nat) : single_even_prop x := by
  sorry

def contains_odd_prop (xs : List Nat) : Prop :=
  (∃ x ∈ xs, x % 2 = 1) → allEven xs (by simp) = false

@[simp] theorem contains_odd_thm (xs : List Nat) : contains_odd_prop xs := by
  sorry

def boolean_result_prop (xs : List Nat) : Prop :=
  allEven xs (by simp) = true ∨ allEven xs (by simp) = false

@[simp] theorem boolean_result_thm (xs : List Nat) : boolean_result_prop xs := by
  sorry


@[reducible, simp]
def allEven_postcond (xs : List Nat) (result : Bool) (h_precond : allEven_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
    (all_even_prop xs) ∧
    (∀ x, single_even_prop x) ∧
    (contains_odd_prop xs) ∧
    (boolean_result_prop xs)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem allEven_spec_satisfied (xs : List Nat) (h_precond : allEven_precond (xs)) :
    allEven_postcond (xs) (allEven (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof