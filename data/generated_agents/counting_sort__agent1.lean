import Std.Data.List.Basic
import Mathlib.Tactic

namespace VeriBench.CountingSort

/-- Predicates for checking if the input is a list of integers -/
def pre (arr : List Int) : Prop := True

/-- Specification: the output list is a sorted permutation of the input list -/
def post (arr result : List Int) : Prop :=
  result.Perm arr ∧ result.Sorted (· ≤ ·)

/-- Implementation of counting sort for integers -/
def countingSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let maxVal := arr.maximum?.get!
    let minVal := arr.minimum?.get!
    
    -- Handle negative numbers by shifting the range
    let rangeSize := maxVal - minVal + 1
    
    -- Create count array initialized with zeros
    let mut count := List.replicate rangeSize 0
    
    -- Count occurrences of each element
    for num in arr do
      let idx := num - minVal
      count := count.set! idx (count[idx]! + 1)
    
    -- Build the sorted array
    let mut result := []
    for i in List.range rangeSize do
      result := result ++ List.replicate count[i]! (i + minVal)
    
    result

/-- Correctness theorem: the implementation satisfies the specification -/
theorem countingSort_correct (arr : List Int) :
  pre arr → post arr (countingSort arr) := by
  intro h
  unfold post
  constructor
  · sorry -- Proof that the result is a permutation of the input
  · sorry -- Proof that the result is sorted

/-- Test cases -/
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
  
  IO.println "All tests passed."

end VeriBench.CountingSort
