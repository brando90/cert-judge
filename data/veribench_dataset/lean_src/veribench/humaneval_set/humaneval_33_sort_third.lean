/-!
# VeriBench – Sort Third

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

## Sort Third

Sorts elements at indices divisible by three in a list while preserving other elements.-/

namespace SortThird

/-- Helper function to sort a list using insertion sort -/
def insertionSort (l : List Int) : List Int :=
  let rec insert (x : Int) (l : List Int) : List Int :=
    match l with
    | [] => [x]
    | h::t => if x ≤ h then x::h::t else h::(insert x t)

  let rec sort (l : List Int) : List Int :=
    match l with
    | [] => []
    | h::t => insert h (sort t)

  sort l

/--
**Implementation of `sort_third`.**

`sort_third l` sorts elements at indices divisible by three in a list while preserving other elements.

Given a list l, returns a list l' where:
1. Elements at indices not divisible by 3 remain unchanged
2. Elements at indices divisible by 3 (0, 3, 6, ...) are sorted in ascending order

## Examples

#eval sort_third [1, 2, 3]  -- expected: [1, 2, 3]
#eval sort_third [5, 6, 3, 4, 8, 9, 2]  -- expected: [2, 6, 3, 4, 8, 9, 5]
-/
def sort_third (l : List Int) : List Int :=
  let indices := List.range l.length
  let third_indices := indices.filter (fun i => i % 3 = 0)
  let third_values := third_indices.map (fun i => l[i]!)
  let sorted_third := insertionSort third_values
  let rec update_list (curr : List Int) (pos : List Nat) (vals : List Int) : List Int :=
    match pos, vals with
    | [], _ => curr
    | _, [] => curr
    | p::ps, v::vs =>
      let new_curr := curr.set p v
      update_list new_curr ps vs

  update_list l third_indices sorted_third

/-!
# Tests
-/

/-- expected: [1, 2, 3] -/
example : sort_third [1, 2, 3] = [1, 2, 3] := by native_decide
#eval sort_third [1, 2, 3] -- expected: [1, 2, 3]

/-- expected: [2, 6, 3, 4, 8, 9, 5] -/
example : sort_third [5, 6, 3, 4, 8, 9, 2] = [2, 6, 3, 4, 8, 9, 5] := by native_decide
#eval sort_third [5, 6, 3, 4, 8, 9, 2] -- expected: [2, 6, 3, 4, 8, 9, 5]

/-!
# Tests: Edge Cases
-/

/-- expected: [] -/
example : sort_third [] = [] := by native_decide
#eval sort_third [] -- expected: []

/-- expected: [1] -/
example : sort_third [1] = [1] := by native_decide
#eval sort_third [1] -- expected: [1]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: elements at third indices are sorted -/
example : sort_third [3, 2, 1, 6, 5, 4] = [3, 2, 1, 6, 5, 4] := by native_decide
#eval sort_third [3, 2, 1, 6, 5, 4] -- expected: [3, 2, 1, 6, 5, 4]

/-- positive test: larger list -/
example : sort_third [9, 8, 7, 6, 5, 4, 3, 2, 1] = [3, 8, 7, 6, 5, 4, 9, 2, 1] := by native_decide
#eval sort_third [9, 8, 7, 6, 5, 4, 3, 2, 1] -- expected: [3, 8, 7, 6, 5, 4, 9, 2, 1]

/-- negative test: non-third indices change -/
example : ¬ (sort_third [5, 6, 3, 4, 8, 9, 2] = [5, 6, 3, 4, 8, 9, 2]) := by native_decide

/-- negative test: different input gives different result -/
example : ¬ (sort_third [1, 2, 3] = sort_third [3, 2, 1]) := by native_decide

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any list is valid input. -/
def Pre (_ : List Int) : Prop := True

/-!
# Property Theorems
-/

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (l : List Int) : Prop := (sort_third l).length = l.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (l : List Int) : length_preservation_prop l := sorry

