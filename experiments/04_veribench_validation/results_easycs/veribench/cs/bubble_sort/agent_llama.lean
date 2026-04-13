import Mathlib.Tactic.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.List.Perm
import Mathlib.Data.List.Sorted

def bubbleSort (arr : List Int) : List Int :=
  if arr = [] then
    []
  else
    let result := arr
    let n := result.length
    let rec loop (i : Nat) (result : List Int) (swapped : Bool) : List Int :=
      if i ≥ n then
        result
      else
        let rec innerLoop (j : Nat) (result : List Int) (swapped : Bool) : (List Int × Bool) :=
          if j ≥ n - i - 1 then
            (result, swapped)
          else
            let (result', swapped') :=
              match result.get? j, result.get? (j+1) with
              | some a, some b =>
                if a > b then
                  (result.set j b |>.set (j+1) a, true)
                else
                  (result, swapped)
              | _, _ => (result, swapped)
            innerLoop (j+1) result' swapped'
        
        let (result', swapped') := innerLoop 0 result swapped
        if !swapped' then
          result'
        else
          loop (i+1) result' false
          
    loop 0 result false

def isSorted (arr : List Int) : Bool :=
  List.pairwise (· ≤ ·) arr

def isPermutation (arr1 arr2 : List Int) : Bool :=
  arr1.perm arr2

def bubbleSortPre (arr : List Int) : Prop := True

def bubbleSortPost (arr : List Int) (result : List Int) : Prop :=
  isSorted result ∧ isPermutation arr result

theorem bubbleSort_preserves_length (arr : List Int) : 
  (bubbleSort arr).length = arr.length := by
  sorry

theorem bubbleSort_sorts (arr : List Int) : 
  isSorted (bubbleSort arr) := by
  sorry

theorem bubbleSort_permutes (arr : List Int) : 
  isPermutation arr (bubbleSort arr) := by
  sorry

theorem bubbleSort_correct (arr : List Int) : 
  bubbleSortPre arr → bubbleSortPost arr (bubbleSort arr) := by
  intro _
  constructor
  · apply bubbleSort_sorts
  · apply bubbleSort_permutes

/-- Tests -/

def test_bubbleSort : IO Unit := do
  -- Basic functionality tests
  assert! (bubbleSort [3, 1, 2] == [1, 2, 3])
  assert! (bubbleSort [1, 2, 3] == [1, 2, 3])
  assert! (bubbleSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (bubbleSort ([] : List Int) == [])
  assert! (bubbleSort [1] == [1])
  
  -- Larger arrays
  assert! (bubbleSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (bubbleSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (bubbleSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (bubbleSort [2, 1] == [1, 2])
  assert! (bubbleSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (bubbleSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (bubbleSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (bubbleSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (bubbleSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (bubbleSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  IO.println "All tests passed!"

#eval test_bubbleSort
