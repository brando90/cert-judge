-- !benchmark @start import type=solution
import Mathlib
namespace SortEven
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def sortEven_precond (l : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

/-- Extracts elements at even indices (0, 2, 4, ...) from a list. -/
def getEvens : List Int → List Int
  | [] => []
  | [x] => [x]
  | x::_::xs => x :: getEvens xs

/-- Extracts elements at odd indices (1, 3, 5, ...) from a list. -/
def getOdds : List Int → List Int
  | [] => []
  | [_] => []
  | _::x::xs => x :: getOdds xs

/-- Interleaves two lists, taking elements alternately from each list. -/
def zipLists : List Int → List Int → List Int
  | [], _ => []
  | e::_, [] => [e]
  | e::es, o::os => e :: o :: zipLists es os

-- !benchmark @end code_aux

def sortEven (l : List Int) (h_precond : sortEven_precond (l)) : List Int :=
  -- !benchmark @start code
  let evens := (getEvens l).toArray.qsort (· ≤ ·) |>.toList
  let odds := getOdds l
  zipLists evens odds
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (l : List Int) : Prop := (sortEven l (by simp)).length = l.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (l : List Int) : length_preservation_prop l := by
  sorry

/-- **Odd preservation property**: Elements at odd indices remain unchanged. -/
def odd_preservation_prop (l : List Int) : Prop :=
  ∀ i, i % 2 = 1 → i < l.length → (sortEven l (by simp))[i]? = l[i]?

/-- **Odd preservation theorem**: Elements at odd indices remain unchanged. -/
@[simp] theorem odd_preservation_thm (l : List Int) : odd_preservation_prop l := by
  sorry

/-- **Even sorting property**: Elements at even indices are sorted in ascending order. -/
def even_sorting_prop (l : List Int) : Prop :=
  ∀ i j, i % 2 = 0 → j % 2 = 0 → i < j → i < l.length → j < l.length →
    ((sortEven l (by simp))[i]?).isSome → ((sortEven l (by simp))[j]?).isSome →
      ((sortEven l (by simp))[i]!) ≤ ((sortEven l (by simp))[j]!)

/-- **Even sorting theorem**: Elements at even indices are sorted in ascending order. -/
@[simp] theorem even_sorting_thm (l : List Int) : even_sorting_prop l := by
  sorry

/-- **Idempotent property**: The function is idempotent. -/
def idempotent_prop (l : List Int) : Prop := sortEven (sortEven l (by simp)) (by simp) = sortEven l (by simp)

/-- **Idempotent theorem**: The function is idempotent. -/
@[simp] theorem idempotent_thm (l : List Int) : idempotent_prop l := by
  sorry

-- !benchmark @end proof_aux

@[reducible, simp]
def sortEven_postcond (l : List Int) (result : List Int) (h_precond : sortEven_precond (l)) :=
  -- !benchmark @start postcond
  (result.length = l.length) ∧
  (∀ i, i % 2 = 1 → i < l.length → result[i]? = l[i]?) ∧
  (∀ i j, i % 2 = 0 → j % 2 = 0 → i < j → i < l.length → j < l.length →
      (result[i]?).isSome → (result[j]?).isSome → (result[i]!) ≤ (result[j]!)) ∧
  (sortEven result (by simp) = result)
  -- !benchmark @end postcond

theorem sortEven_spec_satisfied (l : List Int) (h_precond : sortEven_precond (l)) :
    sortEven_postcond (l) (sortEven (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof