import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch

namespace BubbleSort

/-
  Bubble sort for a list of integers.
  Edge cases:
  - Empty list returns empty list.
-/

def bubbleSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let rec bubblePass (xs : List Int) (swapped : Bool) : List Int × Bool :=
      match xs with
      | [] => ([], swapped)
      | [x] => ([x], swapped)
      | x :: y :: rest =>
          if x > y then
            let (result, swappedRest) := bubblePass (x :: rest) swapped
            (y :: result, true)
          else
            let (result, swappedRest) := bubblePass (y :: rest) swapped
            (x :: result, swappedRest)

    let rec bubbleSortAux (arr : List Int) (n : Nat) : List Int :=
      if n = 0 then
        arr
      else
        let (newArr, swapped) := bubblePass arr false
        if swapped then
          bubbleSortAux newArr (n - 1)
        else
          newArr

    bubbleSortAux arr arr.length

-- Predicate to check if a list is sorted
def isSorted (arr : List Int) : Bool :=
  match arr with
  | [] => true
  | [_] => true
  | x :: y :: rest => x ≤ y && isSorted (y :: rest)

-- Predicate to check if two lists have the same elements (are permutations of each other)
def sameElements (xs ys : List Int) : Bool :=
  xs.all (fun x => ys.count (· = x) = xs.count (· = x)) &&
  ys.all (fun y => xs.count (· = y) = ys.count (· = y))

-- Precondition: no special precondition needed in Lean since type system ensures arr is List Int
def pre (_arr : List Int) : Prop := True

-- Postcondition: result is sorted and has the same elements as the input
def post (arr result : List Int) : Prop :=
  isSorted result ∧ sameElements arr result

-- Correctness theorem
theorem bubbleSort_correct (arr : List Int) : post arr (bubbleSort arr) := by
  sorry

-- Test cases
#eval bubbleSort [3, 1, 2] -- [1, 2, 3]
#eval bubbleSort [] -- []
#eval bubbleSort [1] -- [1]
#eval bubbleSort [1, 2, 3] -- [1, 2, 3]
#eval bubbleSort [2, 1, 3] -- [1, 2, 3]
#eval bubbleSort [5, 2, 4, 6, 1, 3] -- [1, 2, 3, 4, 5, 6]
#eval bubbleSort [9, 8, 7, 6, 5, 4, 3, 2, 1] -- [1, 2, 3, 4, 5, 6, 7, 8, 9]
#eval bubbleSort [2, 6, 4, 3, 1, 5] -- [1, 2, 3, 4, 5, 6]
#eval bubbleSort [2, 1] -- [1, 2]
#eval bubbleSort [1, 2] -- [1, 2]
#eval bubbleSort [3, 1, 4, 1, 2, 3] -- [1, 1, 2, 3, 3, 4]
#eval bubbleSort [5, 5, 5, 5, 5] -- [5, 5, 5, 5, 5]
#eval bubbleSort [1, 2, 3, 4, 5] -- [1, 2, 3, 4, 5]
#eval bubbleSort [5, 4, 3, 2, 1] -- [1, 2, 3, 4, 5]
#eval bubbleSort [3, 7, 1, 9, 2, 8, 4, 6, 5] -- [1, 2, 3, 4, 5, 6, 7, 8, 9]

end BubbleSort
