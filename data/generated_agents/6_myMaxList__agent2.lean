import Lean.Data.HashMap
import Mathlib.Tactic.LibrarySearch
import Mathlib.Data.List.Basic

/-
Return the largest element in a non-empty list of natural numbers.

Edge cases:
- Single element list returns that element.
- The function raises ValueError if the list is empty or contains non-natural numbers.
-/

def pre (xs : List Nat) : Bool :=
  xs.length > 0

def prog (xs : List Nat) : Option Nat :=
  if pre xs then
    some (xs.foldl (fun acc x => max acc x) xs.head!)
  else
    none

-- Tests

#eval prog [7, 3, 9, 2] -- some 9
#eval prog [5] -- some 5
#eval prog ([] : List Nat) -- none

-- Specification

def post (xs : List Nat) (result : Nat) : Prop :=
  xs.length > 0 → ∀ x ∈ xs, x ≤ result ∧ result ∈ xs

-- Correctness theorem

theorem prog_correct (xs : List Nat) :
  pre xs → 
  match prog xs with
  | some result => post xs result
  | none => ¬ pre xs
  := by
    intro h
    simp [prog, pre, h]
    intro x_in_xs
    have h_max : ∀ (y : Nat), y ∈ xs → y ≤ xs.foldl (fun acc x => max acc x) xs.head! := by sorry
    have h_in : xs.foldl (fun acc x => max acc x) xs.head! ∈ xs := by sorry
    exact ⟨h_max, h_in⟩
    sorry
