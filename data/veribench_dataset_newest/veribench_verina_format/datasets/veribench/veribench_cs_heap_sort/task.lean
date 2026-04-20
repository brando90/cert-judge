-- !benchmark @start import type=solution
import Mathlib
namespace HeapSort
-- !benchmark @end import

-- !benchmark @start solution_aux
open List
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def heapSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Gets the left child index in a heap represented as a list -/
def leftChild (i : Nat) : Nat := 2 * i + 1

/-- Gets the right child index in a heap represented as a list -/
def rightChild (i : Nat) : Nat := 2 * i + 2

/-- Gets the parent index in a heap represented as a list -/
def parent (i : Nat) : Nat := (i - 1) / 2

/-- Swaps two elements at given indices in a list -/
def swap (l : List Nat) (i j : Nat) : List Nat :=
  match l[i]?, l[j]? with
  | some a, some b =>
    let l' := l.set i b
    l'.set j a
  | _, _ => l

/-- Maintains the max heap property by moving an element down the heap -/
partial def heapify (l : List Nat) (i : Nat) (heapSize : Nat) : List Nat :=
  if i < heapSize ∧ i < l.length then
    let left := leftChild i
    let right := rightChild i
    let largest :=
      if left < heapSize ∧ left < l.length then
        match l[i]?, l[left]? with
        | some vi, some vl => if vl > vi then left else i
        | _, _ => i
      else i
    let largest :=
      if right < heapSize ∧ right < l.length then
        match l[largest]?, l[right]? with
        | some vl, some vr => if vr > vl then right else largest
        | _, _ => largest
      else largest
    if largest ≠ i then
      let swapped := swap l i largest
      heapify swapped largest heapSize
    else l
  else l

/-- Builds a max heap from an unsorted list -/
def buildMaxHeap (l : List Nat) : List Nat :=
  let len := l.length
  if len ≤ 1 then l
  else
    let rec build (l : List Nat) (i : Nat) : List Nat :=
      if i = 0 then heapify l 0 len
      else
        let heapified := heapify l i len
        build heapified (i - 1)
    build l (parent (len - 1))
-- !benchmark @end code_aux

def heapSort (l : List Nat) (h_precond : heapSort_precond (l)) : List Nat :=
  -- !benchmark @start code
  if l.length ≤ 1 then l
  else
    let heap := buildMaxHeap l
    let rec sort (l : List Nat) (heapSize : Nat) : List Nat :=
      if heapSize ≤ 1 then l
      else
        let swapped := swap l 0 (heapSize - 1)
        let heapified := heapify swapped 0 (heapSize - 1)
        sort heapified (heapSize - 1)
    sort heap l.length
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def heapSort_postcond (l : List Nat) (result : List Nat) (h_precond : heapSort_precond (l)) : Prop :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
    (result ~ l) ∧
    (result.length = l.length) ∧
    (heapSort (result) (by simp) = result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem heapSort_spec_satisfied (l : List Nat) (h_precond : heapSort_precond (l)) :
    heapSort_postcond (l) (heapSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof