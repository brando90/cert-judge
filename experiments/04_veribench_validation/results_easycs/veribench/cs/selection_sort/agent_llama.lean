import Std.Data.List.Basic

namespace SelectionSort

/-- Check if an element is the minimum in a list from a given index -/
def isMinFrom (a : Int) (l : List Int) (idx : Nat) : Prop :=
  ∀ j, idx ≤ j → j < l.length → a ≤ l[j]!

/-- Find the minimum element's index in a list starting from a given index -/
def findMinIdx (l : List Int) (start : Nat) : Nat :=
  let rec loop (i : Nat) (minIdx : Nat) : Nat :=
    if i < l.length then
      if l[i]! < l[minIdx]! then
        loop (i + 1) i
      else
        loop (i + 1) minIdx
    else
      minIdx
  loop start start

/-- Swap elements at two indices in a list -/
def swap (l : List Int) (i j : Nat) : List Int :=
  if i = j then l else
    let vi := l[i]!
    let vj := l[j]!
    l.set! i vj |>.set! j vi

/-- Implementation of selection sort algorithm for integers -/
def selectionSort (arr : List Int) : List Int :=
  let rec loop (result : List Int) (i : Nat) : List Int :=
    if i < result.length then
      let minIdx := findMinIdx result i
      loop (swap result i minIdx) (i + 1)
    else
      result
  loop arr 0

/-- Predicate that checks if a list is sorted -/
def isSorted (l : List Int) : Prop :=
  ∀ i j, i < j → j < l.length → l[i]! ≤ l[j]!

/-- Predicate that checks if two lists are permutations of each other -/
def isPermutationOf (l1 l2 : List Int) : Prop :=
  l1.length = l2.length ∧
  ∀ x, l1.count x = l2.count x

/-- Selection sort preserves the elements of the input list -/
theorem selectionSort_preserves_elements (arr : List Int) :
  isPermutationOf (selectionSort arr) arr := sorry

/-- Selection sort produces a sorted list -/
theorem selectionSort_sorts (arr : List Int) :
  isSorted (selectionSort arr) := sorry

/-- Main correctness theorem for selection sort -/
theorem selectionSort_correct (arr : List Int) :
  isSorted (selectionSort arr) ∧ isPermutationOf (selectionSort arr) arr :=
  ⟨selectionSort_sorts arr, selectionSort_preserves_elements arr⟩

/-- Test cases for selection sort -/
def runTests : IO Unit := do
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
  
  IO.println "All tests passed!"

end SelectionSort
