import Mathlib.Data.List.Basic
import Mathlib.Data.List.Sort
import Mathlib.Data.Int.Basic

namespace CountingSort

def pre (arr : List Int) : Bool := true

/-- Sorts a list using the counting sort algorithm.
    It counts the occurrences of each element and uses this information
    to place elements in their correct sorted positions. -/
def countingSort (arr : List Int) : List Int :=
  if !pre arr then
    [] -- In Lean we don't have exceptions, so return empty list for invalid input
  else if arr.isEmpty then
    []
  else
    let maxVal := arr.foldl max arr.head!
    let minVal := arr.foldl min arr.head!
    
    -- Handle negative numbers by shifting the range
    let rangeSize := maxVal - minVal + 1
    
    -- Create count array
    let count := List.replicate rangeSize.toNat 0
    
    -- Count occurrences of each element
    let count := arr.foldl (fun c num => 
      let idx := (num - minVal).toNat
      c.set idx (c.get! idx + 1)
    ) count
    
    -- Build the sorted array
    let result := List.nil
    let result := List.foldl (fun res i =>
      let num := i + minVal
      let count := count.get! i.toNat
      res ++ List.replicate count num
    ) result (List.range rangeSize.toNat)
    
    result

/-- Post-condition: the output is a sorted permutation of the input -/
def post (arr : List Int) (result : List Int) : Prop :=
  result.Sorted (· ≤ ·) ∧ result.Perm arr

theorem countingSort_correct (arr : List Int) (h : pre arr) : 
  post arr (countingSort arr) := sorry

/-- Test cases for the counting sort function -/
def test : IO Unit := do
  -- Basic functionality tests
  assert! (countingSort [3, 1, 2] == [1, 2, 3])
  assert! (countingSort [1, 2, 3] == [1, 2, 3])
  assert! (countingSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (countingSort ([] : List Int) == [])
  assert! (countingSort [1] == [1])
  
  -- Larger arrays
  assert! (countingSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (countingSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (countingSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (countingSort [2, 1] == [1, 2])
  assert! (countingSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (countingSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (countingSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  assert! (countingSort [3, 1, 2, 1, 3, 2] == [1, 1, 2, 2, 3, 3])
  assert! (countingSort [1, 0, 2, 0, 1, 0] == [0, 0, 0, 1, 1, 2])
  
  -- Already sorted
  assert! (countingSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (countingSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (countingSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  -- With zeros
  assert! (countingSort [0, 3, 1, 0, 2] == [0, 0, 1, 2, 3])
  
  -- Larger test case
  let largeArr := [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
  let expected := [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
  assert! (countingSort largeArr == expected)
  
  -- Negative numbers
  assert! (countingSort [-3, 1, -1, 0, 2] == [-3, -1, 0, 1, 2])
  
  IO.println "All tests passed!"

end CountingSort
