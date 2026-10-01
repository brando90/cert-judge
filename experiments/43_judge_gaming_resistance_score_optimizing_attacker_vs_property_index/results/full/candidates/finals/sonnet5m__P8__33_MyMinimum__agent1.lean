import Mathlib
import Mathlib.Tactic.Have

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

theorem foldl_min_props (a : Nat) (ys : List Nat) :
    (∀ z ∈ a :: ys, List.foldl min a ys ≤ z) ∧
      List.foldl min a ys ∈ a :: ys := by sorry

theorem my_min_list_spec (xs : List Nat) (h : pre xs) :
    post xs (my_min_list xs) := by
  cases xs with
  | nil =>
      simp [pre] at h
  | cons x xs =>
      simpa [my_min_list, post] using (foldl_min_props x xs)

theorem post_unique {xs : List Nat} {a b : Nat}
    (ha : post xs a) (hb : post xs b) : a = b := by
  rcases ha with ⟨ha_lower, ha_mem⟩
  rcases hb with ⟨hb_lower, hb_mem⟩
  exact Nat.le_antisymm (ha_lower b hb_mem) (hb_lower a ha_mem)

theorem pre_iff_nonempty (xs : List Nat) : pre xs ↔ xs ≠ [] :=
  Iff.rfl

theorem my_min_list_singleton (x : Nat) : my_min_list [x] = x := by
  simp [my_min_list]

example : my_min_list [7, 3, 9, 2] = 2 := by decide
example : my_min_list [5] = 5 := by decide
example : my_min_list [4, 2, 2, 3] = 2 := by decide
example : my_min_list [100, 42, 99, 101] = 42 := by decide

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
