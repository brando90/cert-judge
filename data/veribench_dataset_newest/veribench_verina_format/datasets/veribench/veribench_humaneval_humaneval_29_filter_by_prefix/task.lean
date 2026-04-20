-- !benchmark @start import type=solution
import Mathlib
namespace StringFilter
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def filter_by_prefix_precond (xs : List String) (p : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def filter_by_prefix (xs : List String) (p : String) (h_precond : filter_by_prefix_precond (xs) (p)) : List String :=
  -- !benchmark @start code
  List.filter (fun s => String.startsWith s p) xs
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Empty list returns empty list. -/
def empty_list_prop (p : String) : Prop := filter_by_prefix [] p (by simp) = []

/-- **Empty list theorem**: Empty list returns empty list. -/
@[simp] theorem empty_list_thm (p : String) : empty_list_prop p := by
  sorry

/-- **Empty prefix property**: Empty prefix matches all strings. -/
def empty_prefix_prop (xs : List String) : Prop := filter_by_prefix xs "" (by simp) = xs

/-- **Empty prefix theorem**: Empty prefix matches all strings. -/
@[simp] theorem empty_prefix_thm (xs : List String) : empty_prefix_prop xs := by
  sorry

/-- **Subset property**: Result is a subset of input. -/
def subset_prop (xs : List String) (p : String) : Prop :=
  ∀ s ∈ filter_by_prefix xs p (by simp), s ∈ xs

/-- **Subset theorem**: Result is a subset of input. -/
@[simp] theorem subset_thm (xs : List String) (p : String) : subset_prop xs p := by
  sorry

/-- **Prefix property**: All results start with the prefix. -/
def prefix_prop (xs : List String) (p : String) : Prop :=
  ∀ s ∈ filter_by_prefix xs p (by simp), String.startsWith s p

/-- **Prefix theorem**: All results start with the prefix. -/
@[simp] theorem prefix_thm (xs : List String) (p : String) : prefix_prop xs p := by
  sorry

/-- **Order preservation property**: Order of matching elements is preserved. -/
def order_preservation_prop (xs : List String) (p : String) : Prop :=
  ∀ x y,
    x ∈ filter_by_prefix xs p (by simp) →
      y ∈ filter_by_prefix xs p (by simp) →
        xs.idxOf x < xs.idxOf y →
          (filter_by_prefix xs p (by simp)).idxOf x < (filter_by_prefix xs p (by simp)).idxOf y

/-- **Order preservation theorem**: Order of matching elements is preserved. -/
@[simp] theorem order_preservation_thm (xs : List String) (p : String) : order_preservation_prop xs p := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def filter_by_prefix_postcond (xs : List String) (p : String) (result : List String)
    (h_precond : filter_by_prefix_precond (xs) (p)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop p) ∧
    (empty_prefix_prop xs) ∧
    (subset_prop xs p) ∧
    (prefix_prop xs p) ∧
    (order_preservation_prop xs p)
  -- !benchmark @end postcond

theorem filter_by_prefix_spec_satisfied (xs : List String) (p : String)
    (h_precond : filter_by_prefix_precond (xs) (p)) :
    filter_by_prefix_postcond (xs) (p) (filter_by_prefix (xs) (p) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof

end StringFilter