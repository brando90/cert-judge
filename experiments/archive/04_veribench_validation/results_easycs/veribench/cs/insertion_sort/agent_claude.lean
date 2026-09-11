import Mathlib.Data.List.Basic
import Mathlib.Data.List.Perm
import Mathlib.Tactic

/-- Insertion sort for a list of integers.

Edge cases:
- Empty list returns empty list.
-/

def insertionSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let result := arr
    let rec loop (i : Nat) (acc : List Int) : List Int :=
      if i >= result.length then
        acc
      else
        let key := result[i]!
        let rec insertKey (j : Int) (acc' : List Int) : List Int :=
          if j < 0 || acc'[j.toNat]! <= key then
            acc'.set (j + 1).toNat key
          else
            insertKey (j - 1) (acc'.set (j + 1).toNat acc'[j.toNat]!)
        
        loop (i + 1) (insertKey (i.toInt - 1) acc)
    
    loop 1 result

/-- Predicate that checks if a list is sorted -/
def isSorted (l : List Int) : Prop :=
  ∀ i j, i < j → j < l.length → l[i]! ≤ l[j]!

/-- Predicate that checks if two lists have the same elements (are permutations of each other) -/
def sameElements (l1 l2 : List Int) : Prop :=
  l1.perm l2

/-- Precondition for insertion sort: any list of integers is valid -/
def insertionSort.pre (arr : List Int) : Prop := True

/-- Postcondition for insertion sort: the output is sorted and has the same elements as the input -/
def insertionSort.post (arr result : List Int) : Prop :=
  isSorted result ∧ sameElements arr result

/-- Theorem stating that insertionSort satisfies its specification -/
theorem insertionSort_correct (arr : List Int) :
  insertionSort.pre arr → insertionSort.post arr (insertionSort arr) := by
  sorry

/-- Tests for insertionSort -/
def insertionSort_test : IO Unit := do
  -- Basic functionality tests
  assert! (insertionSort [3, 1, 2] == [1, 2, 3])
  assert! (insertionSort [1, 2, 3] == [1, 2, 3])
  assert! (insertionSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (insertionSort [] == [])
  assert! (insertionSort [1] == [1])
  
  -- Larger arrays
  assert! (insertionSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (insertionSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (insertionSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (insertionSort [2, 1] == [1, 2])
  assert! (insertionSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (insertionSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (insertionSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (insertionSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (insertionSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (insertionSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])

  IO.println "All tests passed!"
