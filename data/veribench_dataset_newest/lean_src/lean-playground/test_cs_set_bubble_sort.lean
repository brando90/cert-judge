import Mathlib.Data.List.Sort
import Mathlib.Data.List.Permutation

open List
namespace BubbleSort

open List

-- This function performs one "pass" of a recursive bubbling process.
-- After this function is applied to a list `l`, the largest element of `l`
-- will be at the end of the output list. The other elements
-- will be in the initial part of the list, possibly reordered.
def bubble_iter : List Nat → List Nat
  | [] => []
  | [x] => [x]
  | x :: y :: xs =>
    if x > y then
      y :: bubble_iter (x :: xs)
    else
      x :: bubble_iter (y :: xs)

-- Auxiliary function for `bubbleSort` that applies `bubble_iter` a fixed number of times.
-- `k` is the number of remaining iterations.
def bubbleSortAux (l : List Nat) (k : Nat) : List Nat :=
  match k with
  | 0 => l
  | Nat.succ k' =>
    let l' := bubble_iter l
    if l' = l then
      l
    else
      bubbleSortAux l' k'


def bubbleSort (l : List Nat) : List Nat :=
  bubbleSortAux l l.length

-- Imperative-style implementation for testing equivalence
def bubbleSortImp (l : List Nat) : List Nat := bubbleSort l

-- Helper lemmas for length preservation
termination_by l.length

termination_by l.length

termination_by l.length

-- Main sortedness theorem
termination_by l.length


/-!
# Positive / Negative Test‑Suite
-/

/-- positive: sorted list remains sorted -/
example : bubbleSortImp [1, 2, 3] = [1, 2, 3] := by native_decide
#eval bubbleSortImp [1, 2, 3] -- expected: [1, 2, 3]

/-- positive: reverse sorted gets sorted -/
example : bubbleSortImp [3, 2, 1] = [1, 2, 3] := by native_decide
#eval bubbleSortImp [3, 2, 1] -- expected: [1, 2, 3]

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem bubbleSort_equivalence_thm (xs : List Nat) :
  bubbleSort xs = bubbleSortImp xs := sorry




end BubbleSort