/-- **Non-third preservation property**: Elements at non-third indices remain unchanged. -/
def non_third_preservation_prop (l : List Int) : Prop :=
  ∀ i, i < l.length → i % 3 ≠ 0 → (sort_third l)[i]! = l[i]!

/-- **Non-third preservation theorem**: Elements at non-third indices remain unchanged. -/
@[simp] theorem non_third_preservation_thm (l : List Int) : non_third_preservation_prop l := sorry

/-- **Third sorting property**: Elements at third indices are sorted in ascending order. -/
def third_sorting_prop (l : List Int) : Prop :=
  ∀ i j, i < l.length → j < l.length → i % 3 = 0 → j % 3 = 0 → i < j → (sort_third l)[i]! ≤ (sort_third l)[j]!

/-- **Third sorting theorem**: Elements at third indices are sorted in ascending order. -/
@[simp] theorem third_sorting_thm (l : List Int) : third_sorting_prop l := sorry

/-- **Idempotent property**: sort_third is idempotent. -/
def idempotent_prop (l : List Int) : Prop := sort_third (sort_third l) = sort_third l

/-- **Idempotent theorem**: sort_third is idempotent. -/
@[simp] theorem idempotent_thm (l : List Int) : idempotent_prop l := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for sort_third. -/
def Post_prop (l : List Int) : Prop :=
  (length_preservation_prop l) ∧                         -- length preservation property
  (non_third_preservation_prop l) ∧                      -- non-third preservation property
  (third_sorting_prop l) ∧                               -- third sorting property
  (idempotent_prop l)                                    -- idempotent property

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (l : List Int) (hPre : Pre l) : Post_prop l := sorry

/-!
# Imperative Implementation
-/

/--
`sort_thirdImp l` computes the same result using imperative style with mutable arrays.
-/
def sort_thirdImp (l : List Int) : List Int :=
  Id.run do
    let mut result := l.toArray
    let mut third_values : List Int := []
    let mut third_indices : List Nat := []

    -- Collect third indices and their values
    for i in [:l.length] do
      if i % 3 = 0 then
        third_values := third_values ++ [l[i]!]
        third_indices := third_indices ++ [i]

    -- Sort third values
    third_values := insertionSort third_values

    -- Update the result array using runtime bounds checking
    for i in [:third_indices.length] do
      let idx := third_indices[i]!
      let val := third_values[i]!
      -- Use runtime bounds checking with ! notation
      if idx < result.size then
        result := result.set! idx val

    return result.toList

/-!
# Imperative Tests
-/

/-- expected: [1, 2, 3] -/
example : sort_thirdImp [1, 2, 3] = [1, 2, 3] := by native_decide
#eval sort_thirdImp [1, 2, 3] -- expected: [1, 2, 3]

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: [2, 6, 3, 4, 8, 9, 5] -/
example : sort_thirdImp [5, 6, 3, 4, 8, 9, 2] = [2, 6, 3, 4, 8, 9, 5] := by native_decide
#eval sort_thirdImp [5, 6, 3, 4, 8, 9, 2] -- expected: [2, 6, 3, 4, 8, 9, 5]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: finds correct result -/
example : sort_thirdImp [9, 8, 7, 6, 5, 4, 3, 2, 1] = [3, 8, 7, 6, 5, 4, 9, 2, 1] := by native_decide
#eval sort_thirdImp [9, 8, 7, 6, 5, 4, 3, 2, 1] -- expected: [3, 8, 7, 6, 5, 4, 9, 2, 1]

/-- negative test: not exactly the same as unsorted -/
example : ¬ (sort_thirdImp [5, 6, 3, 4, 8, 9, 2] = [5, 6, 3, 4, 8, 9, 2]) := by native_decide

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem sort_third_equivalence_thm (l : List Int) :
  sort_third l = sort_thirdImp l := sorry

end SortThird
