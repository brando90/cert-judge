import Lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic

namespace AllEven

/-- Check if all elements in a list are even integers.
    Empty list returns true.
-/
def allEven (xs : List Int) : Bool :=
  match xs with
  | [] => true
  | x :: xs' => x % 2 == 0 && allEven xs'

/-- Predicate specifying that all elements in the list are even -/
def all_even_spec (xs : List Int) : Prop :=
  ∀ x ∈ xs, x % 2 = 0

/-- Precondition: input must be a list of integers.
    This is automatically satisfied in Lean's type system. -/
def pre (_xs : List Int) : Prop := True

/-- Postcondition: result is true iff all elements in the list are even -/
def post (xs : List Int) (result : Bool) : Prop :=
  result = true ↔ all_even_spec xs

theorem allEven_correct (xs : List Int) : post xs (allEven xs) := by
  unfold post
  unfold all_even_spec
  induction xs with
  | nil => 
    simp [allEven]
    constructor
    · intro _; intros x h; contradiction
    · intro _; trivial
  | cons x xs ih =>
    simp [allEven]
    cases h : x % 2 == 0
    · simp [h]
      constructor
      · intro contra; contradiction
      · intro h'
        have : x % 2 ≠ 0 := by
          simp [Bool.eq_false_iff] at h
          omega
        have : x % 2 = 0 := h' x (by simp)
        contradiction
    · simp [h]
      constructor
      · intro h'
        have : x % 2 = 0 := by
          simp [Bool.eq_true_iff] at h
          omega
        apply ih.mp
        intro y hy
        apply h'
        simp [hy]
      · intro h'
        have : x % 2 = 0 := h' x (by simp)
        have : x % 2 == 0 = true := by
          simp [Bool.eq_true_iff]
          assumption
        rw [this] at h
        apply ih.mpr
        intro y hy
        apply h'
        simp [hy]
  sorry

/-- Tests for the allEven function -/
def tests : IO Unit := do
  -- Basic test
  assert! (allEven [2, 4, 6] = true)
  
  -- Test with mixed values
  assert! (allEven [2, 4, 5, 6] = false)
  
  -- Edge case: empty list
  assert! (allEven [] = true)
  
  -- Negative numbers
  assert! (allEven [-2, -4, -6] = true)
  assert! (allEven [-1, -2, -3] = false)
  
  IO.println "All tests passed!"

end AllEven
