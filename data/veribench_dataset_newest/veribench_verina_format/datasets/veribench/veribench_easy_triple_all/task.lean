-- !benchmark @start import type=solution
import Mathlib
namespace TripleAll
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def tripleAll_precond (xs : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def tripleAll (xs : List Int) (h_precond : tripleAll_precond (xs)) : List Int :=
  -- !benchmark @start code
  xs.map (· * 3)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def tripleAll_postcond (xs : List Int) (result : List Int) (h_precond : tripleAll_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  (result = [] ∧ tripleAll ([] : List Int) (by simp) = []) ∧
    (result.length = xs.length) ∧
    (result = xs.map (· * 3)) ∧
    (∀ x : Int, tripleAll [x] (by simp) = [x * 3]) ∧
    (tripleAll [0] (by simp) = [0])
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def empty_list_prop : Prop := tripleAll ([] : List Int) (by simp) = []

@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

def length_preservation_prop (xs : List Int) : Prop :=
  (tripleAll xs (by simp)).length = xs.length

@[simp] theorem length_preservation_thm (xs : List Int) : length_preservation_prop xs := by
  sorry

def triple_correctness_prop (xs : List Int) : Prop :=
  tripleAll xs (by simp) = xs.map (· * 3)

@[simp] theorem triple_correctness_thm (xs : List Int) : triple_correctness_prop xs := by
  sorry

def single_element_prop (x : Int) : Prop :=
  tripleAll [x] (by simp) = [x * 3]

@[simp] theorem single_element_thm (x : Int) : single_element_prop x := by
  sorry

def zero_preservation_prop : Prop :=
  tripleAll [0] (by simp) = [0]

@[simp] theorem zero_preservation_thm : zero_preservation_prop := by
  sorry

-- !benchmark @end proof_aux

theorem tripleAll_spec_satisfied (xs : List Int) (h_precond : tripleAll_precond (xs)) :
    tripleAll_postcond (xs) (tripleAll (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof