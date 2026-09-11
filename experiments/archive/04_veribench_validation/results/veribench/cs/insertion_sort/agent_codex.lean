/-
# VeriBench Artifact: Insertion Sort
-/

import Mathlib.Data.List.Basic
import Mathlib.Data.List.Perm
import Mathlib.Data.List.Sort
import Std.Data.List.Basic

namespace InsertionSort

/-- Insertion sort algorithm for lists of integers.
    Builds the final sorted array one item at a time, inserting each element
    into its correct position among the previously sorted elements. -/
def insertionSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let rec insert (x : Int) (sorted : List Int) : List Int :=
      match sorted with
      | [] => [x]
      | y :: ys => if x ≤ y then x :: y :: ys else y :: insert x ys

    let rec sort (unsorted : List Int) (sorted : List Int) : List Int :=
      match unsorted with
      | [] => sorted
      | x :: xs => sort xs (insert x sorted)

    sort arr.tail [arr.head!]

/-- Precondition: Input must be a list of integers.
    Since Lean's type system enforces this, we just return true. -/
def pre (arr : List Int) : Prop := True

/-- Postcondition: The output must be a sorted permutation of the input. -/
def post (arr : List Int) (result : List Int) : Prop :=
  List.Perm arr result ∧ List.Sorted (· ≤ ·) result

/-- Correctness theorem for insertion sort. -/
theorem insertionSort_correct (arr : List Int) : 
  pre arr → post arr (insertionSort arr) := by
  intro _
  unfold post
  constructor
  sorry  -- Proof that result is a permutation of input
  sorry  -- Proof that result is sorted

/-! ## Tests -/

def test1 : insertionSort [3, 1, 2] = [1, 2, 3] := by rfl
def test2 : insertionSort [] = [] := by rfl
def test3 : insertionSort [1] = [1] := by rfl
def test4 : insertionSort [1, 2, 3] = [1, 2, 3] := by rfl
def test5 : insertionSort [2, 1, 3] = [1, 2, 3] := by rfl
def test6 : insertionSort [5, 2, 4, 6, 1, 3] = [1, 2, 3, 4, 5, 6] := by rfl
def test7 : insertionSort [9, 8, 7, 6, 5, 4, 3, 2, 1] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by rfl
def test8 : insertionSort [2, 6, 4, 3, 1, 5] = [1, 2, 3, 4, 5, 6] := by rfl
def test9 : insertionSort [2, 1] = [1, 2] := by rfl
def test10 : insertionSort [1, 2] = [1, 2] := by rfl
def test11 : insertionSort [3, 1, 4, 1, 2, 3] = [1, 1, 2, 3, 3, 4] := by rfl
def test12 : insertionSort [5, 5, 5, 5, 5] = [5, 5, 5, 5, 5] := by rfl
def test13 : insertionSort [1, 2, 3, 4, 5] = [1, 2, 3, 4, 5] := by rfl
def test14 : insertionSort [5, 4, 3, 2, 1] = [1, 2, 3, 4, 5] := by rfl
def test15 : insertionSort [3, 7, 1, 9, 2, 8, 4, 6, 5] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by rfl

end InsertionSort
