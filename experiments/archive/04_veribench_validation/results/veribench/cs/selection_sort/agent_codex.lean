import Std.Data.List.Basic

/-- Selection sort for a list of integers.

Edge cases:
- Empty list returns empty list.
- Non-integer elements are invalid (not modeled in Lean since type system enforces this).
-/

def selectionSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let result := arr
    let n := result.length
    
    let rec sort (result : List Int) (i : Nat) : List Int :=
      if i >= n then
        result
      else
        -- Find the minimum element in the remaining unsorted array
        let rec findMinIdx (j : Nat) (minIdx : Nat) : Nat :=
          if j >= n then
            minIdx
          else
            let newMinIdx := if result.get! j < result.get! minIdx then j else minIdx
            findMinIdx (j+1) newMinIdx
        
        let minIdx := findMinIdx (i+1) i
        
        -- Swap the found minimum element with the first element
        let swapped := result.set! i (result.get! minIdx) |>.set! minIdx (result.get! i)
        
        sort swapped (i+1)
    
    sort result 0

/-- Predicate stating that a list is sorted in ascending order -/
def isSorted (arr : List Int) : Prop :=
  ∀ i j, i < j → j < arr.length → arr[i]! ≤ arr[j]!

/-- Predicate stating that two lists are permutations of each other -/
def isPermutationOf (arr1 arr2 : List Int) : Prop :=
  arr1.length = arr2.length ∧ 
  ∀ x, arr1.count x = arr2.count x

/-- Post-condition for selection sort: result is sorted and a permutation of the input -/
def selectionSortPost (arr result : List Int) : Prop :=
  isSorted result ∧ isPermutationOf arr result

/-- Selection sort returns a sorted permutation of the input -/
theorem selectionSort_correct (arr : List Int) : 
  selectionSortPost arr (selectionSort arr) := sorry

/-- Unit tests for selection sort -/
def selectionSort_tests : IO Unit := do
  -- Basic functionality tests
  assert! (selectionSort [3, 1, 2] == [1, 2, 3])
  assert! (selectionSort [1, 2, 3] == [1, 2, 3])
  assert! (selectionSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (selectionSort [] == [])
  assert! (selectionSort [1] == [1])
  
  -- Larger arrays
  assert! (selectionSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (selectionSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (selectionSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (selectionSort [2, 1] == [1, 2])
  assert! (selectionSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (selectionSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (selectionSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (selectionSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (selectionSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (selectionSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  IO.println "All tests passed."
