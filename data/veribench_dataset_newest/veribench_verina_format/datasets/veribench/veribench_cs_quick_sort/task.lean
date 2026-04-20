-- !benchmark @start import type=solution
import Mathlib
namespace QuickSort
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def quickSort_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
open List

/-- Partitions a list into elements less than or equal to the pivot,
    and elements greater than the pivot. -/
def partition (pivot : Nat) : List Nat → (List Nat × List Nat)
  | [] => ([], [])
  | x :: xs =>
    let (lesser, greater) := partition pivot xs
    if x ≤ pivot then
      (x :: lesser, greater)
    else
      (lesser, x :: greater)
-- !benchmark @end code_aux

partial def quickSort (xs : List Nat) (h_precond : quickSort_precond (xs)) : List Nat :=
  -- !benchmark @start code
  match xs with
  | [] => []
  | pivot :: tail =>
    let (lesser, greater) := partition pivot tail
    quickSort lesser (by simp) ++ [pivot] ++ quickSort greater (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Sorted property**: Result is sorted in ascending order. -/
def sorted_prop (xs : List Nat) : Prop := List.Sorted (· ≤ ·) (quickSort xs (by simp))

/-- **Sorted theorem**: Result is sorted in ascending order. -/
@[simp] theorem sorted_thm (xs : List Nat) : sorted_prop xs := by
  sorry

/-- **Permutation property**: Result is a permutation of input. -/
def permutation_prop (xs : List Nat) : Prop := quickSort xs (by simp) ~ xs

/-- **Permutation theorem**: Result is a permutation of input. -/
@[simp] theorem permutation_thm (xs : List Nat) : permutation_prop xs := by
  sorry

/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (xs : List Nat) : Prop := (quickSort xs (by simp)).length = xs.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := by
  sorry

/-- **Idempotent property**: Sorting twice gives same result as sorting once. -/
def idempotent_prop (xs : List Nat) : Prop :=
  quickSort (quickSort xs (by simp)) (by simp) = quickSort xs (by simp)

/-- **Idempotent theorem**: Sorting twice gives same result as sorting once. -/
@[simp] theorem idempotent_thm (xs : List Nat) : idempotent_prop xs := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def quickSort_postcond (xs : List Nat) (result : List Nat) (h_precond : quickSort_precond (xs)) : Prop :=
  -- !benchmark @start postcond
  (List.Sorted (· ≤ ·) result) ∧
  (result ~ xs) ∧
  (result.length = xs.length) ∧
  (quickSort result (by simp) = result)
  -- !benchmark @end postcond

theorem quickSort_spec_satisfied (xs : List Nat) (h_precond : quickSort_precond (xs)) :
    quickSort_postcond (xs) (quickSort (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof

end QuickSort