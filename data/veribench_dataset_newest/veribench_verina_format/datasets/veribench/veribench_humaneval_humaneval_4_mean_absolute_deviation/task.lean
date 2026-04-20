-- !benchmark @start import type=solution
import Mathlib
namespace MeanAbsoluteDeviation

open List
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def meanAbsoluteDeviation_precond (numbers : List Float) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def meanAbsoluteDeviation (numbers : List Float) (h_precond : meanAbsoluteDeviation_precond (numbers)) : Float :=
  -- !benchmark @start code
  let n := numbers.length
  if n == 0 then
    0.0
  else
    let meanVal := (numbers.foldl (· + ·) 0.0) / n.toFloat
    let sumDev := numbers.foldl (fun acc x => acc + Float.abs (x - meanVal)) 0.0
    sumDev / n.toFloat
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Empty list returns zero. -/
def empty_list_prop : Prop := meanAbsoluteDeviation ([]) (by simp) = 0.0

/-- **Empty list theorem**: Empty list returns zero. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Non-negative property**: Result is always non-negative. -/
def non_negative_prop (numbers : List Float) : Prop :=
  meanAbsoluteDeviation (numbers) (by simp) ≥ 0.0

/-- **Non-negative theorem**: Result is always non-negative. -/
@[simp] theorem non_negative_thm (numbers : List Float) : non_negative_prop numbers := by
  sorry

/-- **Constant list property**: Constant lists have zero deviation. -/
def constant_list_prop (numbers : List Float) : Prop :=
  (∀ a b, a ∈ numbers → b ∈ numbers → a = b) → meanAbsoluteDeviation (numbers) (by simp) = 0.0

/-- **Constant list theorem**: Constant lists have zero deviation. -/
@[simp] theorem constant_list_thm (numbers : List Float) : constant_list_prop numbers := by
  sorry

/-- **Single element property**: Single element has zero deviation. -/
def single_element_prop (x : Float) : Prop := meanAbsoluteDeviation ([x]) (by simp) = 0.0

/-- **Single element theorem**: Single element has zero deviation. -/
@[simp] theorem single_element_thm (x : Float) : single_element_prop x := by
  sorry

/-- **Shift invariance property**: Adding constant to all elements preserves MAD. -/
def shift_invariant_prop (numbers : List Float) (c : Float) : Prop :=
  meanAbsoluteDeviation (numbers.map (· + c)) (by simp) = meanAbsoluteDeviation (numbers) (by simp)

/-- **Shift invariance theorem**: Adding constant to all elements preserves MAD. -/
@[simp] theorem shift_invariant_thm (numbers : List Float) (c : Float) : shift_invariant_prop numbers c := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def meanAbsoluteDeviation_postcond (numbers : List Float) (result : Float)
    (h_precond : meanAbsoluteDeviation_precond (numbers)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
  (non_negative_prop numbers) ∧
  (constant_list_prop numbers) ∧
  (∀ x, single_element_prop x) ∧
  (∀ c, shift_invariant_prop numbers c)
  -- !benchmark @end postcond

theorem meanAbsoluteDeviation_spec_satisfied (numbers : List Float)
    (h_precond : meanAbsoluteDeviation_precond (numbers)) :
    meanAbsoluteDeviation_postcond (numbers) (meanAbsoluteDeviation (numbers) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof