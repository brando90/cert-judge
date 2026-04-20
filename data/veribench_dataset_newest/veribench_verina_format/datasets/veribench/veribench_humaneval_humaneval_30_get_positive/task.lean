-- !benchmark @start import type=solution
import Mathlib
namespace PositiveFilter
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def get_positive_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def get_positive (l : List Int) (h_precond : get_positive_precond (l)) : List Int :=
  -- !benchmark @start code
  l.filter (fun x => x > 0)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- Property Theorems (moved here as proof_aux)
-- Note: kept as in the original file, but adapted to call get_positive with a precondition proof.

-- !benchmark @start proof_aux
def empty_list_prop : Prop := get_positive ([] : List Int) (by simp) = []

@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

def positive_only_prop (l : List Int) : Prop :=
  ∀ x ∈ get_positive (l) (by simp), x > 0

@[simp] theorem positive_only_thm (l : List Int) : positive_only_prop l := by
  sorry

def subset_prop (l : List Int) : Prop :=
  ∀ x ∈ get_positive (l) (by simp), x ∈ l

@[simp] theorem subset_thm (l : List Int) : subset_prop l := by
  sorry

def order_preservation_prop (l : List Int) : Prop :=
  ∀ x y,
    x ∈ get_positive (l) (by simp) →
      y ∈ get_positive (l) (by simp) →
        l.idxOf x < l.idxOf y →
          (get_positive (l) (by simp)).idxOf x < (get_positive (l) (by simp)).idxOf y

@[simp] theorem order_preservation_thm (l : List Int) : order_preservation_prop l := by
  sorry

def completeness_prop (l : List Int) : Prop :=
  ∀ x ∈ l, x > 0 → x ∈ get_positive (l) (by simp)

@[simp] theorem completeness_thm (l : List Int) : completeness_prop l := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def get_positive_postcond (l : List Int) (result : List Int) (h_precond : get_positive_precond (l)) : Prop :=
  -- !benchmark @start postcond
  empty_list_prop ∧
    positive_only_prop l ∧
      subset_prop l ∧
        order_preservation_prop l ∧
          completeness_prop l
  -- !benchmark @end postcond

theorem get_positive_spec_satisfied (l : List Int) (h_precond : get_positive_precond (l)) :
    get_positive_postcond (l) (get_positive (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof