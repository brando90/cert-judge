import Std.Data.List.Basic

def pre (arr : List Int) : Bool := true

/-- Merges two sorted lists into a single sorted list. -/
def merge (left : List Int) (right : List Int) : List Int :=
  match left, right with
  | [], right => right
  | left, [] => left
  | h1::t1, h2::t2 =>
    if h1 <= h2 then
      h1 :: merge t1 (h2::t2)
    else
      h2 :: merge (h1::t1) t2

/-- 
Sorts a list using the merge sort algorithm.
It divides the array into halves, recursively sorts them, and then merges 
the sorted halves back together.
-/
def mergeSort (arr : List Int) : List Int :=
  if arr.length <= 1 then
    arr
  else
    let mid := arr.length / 2
    let left := mergeSort (arr.take mid)
    let right := mergeSort (arr.drop mid)
    merge left right

-- Tests
example : mergeSort [3, 1, 2] = [1, 2, 3] := by decide
example : mergeSort [1, 2, 3] = [1, 2, 3] := by decide
example : mergeSort [2, 1, 3] = [1, 2, 3] := by decide
example : mergeSort [] = [] := by decide
example : mergeSort [1] = [1] := by decide
example : mergeSort [5, 2, 4, 6, 1, 3] = [1, 2, 3, 4, 5, 6] := by decide
example : mergeSort [9, 8, 7, 6, 5, 4, 3, 2, 1] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by decide
example : mergeSort [2, 6, 4, 3, 1, 5] = [1, 2, 3, 4, 5, 6] := by decide
example : mergeSort [2, 1] = [1, 2] := by decide
example : mergeSort [1, 2] = [1, 2] := by decide
example : mergeSort [3, 1, 4, 1, 2, 3] = [1, 1, 2, 3, 3, 4] := by decide
example : mergeSort [5, 5, 5, 5, 5] = [5, 5, 5, 5, 5] := by decide
example : mergeSort [1, 2, 3, 4, 5] = [1, 2, 3, 4, 5] := by decide
example : mergeSort [5, 4, 3, 2, 1] = [1, 2, 3, 4, 5] := by decide
example : mergeSort [3, 7, 1, 9, 2, 8, 4, 6, 5] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by decide
example : mergeSort [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42] = [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90] := by decide

-- Specifications

def sorted (arr : List Int) : Prop :=
  ∀ i j, i < j → j < arr.length → arr[i]! ≤ arr[j]!

def isPermutation (a b : List Int) : Prop :=
  ∀ x, a.count x = b.count x

-- Precondition (always true for List Int)
theorem mergeSortPre (arr : List Int) : pre arr := by
  simp [pre]

-- Postcondition: Output is sorted
theorem mergeSortSorted (arr : List Int) : sorted (mergeSort arr) := by
  sorry

-- Postcondition: Output is a permutation of input
theorem mergeSortPermutation (arr : List Int) : isPermutation arr (mergeSort arr) := by
  sorry

-- Correctness theorem
theorem mergeSortCorrect (arr : List Int) : 
  pre arr → sorted (mergeSort arr) ∧ isPermutation arr (mergeSort arr) := by
  intro h
  apply And.intro
  · apply mergeSortSorted
  · apply mergeSortPermutation
