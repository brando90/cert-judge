-- !benchmark @start import type=solution
import Mathlib
namespace FilterIntegers
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def filter_integers_precond (values : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def filter_integers (values : List Int) (h_precond : filter_integers_precond (values)) : List Int :=
  -- !benchmark @start code
  List.filter (fun x => true) values
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp] def identity_prop (values : List Int) : Prop := filter_integers (values) (by simp) = values
@[simp] theorem identity_thm (values : List Int) : identity_prop values := by
  sorry

@[reducible, simp] def empty_list_prop : Prop := filter_integers ([]) (by simp) = []
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

@[reducible, simp]
def length_preservation_prop (values : List Int) : Prop :=
  (filter_integers (values) (by simp)).length = values.length
@[simp] theorem length_preservation_thm (values : List Int) : length_preservation_prop values := by
  sorry

@[reducible, simp]
def order_preservation_prop (values : List Int) : Prop :=
  ∀ i j,
    i < j →
      i < values.length →
        j < values.length →
          values.idxOf (filter_integers (values) (by simp))[i]! ≤ values.idxOf (filter_integers (values) (by simp))[j]!
@[simp] theorem order_preservation_thm (values : List Int) : order_preservation_prop values := by
  sorry

@[reducible, simp]
def membership_prop (values : List Int) : Prop :=
  ∀ x ∈ filter_integers (values) (by simp), x ∈ values
@[simp] theorem membership_thm (values : List Int) : membership_prop values := by
  sorry

@[reducible, simp]
def filter_integers_postcond (values : List Int) (result : List Int)
    (h_precond : filter_integers_precond (values)) : Prop :=
  -- !benchmark @start postcond
  (identity_prop values) ∧
    (empty_list_prop) ∧
    (length_preservation_prop values) ∧
    (order_preservation_prop values) ∧
    (membership_prop values)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem filter_integers_spec_satisfied (values : List Int) (h_precond : filter_integers_precond (values)) :
    filter_integers_postcond (values) (filter_integers (values) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof