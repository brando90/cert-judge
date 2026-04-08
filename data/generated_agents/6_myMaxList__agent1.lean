```lean
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

namespace VB.MaxOfList

/-- True iff xs is a non-empty list of non-negative integers. -/
def pre (xs : List Nat) : Prop :=
  xs.length > 0

/-- Return max(xs) for a non-empty list of non‑negative integers.
    Raises error if the precondition is violated. -/
def prog (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | x :: xs => xs.foldl max x

/-- Tests for the prog function -/
def tests : IO Unit := do
  -- Basic unit test
  assert! (prog [7, 3, 9, 2] = 9)

  -- Edge unit test
  assert! (prog [5] = 5)

  -- Additional tests
  assert! (prog [1, 2, 3, 4] = 4)
  assert! (prog [5, 5, 5] = 5)
  assert! (prog [10, 9, 8, 7, 6] = 10)
  
  IO.println "All tests passed."

/-- Specification: Returns the maximum element in a non-empty list -/
def post (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, x ≤ result

/-- The main correctness theorem: prog satisfies post when pre holds -/
theorem prog_correct (xs : List Nat) (h : pre xs) : post xs (prog xs) := by
  sorry

/-- Helper lemma: prog preserves the invariant that result is always in the list -/
lemma prog_element_of (xs : List Nat) (h : xs.length > 0) : prog xs ∈ xs := by
  sorry

/-- Helper lemma: prog returns a value that is greater than or equal to all elements -/
lemma prog_max (xs : List Nat) (h : xs.length > 0) : ∀ x ∈ xs, x ≤ prog xs := by
  sorry

end VB.MaxOfList
```
