```lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch

namespace HeapSort

/-- Represents a precondition for heap sort. Since Lean has static typing, 
    we don't need to check types at runtime. -/
def pre (arr : List Int) : Prop := True

/-- Maintains the max heap property for a subtree rooted at index i. -/
def heapify (arr : List Int) (n : Nat) (i : Nat) : List Int :=
  if h : i < arr.length ∧ n ≤ arr.length then
    let largest := i
    let left := 2 * i + 1
    let right := 2 * i + 2
    
    let largest := if left < n ∧ arr[left]? = some (arr[largest]?.getD 0) ∧ arr[left]?.getD 0 > arr[largest]?.getD 0 then
                    left
                   else
                    largest
    
    let largest := if right < n ∧ arr[right]? = some (arr[right]?.getD 0) ∧ arr[right]?.getD 0 > arr[largest]?.getD 0 then
                    right
                   else
                    largest
    
    if largest ≠ i then
      let swapped := arr.set i (arr[largest]?.getD 0) |>.set largest (arr[i]?.getD 0)
      heapify swapped n largest
    else
      arr
  else
    arr

/-- Builds a max heap from the array. -/
def buildMaxHeap (arr : List Int) : List Int :=
  let n := arr.length
  let indices := List.range (n / 2)
  indices.foldr (fun i acc => heapify acc n ((n / 2 - 1) - i)) arr

/-- Heap sort implementation. -/
def heap_sort (arr : List Int) : List Int :=
  if arr.length ≤ 1 then
    arr
  else
    let result := buildMaxHeap arr
    let indices := List.range (arr.length - 1)
    indices.foldl (fun acc i => 
      let j := (arr.length - 1) - i
      let swapped := acc.set 0 (acc[j]?.getD 0) |>.set j (acc[0]?.getD 0)
      heapify swapped j 0
    ) result

/-- Post-condition: The output is sorted in ascending order. -/
def post (arr : List Int) (result : List Int) : Prop :=
  result.sorted (· ≤ ·) ∧ result.perm arr

/-- Correctness theorem for heap sort. -/
theorem heap_sort_correct (arr : List Int) (h : pre arr) : post arr (heap_sort arr) := by
  sorry

/-- Tests for heap sort -/
def test : IO Unit := do
  -- Basic functionality tests
  assert $ heap_sort [3, 1, 2] == [1, 2, 3]
  assert $ heap_sort [1, 2, 3] == [1, 2, 3]
  assert $ heap_sort [2, 1, 3] == [1, 2, 3]
  
  -- Edge cases
  assert $ heap_sort ([] : List Int) == []
  assert $ heap_sort [1] == [1]
  
  -- Larger arrays
  assert $ heap_sort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6]
  assert $ heap_sort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
  assert $ heap_sort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6]
  
  -- Two elements
  assert $ heap_sort [2, 1] == [1, 2]
  assert $ heap_sort [1, 2] == [1, 2]
  
  -- Duplicates
  assert $ heap_sort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4]
  assert $ heap_sort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5]
  
  -- Already sorted
  assert $ heap_sort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5]
  
  -- Reverse sorted
  assert $ heap_sort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5]
  
  -- Random order
  assert $ heap_sort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
  
  -- Larger test case
  let large_arr := [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
  let expected := [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
  assert $ heap_sort large_arr == expected

  IO.println "All tests passed"

end HeapSort
```
