-- !benchmark @start import type=solution
import Mathlib
namespace MergeSort

open List
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def mergeSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
/-- Merges two sorted lists into a single sorted list. -/
def merge (l₁ l₂ : List Nat) : List Nat :=
  match l₁, l₂ with
  | [], _ => l₂
  | _, [] => l₁
  | x :: xs, y :: ys =>
    if x ≤ y then
      x :: merge xs (y :: ys)
    else
      y :: merge (x :: xs) ys
-- !benchmark @end code_aux


partial def mergeSort : List Nat → mergeSort_precond (l) → List Nat
  | [], _ => []
  | [x], _ => [x]
  | l, h_precond =>
    -- !benchmark @start code
    let (front, back) := l.splitAt (l.length / 2)
    merge (mergeSort front (by simp)) (mergeSort back (by simp))
    -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def mergeSort_postcond (l : List Nat) (result : List Nat) (h_precond : mergeSort_precond (l)) :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
    (result ~ l) ∧
    (result.length = l.length) ∧
    (mergeSort result (by simp) = result)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
/-- **Sorted property**: Result is sorted in ascending order. -/
def sorted_prop (xs : List Nat) : Prop := List.Sorted (· ≤ ·) (mergeSort xs (by simp))

/-- **Sorted theorem**: Result is sorted in ascending order. -/
@[simp] theorem sorted_thm (xs : List Nat) : sorted_prop xs := by
  sorry

/-- **Permutation property**: Result is a permutation of input. -/
def permutation_prop (xs : List Nat) : Prop := mergeSort xs (by simp) ~ xs

/-- **Permutation theorem**: Result is a permutation of input. -/
@[simp] theorem permutation_thm (xs : List Nat) : permutation_prop xs := by
  sorry

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (xs : List Nat) : Prop := (mergeSort xs (by simp)).length = xs.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := by
  sorry

/-- **Idempotent property**: Sorting twice gives same result as sorting once. -/
def idempotent_prop (xs : List Nat) : Prop :=
  mergeSort (mergeSort xs (by simp)) (by simp) = mergeSort xs (by simp)

/-- **Idempotent theorem**: Sorting twice gives same result as sorting once. -/
@[simp] theorem idempotent_thm (xs : List Nat) : idempotent_prop xs := by
  sorry

/-- **Post‑condition**: conjunction of all desired properties for mergeSort. -/
def Post_prop (xs : List Nat) : Prop :=
  (sorted_prop xs) ∧
    (permutation_prop xs) ∧
    (length_preservation_prop xs) ∧
    (idempotent_prop xs)
-- !benchmark @end proof_aux


theorem mergeSort_spec_satisfied (l : List Nat) (h_precond : mergeSort_precond (l)) :
    mergeSort_postcond (l) (mergeSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof