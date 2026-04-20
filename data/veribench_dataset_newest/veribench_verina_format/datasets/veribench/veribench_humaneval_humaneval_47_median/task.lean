-- !benchmark @start import type=solution
import Mathlib
namespace Median
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def median_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def median (l : List Int) (h_precond : median_precond (l)) : Float :=
  -- !benchmark @start code
  if l.isEmpty then
    0.0
  else
    let sorted := l.toArray.qsort (·<=·) |>.toList
    let n := sorted.length
    if n % 2 == 1 then
      Float.ofInt sorted[n / 2]!
    else
      let mid1 := Float.ofInt sorted[n / 2 - 1]!
      let mid2 := Float.ofInt sorted[n / 2]!
      (mid1 + mid2) / 2.0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux

/-- **Empty list property**: The median of an empty list is 0.0. -/
def empty_list_prop : Prop := median ([]) (by simp) = 0.0

/-- **Empty list theorem**: The median of an empty list is 0.0. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Singleton property**: The median of a single-element list is that element. -/
def singleton_prop (x : Int) : Prop := median ([x]) (by simp) = Float.ofInt x

/-- **Singleton theorem**: The median of a single-element list is that element. -/
@[simp] theorem singleton_thm (x : Int) : singleton_prop x := by
  sorry

/-- **Order independence property**: The median is independent of the order of elements. -/
def order_independent_prop (l : List Int) : Prop :=
  median (l) (by simp) = median (l.reverse) (by simp)

/-- **Order independence theorem**: The median is independent of the order of elements. -/
@[simp] theorem order_independent_thm (l : List Int) : order_independent_prop l := by
  sorry

/-- **Range property**: The median is always between the min and max values for non-empty lists. -/
def range_prop (l : List Int) : Prop :=
  l ≠ [] →
    let sorted := l.toArray.qsort (·<=·) |>.toList
    Float.ofInt sorted[0]! ≤ median (l) (by simp) ∧
      median (l) (by simp) ≤ Float.ofInt sorted[sorted.length - 1]!

/-- **Range theorem**: The median is always between the min and max values for non-empty lists. -/
@[simp] theorem range_thm (l : List Int) : range_prop l := by
  sorry

-- !benchmark @end proof_aux

@[reducible, simp]
def median_postcond (l : List Int) (result : Float) (h_precond : median_precond (l)) :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
    (∀ x, singleton_prop x) ∧
    (order_independent_prop l) ∧
    (range_prop l)
  -- !benchmark @end postcond

theorem median_spec_satisfied (l : List Int) (h_precond : median_precond (l)) :
    median_postcond (l) (median (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof