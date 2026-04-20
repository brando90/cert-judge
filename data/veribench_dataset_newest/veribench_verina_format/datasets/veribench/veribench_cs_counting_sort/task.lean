-- !benchmark @start import type=solution
import Mathlib
namespace CountingSort
-- !benchmark @end import

-- !benchmark @start solution_aux
open List
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def countingSort_precond (l : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Find the maximum element in a non-empty list -/
def findMax : List Nat → Nat
  | [] => 0
  | [x] => x
  | x :: xs => max x (findMax xs)

/-- Count occurrences of each number from 0 to max_val -/
def countOccurrences (l : List Nat) (max_val : Nat) : List Nat :=
  (range (max_val + 1)).map (fun i => l.count i)

/-- Build sorted list from count array -/
def buildSorted : List Nat → Nat → List Nat
  | [], _ => []
  | count :: counts, i =>
    (replicate count i) ++ buildSorted counts (i + 1)
-- !benchmark @end code_aux

/-- Sorts a list using the counting sort algorithm. -/
def countingSort (l : List Nat) (h_precond : countingSort_precond (l)) : List Nat :=
  -- !benchmark @start code
  if l.isEmpty then
    []
  else
    let max_val := findMax l
    let counts := countOccurrences l max_val
    buildSorted counts 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def countingSort_postcond (l : List Nat) (result : List Nat) (h_precond : countingSort_precond (l)) : Prop :=
  -- !benchmark @start postcond
  List.Sorted (fun x y => x ≤ y) result ∧ result ~ l ∧ result.length = l.length ∧ (countingSort ([]) (by simp) = [])
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem length_countingSort (l : List Nat) :
  (countingSort l (by simp)).length = l.length := by
  sorry

theorem sorted_countingSort (l : List Nat) :
  List.Sorted (fun x y => x ≤ y) (countingSort l (by simp)) := by
  sorry

theorem perm_countingSort (l : List Nat) :
    countingSort l (by simp) ~ l := by
  sorry

theorem idempotent_countingSort (l : List Nat) :
    countingSort (countingSort l (by simp)) (by simp) = countingSort l (by simp) := by
  sorry

def sorted_prop (xs : List Nat) : Prop :=
  List.Sorted (· ≤ ·) (countingSort xs (by simp))

theorem sorted_thm (xs : List Nat) : sorted_prop xs := by
  sorry

def permutation_prop (xs : List Nat) : Prop :=
  List.Perm xs (countingSort xs (by simp))

theorem permutation_thm (xs : List Nat) : permutation_prop xs := by
  sorry

def length_preservation_prop (xs : List Nat) : Prop :=
  (countingSort xs (by simp)).length = xs.length

theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := by
  sorry

def empty_list_prop : Prop :=
  countingSort [] (by simp) = []

theorem empty_list_thm : empty_list_prop := by
  sorry
-- !benchmark @end proof_aux

theorem countingSort_spec_satisfied (l : List Nat) (h_precond : countingSort_precond (l)) :
    countingSort_postcond (l) (countingSort (l) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof
end CountingSort