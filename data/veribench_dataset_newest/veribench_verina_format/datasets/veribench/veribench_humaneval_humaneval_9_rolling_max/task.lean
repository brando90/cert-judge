-- !benchmark @start import type=solution
import Mathlib
namespace RollingMax
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def rollingMax_precond (numbers : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def rollingMax (numbers : List Int) (h_precond : rollingMax_precond (numbers)) : List Int :=
  -- !benchmark @start code
  let rec aux : List Int → Int → List Int → List Int
    | [], _, acc => acc.reverse
    | x::xs, currMax, acc =>
        let newMax := max currMax x
        aux xs newMax (newMax::acc)
  match numbers with
  | [] => []
  | x::xs => aux xs x [x]
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Rolling max of empty list is empty list. -/
def empty_list_prop : Prop := rollingMax ([]) (by simp) = []

/-- **Empty list theorem**: Rolling max of empty list is empty list. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (numbers : List Int) : Prop :=
  (rollingMax (numbers) (by simp)).length = numbers.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (numbers : List Int) : length_preservation_prop numbers := by
  sorry

/-- **Monotonicity property**: Each element is ≥ the previous rolling max. -/
def monotonicity_prop (numbers : List Int) : Prop :=
  ∀ i j, i ≤ j → j < (rollingMax (numbers) (by simp)).length →
    (rollingMax (numbers) (by simp))[i]! ≤ (rollingMax (numbers) (by simp))[j]!

/-- **Monotonicity theorem**: Each element is ≥ the previous rolling max. -/
@[simp] theorem monotonicity_thm (numbers : List Int) : monotonicity_prop numbers := by
  sorry

/-- **First element property**: First element equals first input element. -/
def first_element_prop (numbers : List Int) : Prop :=
  numbers.length > 0 → (rollingMax (numbers) (by simp))[0]! = numbers[0]!

/-- **First element theorem**: First element equals first input element. -/
@[simp] theorem first_element_thm (numbers : List Int) : first_element_prop numbers := by
  sorry

/-- **Upper bound property**: Each rolling max is ≥ corresponding input element. -/
def upper_bound_prop (numbers : List Int) : Prop :=
  ∀ i, i < numbers.length → numbers[i]! ≤ (rollingMax (numbers) (by simp))[i]!

/-- **Upper bound theorem**: Each rolling max is ≥ corresponding input element. -/
@[simp] theorem upper_bound_thm (numbers : List Int) : upper_bound_prop numbers := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def rollingMax_postcond (numbers : List Int) (result : List Int)
    (h_precond : rollingMax_precond (numbers)) :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
  (length_preservation_prop numbers) ∧
  (monotonicity_prop numbers) ∧
  (first_element_prop numbers) ∧
  (upper_bound_prop numbers)
  -- !benchmark @end postcond

theorem rollingMax_spec_satisfied (numbers : List Int) (h_precond : rollingMax_precond (numbers)) :
    rollingMax_postcond (numbers) (rollingMax (numbers) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof