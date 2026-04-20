-- !benchmark @start import type=solution
import Mathlib
namespace MaxElement
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def max_element_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def max_element (l : List Int) (h_precond : max_element_precond (l)) : Int :=
  -- !benchmark @start code
  match l with
  | [] => 0
  | x :: xs => xs.foldl (fun m e => if e > m then e else m) x
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Empty list returns 0. -/
def empty_list_prop : Prop := max_element ([] : List Int) (by simp) = 0

/-- **Empty list theorem**: Empty list returns 0. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Single element property**: Single element returns that element. -/
def single_element_prop (x : Int) : Prop := max_element [x] (by simp) = x

/-- **Single element theorem**: Single element returns that element. -/
@[simp] theorem single_element_thm (x : Int) : single_element_prop x := by
  sorry

/-- **Maximum property**: Result is the maximum element when non-empty. -/
def maximum_prop (l : List Int) : Prop :=
  l ≠ [] → (max_element l (by simp) ∈ l ∧ ∀ y ∈ l, y ≤ max_element l (by simp))

/-- **Maximum theorem**: Result is the maximum element when non-empty. -/
@[simp] theorem maximum_thm (l : List Int) : maximum_prop l := by
  sorry

/-- **Membership property**: Result element is in the original list (when non-empty). -/
def membership_prop (l : List Int) : Prop :=
  l ≠ [] → max_element l (by simp) ∈ l

/-- **Membership theorem**: Result element is in the original list (when non-empty). -/
@[simp] theorem membership_thm (l : List Int) : membership_prop l := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def max_element_postcond (l : List Int) (result : Int) (h_precond : max_element_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
    (∀ x, single_element_prop x) ∧
    (maximum_prop l) ∧
    (membership_prop l)
  -- !benchmark @end postcond

theorem max_element_spec_satisfied (l : List Int) (h_precond : max_element_precond (l)) :
    max_element_postcond (l) (max_element (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof