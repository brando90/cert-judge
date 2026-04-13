import Std.Data.List.Basic
import Mathlib.Tactic
open List

namespace InsertionSort

/-- Checks if a list is a valid input for insertion sort -/
def pre (arr : List Int) : Prop := True

/-- Insertion sort for a list of integers -/
def insertion_sort (arr : List Int) : List Int :=
  let rec insert_element (x : Int) (sorted : List Int) : List Int :=
    match sorted with
    | [] => [x]
    | h :: t => if x ≤ h then x :: h :: t else h :: insert_element x t
  
  let rec sort (remaining : List Int) (sorted : List Int) : List Int :=
    match remaining with
    | [] => sorted
    | h :: t => sort t (insert_element h sorted)
  
  sort arr []

/-- Predicate that checks if a list is sorted -/
def is_sorted (l : List Int) : Prop :=
  ∀ i j, i < j → j < l.length → l[i]! ≤ l[j]!

/-- Predicate that checks if two lists are permutations of each other -/
def is_permutation (l₁ l₂ : List Int) : Prop :=
  ∀ x, count (· = x) l₁ = count (· = x) l₂

/-- Postcondition for insertion sort: the result is sorted and a permutation of the input -/
def post (arr : List Int) (result : List Int) : Prop :=
  is_sorted result ∧ is_permutation arr result

/-- Insertion sort is correct -/
theorem insertion_sort_correct (arr : List Int) (h : pre arr) : 
  post arr (insertion_sort arr) := by
  sorry

/-- Tests for insertion sort -/
def test : IO Unit := do
  -- Basic functionality tests
  assert! (insertion_sort [3, 1, 2] == [1, 2, 3])
  assert! (insertion_sort [1, 2, 3] == [1, 2, 3])
  assert! (insertion_sort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (insertion_sort [] == [])
  assert! (insertion_sort [1] == [1])
  
  -- Larger arrays
  assert! (insertion_sort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (insertion_sort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (insertion_sort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (insertion_sort [2, 1] == [1, 2])
  assert! (insertion_sort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (insertion_sort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (insertion_sort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (insertion_sort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (insertion_sort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (insertion_sort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  IO.println "All tests passed!"

end InsertionSort
