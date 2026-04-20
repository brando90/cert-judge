-- !benchmark @start import type=solution
import Mathlib
namespace BubbleSort
-- !benchmark @end import

-- !benchmark @start solution_aux
open List
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def bubbleSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
def bubble_iter : List Nat → List Nat
  | [] => []
  | [x] => [x]
  | x :: y :: xs =>
    if x > y then
      y :: bubble_iter (x :: xs)
    else
      x :: bubble_iter (y :: xs)

def bubbleSortAux (l : List Nat) (k : Nat) : List Nat :=
  match k with
  | 0 => l
  | Nat.succ k' =>
    let l' := bubble_iter l
    if l' = l then
      l
    else
      bubbleSortAux l' k'
-- !benchmark @end code_aux

def bubbleSort (l : List Nat) (h_precond : bubbleSort_precond (l)) : List Nat :=
  -- !benchmark @start code
  bubbleSortAux l l.length
  -- !benchmark @end code

-- !benchmark @start postcond_aux
def sorted_prop (xs : List Nat) : Prop :=
  List.Sorted (· ≤ ·) (bubbleSort xs (by simp))

def permutation_prop (xs : List Nat) : Prop :=
  List.Perm xs (bubbleSort xs (by simp))

def length_preservation_prop (xs : List Nat) : Prop :=
  (bubbleSort xs (by simp)).length = xs.length

def empty_list_prop : Prop :=
  bubbleSort [] (by simp) = []
-- !benchmark @end postcond_aux

@[reducible, simp]
def bubbleSort_postcond (l : List Nat) (result : List Nat) (h_precond : bubbleSort_precond (l)) :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
    (List.Perm l result) ∧
    (result.length = l.length) ∧
    (bubbleSort [] (by simp) = [])
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem length_bubbleSort (l : List Nat) :
  (bubbleSort l (by simp)).length = l.length := by
  sorry

theorem sorted_bubbleSort (l : List Nat) :
  List.Sorted (fun x y => x ≤ y) (bubbleSort l (by simp)) := by
  sorry

theorem perm_bubbleSort (l : List Nat) :
    bubbleSort l (by simp) ~ l := by
  sorry

theorem idempotent_bubbleSort (l : List Nat) :
    bubbleSort (bubbleSort l (by simp)) (by simp) = bubbleSort l (by simp) := by
  sorry

theorem sorted_thm (xs : List Nat) : sorted_prop xs := by
  sorry

theorem permutation_thm (xs : List Nat) : permutation_prop xs := by
  sorry

theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := by
  sorry

theorem empty_list_thm : empty_list_prop := by
  sorry
-- !benchmark @end proof_aux

theorem bubbleSort_spec_satisfied (l : List Nat) (h_precond : bubbleSort_precond (l)) :
    bubbleSort_postcond (l) (bubbleSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof