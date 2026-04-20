-- !benchmark @start import type=solution
import Mathlib
namespace LCS
-- !benchmark @end import

open List

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def longestCommonSubsequence_precond {α : Type*} (l1 : List α) (l2 : List α) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Check if a list is a subsequence of another list -/
def isSubsequence {α : Type*} [DecidableEq α] : List α → List α → Bool
  | [], _ => true
  | _, [] => false
  | x :: xs, y :: ys =>
    if x = y then
      isSubsequence xs ys
    else
      isSubsequence (x :: xs) ys

/-- Length of LCS using dynamic programming (more efficient for length computation) -/
def lcsLength {α : Type*} [DecidableEq α] : List α → List α → Nat
  | [], _ => 0
  | _, [] => 0
  | x :: xs, y :: ys =>
    if x = y then
      1 + lcsLength xs ys
    else
      max (lcsLength (x :: xs) ys) (lcsLength xs (y :: ys))
-- !benchmark @end code_aux

def longestCommonSubsequence {α : Type*} [DecidableEq α] (l1 : List α) (l2 : List α)
    (h_precond : longestCommonSubsequence_precond (l1) (l2)) : List α :=
  -- !benchmark @start code
  match l1, l2 with
  | [], _ => []
  | _, [] => []
  | x :: xs, y :: ys =>
    if x = y then
      x :: longestCommonSubsequence xs ys (by simp [longestCommonSubsequence_precond])
    else
      let lcs1 := longestCommonSubsequence (x :: xs) ys (by simp [longestCommonSubsequence_precond])
      let lcs2 := longestCommonSubsequence xs (y :: ys) (by simp [longestCommonSubsequence_precond])
      if lcs1.length ≥ lcs2.length then lcs1 else lcs2
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def longestCommonSubsequence_postcond {α : Type*} [DecidableEq α] (l1 : List α) (l2 : List α)
    (result : List α) (h_precond : longestCommonSubsequence_precond (l1) (l2)) : Prop :=
  -- !benchmark @start postcond
  (result = longestCommonSubsequence (l1) (l2) h_precond) ∧
  (longestCommonSubsequence l1 [] (by simp [longestCommonSubsequence_precond]) = [] ∧
    longestCommonSubsequence [] l1 (by simp [longestCommonSubsequence_precond]) = []) ∧
  (let lcs := longestCommonSubsequence l1 l2 h_precond
    lcs.Sublist l1 ∧ lcs.Sublist l2) ∧
  (longestCommonSubsequence l1 l1 (by simp [longestCommonSubsequence_precond]) = l1) ∧
  (let lcs := longestCommonSubsequence l1 l2 h_precond
    lcs.length ≤ l1.length ∧ lcs.length ≤ l2.length)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem longestCommonSubsequence_spec_satisfied {α : Type*} [DecidableEq α] (l1 : List α) (l2 : List α)
    (h_precond : longestCommonSubsequence_precond (l1) (l2)) :
    longestCommonSubsequence_postcond (l1) (l2)
      (longestCommonSubsequence (l1) (l2) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof