-- !benchmark @start import type=solution
import Mathlib
namespace RemoveDuplicates
-- !benchmark @end import

-- !benchmark @start solution_aux
/--
Helper function to count occurrences of an element in a list.
Returns the number of times x appears in xs.
-/
def countOccurrences (xs : List Int) (x : Int) : Nat :=
  xs.foldl (fun acc y => if y = x then acc + 1 else acc) 0
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def removeDuplicates_precond (numbers : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def removeDuplicates (numbers : List Int) (h_precond : removeDuplicates_precond (numbers)) : List Int :=
  -- !benchmark @start code
  numbers.filter (fun x => countOccurrences numbers x = 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Empty list returns empty list. -/
def empty_list_prop : Prop := removeDuplicates [] (by simp) = []

/-- **Empty list theorem**: Empty list returns empty list. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **No duplicates property**: Result contains no duplicates. -/
def no_duplicates_prop (numbers : List Int) : Prop :=
  ∀ x ∈ removeDuplicates numbers (by simp), countOccurrences (removeDuplicates numbers (by simp)) x = 1

/-- **No duplicates theorem**: Result contains no duplicates. -/
@[simp] theorem no_duplicates_thm (numbers : List Int) : no_duplicates_prop numbers := by
  sorry

/-- **Order preservation property**: Order of remaining elements is preserved. -/
def order_preservation_prop (numbers : List Int) : Prop :=
  ∀ x y,
    x ∈ removeDuplicates numbers (by simp) →
      y ∈ removeDuplicates numbers (by simp) →
        numbers.idxOf x < numbers.idxOf y →
          (removeDuplicates numbers (by simp)).idxOf x < (removeDuplicates numbers (by simp)).idxOf y

/-- **Order preservation theorem**: Order of remaining elements is preserved. -/
@[simp] theorem order_preservation_thm (numbers : List Int) : order_preservation_prop numbers := by
  sorry

/-- **Single occurrence property**: Only elements with single occurrence remain. -/
def single_occurrence_prop (numbers : List Int) : Prop :=
  ∀ x, x ∈ removeDuplicates numbers (by simp) ↔ countOccurrences numbers x = 1

/-- **Single occurrence theorem**: Only elements with single occurrence remain. -/
@[simp] theorem single_occurrence_thm (numbers : List Int) : single_occurrence_prop numbers := by
  sorry

/-- **Subset property**: Result is a subset of input. -/
def subset_prop (numbers : List Int) : Prop :=
  ∀ x ∈ removeDuplicates numbers (by simp), x ∈ numbers

/-- **Subset theorem**: Result is a subset of input. -/
@[simp] theorem subset_thm (numbers : List Int) : subset_prop numbers := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def removeDuplicates_postcond (numbers : List Int) (result : List Int)
    (h_precond : removeDuplicates_precond (numbers)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
    (no_duplicates_prop numbers) ∧
      (order_preservation_prop numbers) ∧
        (single_occurrence_prop numbers) ∧
          (subset_prop numbers)
  -- !benchmark @end postcond

theorem removeDuplicates_spec_satisfied (numbers : List Int) (h_precond : removeDuplicates_precond (numbers)) :
    removeDuplicates_postcond (numbers) (removeDuplicates (numbers) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof