-- !benchmark @start import type=solution
import Mathlib
namespace BinarySearch
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def binarySearch_precond (arr : List Nat) (target : Nat) : Prop :=
  -- !benchmark @start precond
  List.Sorted (· ≤ ·) arr
  -- !benchmark @end precond

-- !benchmark @start code_aux
open List

/-- Binary search implementation using recursive approach with bounds -/
partial def binarySearchAux (arr : List Nat) (target : Nat) (left right : Nat) : Option Nat :=
  if left > right then
    none
  else
    let mid := (left + right) / 2
    if mid >= arr.length then
      none
    else
      let midVal := arr[mid]!
      if midVal = target then
        some mid
      else if midVal < target then
        binarySearchAux arr target (mid + 1) right
      else
        if mid = 0 then none else binarySearchAux arr target left (mid - 1)

/-- Linear search for comparison and verification -/
def linearSearch (arr : List Nat) (target : Nat) : Option Nat :=
  arr.findIdx? (· = target)
-- !benchmark @end code_aux

def binarySearch (arr : List Nat) (target : Nat) (h_precond : binarySearch_precond (arr) (target)) : Option Nat :=
  -- !benchmark @start code
  if arr.isEmpty then
    none
  else
    binarySearchAux arr target 0 (arr.length - 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Found element property**: If found, the index points to the target. -/
def found_element_prop (arr : List Nat) (target : Nat) : Prop :=
  ∀ idx, binarySearch (arr) (target) (by sorry) = some idx → arr.get? idx = some target

/-- **Found element theorem**: If found, the index points to the target. -/
@[simp] theorem found_element_thm (arr : List Nat) (target : Nat) : found_element_prop arr target := by
  sorry

/-- **Not found property**: If not found, target is not in array. -/
def not_found_prop (arr : List Nat) (target : Nat) : Prop :=
  binarySearch (arr) (target) (by sorry) = none → target ∉ arr

/-- **Not found theorem**: If not found, target is not in array. -/
@[simp] theorem not_found_thm (arr : List Nat) (target : Nat) : not_found_prop arr target := by
  sorry

/-- **Index bounds property**: Returned index is within array bounds. -/
def index_bounds_prop (arr : List Nat) (target : Nat) : Prop :=
  ∀ idx, binarySearch (arr) (target) (by sorry) = some idx → idx < arr.length

/-- **Index bounds theorem**: Returned index is within array bounds. -/
@[simp] theorem index_bounds_thm (arr : List Nat) (target : Nat) : index_bounds_prop arr target := by
  sorry

/-- **Linear search equivalence property**: Binary search equivalent to linear search on sorted arrays. -/
def linear_equivalence_prop (arr : List Nat) (target : Nat) : Prop :=
  List.Sorted (· ≤ ·) arr →
    (binarySearch (arr) (target) (by sorry)).isSome ↔ (linearSearch arr target).isSome

/-- **Linear search equivalence theorem**: Binary search equivalent to linear search on sorted arrays. -/
@[simp] theorem linear_equivalence_thm (arr : List Nat) (target : Nat) : linear_equivalence_prop arr target := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def binarySearch_postcond (arr : List Nat) (target : Nat) (result : Option Nat)
    (h_precond : binarySearch_precond (arr) (target)) : Prop :=
  -- !benchmark @start postcond
  (found_element_prop arr target) ∧
  (not_found_prop arr target) ∧
  (index_bounds_prop arr target) ∧
  (linear_equivalence_prop arr target)
  -- !benchmark @end postcond

theorem binarySearch_spec_satisfied (arr : List Nat) (target : Nat)
    (h_precond : binarySearch_precond (arr) (target)) :
    binarySearch_postcond (arr) (target) (binarySearch (arr) (target) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof