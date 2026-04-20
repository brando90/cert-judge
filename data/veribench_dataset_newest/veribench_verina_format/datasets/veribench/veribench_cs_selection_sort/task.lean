-- !benchmark @start import type=solution
import Mathlib
namespace SelectionSort
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def selectionSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
open List

/-- Finds and removes the minimum element from a list, returning it and the rest of the list.
    Panics if the list is empty. -/
def extractMin : List Nat → Nat × List Nat
  | [] => panic! "extractMin on empty list"
  | [x] => (x, [])
  | x :: xs =>
    let (minTail, restTail) := extractMin xs
    if x < minTail then
      (x, xs)
    else
      (minTail, x :: restTail)
-- !benchmark @end code_aux

def selectionSort (l : List Nat) (h_precond : selectionSort_precond (l)) : List Nat :=
  -- !benchmark @start code
  match l with
  | [] => []
  | l =>
    let (minVal, rest) := extractMin l
    minVal :: selectionSort rest (by simp)
  -- !benchmark @end code
termination_by l => l.length
decreasing_by
  sorry

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def selectionSort_postcond (l : List Nat) (result : List Nat) (h_precond : selectionSort_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
  (result ~ l) ∧
  (result.length = l.length) ∧
  (selectionSort result (by simp) = result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem selectionSort_spec_satisfied (l : List Nat) (h_precond : selectionSort_precond (l)) :
    selectionSort_postcond (l) (selectionSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof