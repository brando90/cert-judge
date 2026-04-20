-- !benchmark @start import type=solution
import Mathlib
namespace InsertionSort
-- !benchmark @end import

-- !benchmark @start solution_aux
open List
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def insertionSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Inserts an element into a sorted list, maintaining sorted order. -/
def insert (a : Nat) : List Nat → List Nat
  | [] => [a]
  | x :: xs =>
    if a ≤ x then
      a :: x :: xs
    else
      x :: insert a xs
-- !benchmark @end code_aux

def insertionSort (l : List Nat) (h_precond : insertionSort_precond (l)) : List Nat :=
  -- !benchmark @start code
  match l with
  | [] => []
  | x :: xs => insert x (insertionSort xs (by simp))
  -- !benchmark @end code

-- !benchmark @start postcond_aux
/-- **Sorted property**: Result is sorted in ascending order. -/
def sorted_prop (xs : List Nat) : Prop := List.Sorted (· ≤ ·) (insertionSort xs (by simp))

/-- **Sorted theorem**: Result is sorted in ascending order. -/
@[simp] theorem sorted_thm (xs : List Nat) : sorted_prop xs := sorry

/-- **Permutation property**: Result is a permutation of input. -/
def permutation_prop (xs : List Nat) : Prop := insertionSort xs (by simp) ~ xs

/-- **Permutation theorem**: Result is a permutation of input. -/
@[simp] theorem permutation_thm (xs : List Nat) : permutation_prop xs := sorry

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (xs : List Nat) : Prop :=
  (insertionSort xs (by simp)).length = xs.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := sorry

/-- **Idempotent property**: Sorting twice gives same result as sorting once. -/
def idempotent_prop (xs : List Nat) : Prop :=
  insertionSort (insertionSort xs (by simp)) (by simp) = insertionSort xs (by simp)

/-- **Idempotent theorem**: Sorting twice gives same result as sorting once. -/
@[simp] theorem idempotent_thm (xs : List Nat) : idempotent_prop xs := sorry
-- !benchmark @end postcond_aux

@[reducible, simp]
def insertionSort_postcond (l : List Nat) (result : List Nat) (h_precond : insertionSort_precond (l)) :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
    (result ~ l) ∧
    (result.length = l.length) ∧
    (insertionSort result (by simp) = result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem insertionSort_spec_satisfied (l : List Nat) (h_precond : insertionSort_precond (l)) :
    insertionSort_postcond (l) (insertionSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof