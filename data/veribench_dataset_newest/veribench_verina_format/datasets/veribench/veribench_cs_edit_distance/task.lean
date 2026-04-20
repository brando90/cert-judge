-- !benchmark @start import type=solution
import Mathlib
namespace EditDistance
-- !benchmark @end import

-- !benchmark @start solution_aux
open List
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def editDistance_precond {α : Type*} (s1 : List α) (s2 : List α) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Compute the minimum of three natural numbers -/
def min3 (a b c : Nat) : Nat :=
  min (min a b) c

/-- Helper function to compute edit distance using dynamic programming. -/
def editDistanceAux {α : Type*} [DecidableEq α] : List α → List α → Nat
  | [], [] => 0
  | [], ys => ys.length
  | xs, [] => xs.length
  | x :: xs, y :: ys =>
    if x = y then
      editDistanceAux xs ys
    else
      1 + min3
        (editDistanceAux xs (y :: ys))
        (editDistanceAux (x :: xs) ys)
        (editDistanceAux xs ys)
-- !benchmark @end code_aux

def editDistance {α : Type*} [DecidableEq α] (s1 : List α) (s2 : List α)
    (h_precond : editDistance_precond (s1) (s2)) : Nat :=
  -- !benchmark @start code
  editDistanceAux s1 s2
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def editDistance_postcond {α : Type*} [DecidableEq α] (s1 : List α) (s2 : List α)
    (result : Nat) (h_precond : editDistance_precond (s1) (s2)) : Prop :=
  -- !benchmark @start postcond
  (reflexivity_prop (s := s1)) ∧
  (symmetry_prop (s1 := s1) (s2 := s2)) ∧
  (empty_list_prop (s := s1)) ∧
  (∀ s3, triangle_inequality_prop (s1 := s1) (s2 := s2) (s3 := s3))
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Reflexivity property**: Edit distance from a list to itself is 0. -/
def reflexivity_prop {α : Type*} [DecidableEq α] (s : List α) : Prop :=
  editDistance (s1 := s) (s2 := s) (by simp) = 0

@[simp] theorem reflexivity_thm {α : Type*} [DecidableEq α] (s : List α) :
    reflexivity_prop (s := s) := by
  sorry

/-- **Symmetry property**: Edit distance is symmetric. -/
def symmetry_prop {α : Type*} [DecidableEq α] (s1 s2 : List α) : Prop :=
  editDistance (s1 := s1) (s2 := s2) (by simp) =
    editDistance (s1 := s2) (s2 := s1) (by simp)

@[simp] theorem symmetry_thm {α : Type*} [DecidableEq α] (s1 s2 : List α) :
    symmetry_prop (s1 := s1) (s2 := s2) := by
  sorry

/-- **Empty list property**: distances to/from empty list equal the other length. -/
def empty_list_prop {α : Type*} [DecidableEq α] (s : List α) : Prop :=
  editDistance (s1 := []) (s2 := s) (by simp) = s.length ∧
    editDistance (s1 := s) (s2 := []) (by simp) = s.length

@[simp] theorem empty_list_thm {α : Type*} [DecidableEq α] (s : List α) :
    empty_list_prop (s := s) := by
  sorry

/-- **Triangle inequality property**. -/
def triangle_inequality_prop {α : Type*} [DecidableEq α] (s1 s2 s3 : List α) : Prop :=
  editDistance (s1 := s1) (s2 := s3) (by simp) ≤
    editDistance (s1 := s1) (s2 := s2) (by simp) +
      editDistance (s1 := s2) (s2 := s3) (by simp)

@[simp] theorem triangle_inequality_thm {α : Type*} [DecidableEq α] (s1 s2 s3 : List α) :
    triangle_inequality_prop (s1 := s1) (s2 := s2) (s3 := s3) := by
  sorry
-- !benchmark @end proof_aux

theorem editDistance_spec_satisfied {α : Type*} [DecidableEq α] (s1 : List α) (s2 : List α)
    (h_precond : editDistance_precond (s1) (s2)) :
    editDistance_postcond (s1) (s2) (editDistance (s1) (s2) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof