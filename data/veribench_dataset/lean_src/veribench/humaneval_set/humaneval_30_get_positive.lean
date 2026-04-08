/-!

# VeriBench – Get Positive

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## Get Positive

Implements `get_positive`, which filters a list to return only positive integers.-/

namespace PositiveFilter

/--
**Implementation of `get_positive`.**

Takes a list of integers and returns a new list containing only the positive
numbers (greater than 0). If the input list is empty, returns an empty list.
The order of elements is preserved.

## Examples

#eval get_positive [-1, 2, -4, 5, 6] -- expected: [2, 5, 6]
#eval get_positive [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] -- expected: [5, 3, 2, 3, 9, 123, 1]
-/
def get_positive (l : List Int) : List Int :=
  l.filter (λ x => x > 0)

/-!
# Tests
-/

/-- expected: [2, 5, 6] -/
example : get_positive [-1, 2, -4, 5, 6] = [2, 5, 6] := by sorry
#eval get_positive [-1, 2, -4, 5, 6]

/-- expected: [5, 3, 2, 3, 9, 123, 1] -/
example : get_positive [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] = [5, 3, 2, 3, 9, 123, 1] := by sorry
#eval get_positive [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10]

/-!
# Tests: Edge Cases
-/

/-- expected: [4, 5, 6] -/
example : get_positive [-1, -2, 4, 5, 6] = [4, 5, 6] := by sorry
#eval get_positive [-1, -2, 4, 5, 6]

/-- expected: [] -/
example : get_positive [-1, -2] = [] := by sorry
#eval get_positive [-1, -2]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: empty list -/
example : get_positive [] = [] := by sorry
#eval get_positive [] -- expected: []

/-- positive: mixed with zero -/
example : get_positive [0, 1, -1, 2, -2] = [1, 2] := by sorry
#eval get_positive [0, 1, -1, 2, -2] -- expected: [1, 2]

/-- negative: zero is not positive -/
example : ¬ (get_positive [0, -1] = [0]) := by sorry
#eval (decide (get_positive [0, -1] = [0])) -- expected: false

/-- negative: negative numbers are filtered out -/
example : ¬ (get_positive [-1, 2, -3] = [-1, 2, -3]) := by sorry
#eval (decide (get_positive [-1, 2, -3] = [-1, 2, -3])) -- expected: false

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any list of integers is valid input. -/
def Pre (l : List Int) : Prop := True

/-!
# Property Theorems
-/

/-- **Empty list property**: Empty list returns empty list. -/
def empty_list_prop : Prop := get_positive [] = []

/-- **Empty list theorem**: Empty list returns empty list. -/
@[simp] theorem empty_list_thm : empty_list_prop := sorry

/-- **Positive only property**: All elements in result are positive. -/
def positive_only_prop (l : List Int) : Prop :=
  ∀ x ∈ get_positive l, x > 0

/-- **Positive only theorem**: All elements in result are positive. -/
@[simp] theorem positive_only_thm (l : List Int) : positive_only_prop l := sorry

/-- **Subset property**: Result is a subset of input. -/
def subset_prop (l : List Int) : Prop :=
  ∀ x ∈ get_positive l, x ∈ l

/-- **Subset theorem**: Result is a subset of input. -/
@[simp] theorem subset_thm (l : List Int) : subset_prop l := sorry

/-- **Order preservation property**: Order of positive elements is preserved. -/
def order_preservation_prop (l : List Int) : Prop :=
  ∀ x y, x ∈ get_positive l → y ∈ get_positive l →
    l.idxOf x < l.idxOf y →
    (get_positive l).idxOf x < (get_positive l).idxOf y

/-- **Order preservation theorem**: Order of positive elements is preserved. -/
@[simp] theorem order_preservation_thm (l : List Int) : order_preservation_prop l := sorry

/-- **Completeness property**: All positive elements from input are included. -/
def completeness_prop (l : List Int) : Prop :=
  ∀ x ∈ l, x > 0 → x ∈ get_positive l

/-- **Completeness theorem**: All positive elements from input are included. -/
@[simp] theorem completeness_thm (l : List Int) : completeness_prop l := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for get_positive. -/
def Post_prop (l : List Int) : Prop :=
  (empty_list_prop) ∧                                    -- empty_list_prop
  (positive_only_prop l) ∧                               -- positive_only_prop
  (subset_prop l) ∧                                      -- subset_prop
  (order_preservation_prop l) ∧                          -- order_preservation_prop
  (completeness_prop l)                                  -- completeness_prop

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (l : List Int) (hPre : Pre l) : Post_prop l := sorry

/-!
# Imperative Implementation
-/

/--
`get_positiveImp l` computes the same result using imperative style with explicit loops.
-/
def get_positiveImp (l : List Int) : List Int :=
  Id.run do
    let mut result : List Int := []
    for x in l do
      if x > 0 then
        result := result ++ [x]
    return result

/-!
# Imperative Tests
-/

/-- expected: [2, 5, 6] -/
example : get_positiveImp [-1, 2, -4, 5, 6] = [2, 5, 6] := by sorry
#eval get_positiveImp [-1, 2, -4, 5, 6]

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: [] -/
example : get_positiveImp [] = [] := by sorry
#eval get_positiveImp []

/-- expected: [1, 2] -/
example : get_positiveImp [0, 1, -1, 2, -2] = [1, 2] := by sorry
#eval get_positiveImp [0, 1, -1, 2, -2]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: all positive numbers -/
example : get_positiveImp [1, 2, 3, 4] = [1, 2, 3, 4] := by sorry
#eval get_positiveImp [1, 2, 3, 4] -- expected: [1, 2, 3, 4]

/-- negative: doesn't include zero or negative -/
example : ¬ (get_positiveImp [-1, 0, 1] = [-1, 0, 1]) := by sorry
#eval (decide (get_positiveImp [-1, 0, 1] = [-1, 0, 1])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem get_positive_equivalence_thm (l : List Int) :
  get_positive l = get_positiveImp l := sorry

end PositiveFilter
