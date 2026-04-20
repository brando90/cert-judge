-- !benchmark @start import type=solution
import Mathlib
namespace Intersperse

open List
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def intersperse_precond (numbers : List Int) (delim : Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def intersperse (numbers : List Int) (delim : Int) (h_precond : intersperse_precond (numbers) (delim)) : List Int :=
  -- !benchmark @start code
  match numbers with
  | [] => []
  | (x :: xs) =>
    go x xs
  where
    go (curr : Int) (rest : List Int) : List Int :=
      match rest with
      | [] => [curr]
      | y :: ys =>
        curr :: delim :: go y ys
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty list property**: Interspersing empty list gives empty list. -/
def empty_list_prop (delim : Int) : Prop := intersperse [] delim (by simp) = []

/-- **Empty list theorem**: Interspersing empty list gives empty list. -/
@[simp] theorem empty_list_thm (delim : Int) : empty_list_prop delim := by
  sorry

/-- **Single element property**: Interspersing single element list gives the same list. -/
def single_element_prop (x delim : Int) : Prop := intersperse [x] delim (by simp) = [x]

/-- **Single element theorem**: Interspersing single element list gives the same list. -/
@[simp] theorem single_element_thm (x delim : Int) : single_element_prop x delim := by
  sorry

/-- **Length property**: Length of result is 2*n-1 for non-empty list of length n. -/
def length_prop (numbers : List Int) (delim : Int) : Prop :=
  numbers.length > 0 → (intersperse numbers delim (by simp)).length = 2 * numbers.length - 1

/-- **Length theorem**: Length of result is 2*n-1 for non-empty list of length n. -/
@[simp] theorem length_thm (numbers : List Int) (delim : Int) : length_prop numbers delim := by
  sorry

/-- **Delimiter placement property**: Delimiters appear at odd indices. -/
def delimiter_placement_prop (numbers : List Int) (delim : Int) : Prop :=
  ∀ i,
    i % 2 = 1 →
      i < (intersperse numbers delim (by simp)).length →
        (intersperse numbers delim (by simp))[i]! = delim

/-- **Delimiter placement theorem**: Delimiters appear at odd indices. -/
@[simp] theorem delimiter_placement_thm (numbers : List Int) (delim : Int) : delimiter_placement_prop numbers delim := by
  sorry

/-- **Original elements property**: Original elements appear at even indices. -/
def original_elements_prop (numbers : List Int) (delim : Int) : Prop :=
  numbers.length > 0 →
    ∀ i,
      i % 2 = 0 →
        i < (intersperse numbers delim (by simp)).length →
          (intersperse numbers delim (by simp))[i]! = numbers[i / 2]!

/-- **Original elements theorem**: Original elements appear at even indices. -/
@[simp] theorem original_elements_thm (numbers : List Int) (delim : Int) : original_elements_prop numbers delim := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def intersperse_postcond (numbers : List Int) (delim : Int) (result : List Int)
    (h_precond : intersperse_precond (numbers) (delim)) :=
  -- !benchmark @start postcond
  (empty_list_prop delim) ∧
    (∀ x, single_element_prop x delim) ∧
    (length_prop numbers delim) ∧
    (delimiter_placement_prop numbers delim) ∧
    (original_elements_prop numbers delim)
  -- !benchmark @end postcond

theorem intersperse_spec_satisfied (numbers : List Int) (delim : Int)
    (h_precond : intersperse_precond (numbers) (delim)) :
    intersperse_postcond (numbers) (delim) (intersperse (numbers) (delim) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof