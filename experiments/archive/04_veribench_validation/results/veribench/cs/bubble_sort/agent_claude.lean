import Mathlib.Data.List.Perm

/-- Bubble sort for a list of integers.

Edge cases:
- Empty list returns empty list.
-/

/-- Check if the input is valid (a list of integers). -/
def pre (arr : List Int) : Prop :=
  true  -- In Lean, type checking ensures arr is a List Int

/-- Check if the output is a sorted version of the input. -/
def post (arr : List Int) (res : List Int) : Prop :=
  res.Sorted (· ≤ ·) ∧ arr.Perm res

/-- Implementation of bubble sort for a list of integers. -/
def bubble_sort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let rec bubble_pass (xs : List Int) (swapped : Bool) : List Int × Bool :=
      match xs with
      | [] => ([], swapped)
      | [x] => ([x], swapped)
      | x :: y :: rest =>
        let (tail, swapped') := bubble_pass (y :: rest) swapped
        if x > y then
          (y :: x :: tail, true)
        else
          (x :: tail, swapped')

    let rec sort_until_no_swap (xs : List Int) : List Int :=
      let (xs', swapped) := bubble_pass xs false
      if swapped then
        sort_until_no_swap xs'
      else
        xs'

    sort_until_no_swap arr

/-- Tests for the bubble sort function. -/
def tests : IO Unit := do
  -- Basic functionality tests
  assert! (bubble_sort [3, 1, 2] == [1, 2, 3])
  assert! (bubble_sort [1, 2, 3] == [1, 2, 3])
  assert! (bubble_sort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (bubble_sort ([] : List Int) == [])
  assert! (bubble_sort [1] == [1])
  
  -- Larger arrays
  assert! (bubble_sort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (bubble_sort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (bubble_sort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (bubble_sort [2, 1] == [1, 2])
  assert! (bubble_sort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (bubble_sort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (bubble_sort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (bubble_sort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (bubble_sort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (bubble_sort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  IO.println "All tests passed."

/-- Theorem stating that bubble_sort satisfies its specification. -/
theorem bubble_sort_correct (arr : List Int) :
  pre arr → post arr (bubble_sort arr) := by
  intro h
  unfold post
  constructor
  · sorry  -- Proof that the result is sorted
  · sorry  -- Proof that the result is a permutation of the input

#eval tests
