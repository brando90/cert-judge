-- !benchmark @start import type=solution
import Mathlib
namespace IncrementList
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def incr_list_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def incr_list (l : List Int) (h_precond : incr_list_precond (l)) : List Int :=
  -- !benchmark @start code
  l.map (· + 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp] def length_preservation_prop (l : List Int) : Prop :=
  (incr_list (l) (by simp)).length = l.length

@[simp] theorem length_preservation_thm (l : List Int) : length_preservation_prop l := by
  sorry

@[reducible, simp] def empty_list_prop : Prop :=
  incr_list ([]) (by simp) = []

@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

@[reducible, simp] def element_increment_prop (l : List Int) : Prop :=
  ∀ i, i < l.length → (incr_list (l) (by simp))[i]! = l[i]! + 1

@[simp] theorem element_increment_thm (l : List Int) : element_increment_prop l := by
  sorry

@[reducible, simp] def distributivity_prop (l₁ l₂ : List Int) : Prop :=
  incr_list (l₁ ++ l₂) (by simp) = incr_list (l₁) (by simp) ++ incr_list (l₂) (by simp)

@[simp] theorem distributivity_thm (l₁ l₂ : List Int) : distributivity_prop l₁ l₂ := by
  sorry

@[reducible, simp]
def incr_list_postcond (l : List Int) (result : List Int) (h_precond : incr_list_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (length_preservation_prop l) ∧
    (empty_list_prop) ∧
    (element_increment_prop l) ∧
    (∀ l₂, distributivity_prop l l₂)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem incr_list_spec_satisfied (l : List Int) (h_precond : incr_list_precond (l)) :
    incr_list_postcond (l) (incr_list (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof