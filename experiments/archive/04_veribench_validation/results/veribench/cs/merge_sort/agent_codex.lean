import VeriBench

namespace MergeSort

/-- Check if the array is a list of integers. -/
def pre (arr : List Int) : Prop := True

/-- Helper function to merge two sorted lists -/
def merge (left : List Int) (right : List Int) : List Int :=
  match left, right with
  | [], r => r
  | l, [] => l
  | l::ls, r::rs =>
    if l <= r then
      l :: merge ls (r::rs)
    else
      r :: merge (l::ls) rs

/-- Merge sort implementation for a list of integers. -/
def merge_sort (arr : List Int) : List Int :=
  if arr.length <= 1 then
    arr
  else
    let mid := arr.length / 2
    let left := merge_sort (arr.take mid)
    let right := merge_sort (arr.drop mid)
    merge left right

/-- Checks if a list is sorted in ascending order -/
def is_sorted (arr : List Int) : Prop :=
  match arr with
  | [] => True
  | [_] => True
  | x::y::rest => x ≤ y ∧ is_sorted (y::rest)

/-- Checks if two lists have the same elements (possibly in different order) -/
def same_elements (a b : List Int) : Prop :=
  a.toMultiset = b.toMultiset

/-- Post-condition: result is sorted and contains the same elements as input -/
def post (arr : List Int) (result : List Int) : Prop :=
  is_sorted result ∧ same_elements arr result

/-- Merge sort preserves elements and sorts the list -/
theorem merge_sort_correct (arr : List Int) : 
  pre arr → post arr (merge_sort arr) := by
  sorry

/-- Tests for merge_sort -/
def test_merge_sort : IO Unit := do
  -- Basic functionality tests
  assert! (merge_sort [3, 1, 2] = [1, 2, 3])
  assert! (merge_sort [1, 2, 3] = [1, 2, 3])
  assert! (merge_sort [2, 1, 3] = [1, 2, 3])
  
  -- Edge cases
  assert! (merge_sort [] = [])
  assert! (merge_sort [1] = [1])
  
  -- Larger arrays
  assert! (merge_sort [5, 2, 4, 6, 1, 3] = [1, 2, 3, 4, 5, 6])
  assert! (merge_sort [9, 8, 7, 6, 5, 4, 3, 2, 1] = [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (merge_sort [2, 6, 4, 3, 1, 5] = [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (merge_sort [2, 1] = [1, 2])
  assert! (merge_sort [1, 2] = [1, 2])
  
  -- Duplicates
  assert! (merge_sort [3, 1, 4, 1, 2, 3] = [1, 1, 2, 3, 3, 4])
  assert! (merge_sort [5, 5, 5, 5, 5] = [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (merge_sort [1, 2, 3, 4, 5] = [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (merge_sort [5, 4, 3, 2, 1] = [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (merge_sort [3, 7, 1, 9, 2, 8, 4, 6, 5] = [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  -- Larger test case
  let large_arr := [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
  let expected := [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
  assert! (merge_sort large_arr = expected)
  
  IO.println "All tests passed."

/-- Theorem: merge preserves elements and maintains sorting -/
theorem merge_preserves_elements_and_sorting (l r : List Int) :
  is_sorted l → is_sorted r → 
  is_sorted (merge l r) ∧ same_elements (merge l r) (l ++ r) := by
  sorry

/-- Theorem: merge_sort produces a sorted list -/
theorem merge_sort_produces_sorted (arr : List Int) :
  is_sorted (merge_sort arr) := by
  sorry

/-- Theorem: merge_sort preserves elements -/
theorem merge_sort_preserves_elements (arr : List Int) :
  same_elements (merge_sort arr) arr := by
  sorry

end MergeSort
