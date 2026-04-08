import Std.Data.List.Basic
import Std.Classes.Order
import Mathlib.Tactic
import Mathlib.Data.List.Perm
import Mathlib.Data.List.Sort

/--
  Quick sort for a list of integers.
  
  Edge cases:
  - Empty or single-element list returns copy.
-/
def quickSort (arr : List Int) : List Int :=
  match arr with
  | [] => []
  | [x] => [x]
  | pivot :: rest =>
    let (less, greater) := rest.partition (· ≤ pivot)
    quickSort less ++ [pivot] ++ quickSort greater

/-- Precondition: The input is a list of integers -/
def quickSort.pre (arr : List Int) : Prop :=
  True

/-- Postcondition: The output is a sorted permutation of the input -/
def quickSort.post (arr : List Int) (result : List Int) : Prop :=
  result.Sorted (· ≤ ·) ∧ result.Perm arr

/-- Correctness theorem for quickSort -/
theorem quickSort.correct (arr : List Int) (h : quickSort.pre arr) : 
  quickSort.post arr (quickSort arr) := by
  unfold quickSort.post
  constructor
  · induction arr with
    | nil => simp [quickSort]
    | cons head tail ih =>
      cases tail with
      | nil => simp [quickSort]
      | cons _ _ =>
        simp [quickSort]
        sorry -- Proof that the result is sorted
  · induction arr with
    | nil => simp [quickSort]
    | cons head tail ih =>
      cases tail with
      | nil => simp [quickSort]
      | cons _ _ =>
        simp [quickSort]
        sorry -- Proof that the result is a permutation of the input
  
/-- Test cases for quickSort -/
def quickSort.tests : IO Unit := do
  -- Basic functionality tests
  assert! (quickSort [3, 1, 2] == [1, 2, 3])
  assert! (quickSort [1, 2, 3] == [1, 2, 3])
  assert! (quickSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (quickSort [] == [])
  assert! (quickSort [1] == [1])
  
  -- Larger arrays
  assert! (quickSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (quickSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (quickSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (quickSort [2, 1] == [1, 2])
  assert! (quickSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (quickSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (quickSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (quickSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (quickSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (quickSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  -- Larger test case
  let large_arr := [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
  let expected := [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
  assert! (quickSort large_arr == expected)
  
  IO.println "All tests passed!"
