import Lean.Data.HashMap
import Mathlib.Tactic.Have
import Mathlib.Tactic.LibrarySearch
import Mathlib.Tactic.Ring
import Mathlib.Data.Int.Basic

/-!
# My Min List

Return the smallest element in a non-empty list of non-negative integers.

Edge cases:
- Single-element list returns that element.
- Empty list or non-integers are invalid and raise ValueError.
-/

namespace MyMinList

def my_min_list (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | x :: xs => xs.foldl min x

/-- The precondition for `my_min_list` is that the input list is non-empty. -/
def pre (xs : List Nat) : Prop :=
  xs ≠ []

/-- The postcondition for `my_min_list` is that the returned value is the smallest element in the list. -/
def post (xs : List Nat) (result : Nat) : Prop :=
  (∀ x ∈ xs, result ≤ x) ∧ (result ∈ xs)

theorem my_min_list_spec (xs : List Nat) (h : pre xs) : post xs (my_min_list xs) := by
  unfold pre at h
  unfold post
  unfold my_min_list
  cases xs with
  | nil => contradiction
  | cons x xs' =>
    simp
    split <;> try contradiction
    sorry

/-- Test cases for my_min_list -/
def test : IO Unit := do
  -- Basic
  assert! (my_min_list [7, 3, 9, 2] = 2)
  -- Edge
  assert! (my_min_list [5] = 5)
  -- Should handle duplicates
  assert! (my_min_list [4, 2, 2, 3] = 2)
  -- Should handle larger numbers
  assert! (my_min_list [100, 42, 99, 101] = 42)
  
  IO.println "All tests passed!"

end MyMinList
