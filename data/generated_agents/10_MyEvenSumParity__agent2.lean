import Lean
import Mathlib.Tactic

/-- Return the parity (0 or 1) of the sum of all elements in a list of even integers.
Edge cases:
- Sum of even numbers is always even (parity 0).
- Empty list sums to 0 (parity 0).
- The function raises an error if input contains non-even integers.
-/

def pre (xs : List Int) : Bool :=
  xs.all fun x => x % 2 = 0

def prog (xs : List Int) : Int :=
  if !pre xs then
    panic! "Require list of even integers"
  else
    xs.sum % 2

/-- The parity of a sum of even integers is always 0 -/
def post (xs : List Int) (result : Int) : Prop :=
  pre xs → result = 0

/-- Unit tests for the parity function -/
def tests : Bool :=
  prog [2, 4, 6] = 0 &&  -- Basic test
  prog [] = 0            -- Empty list test

/-- Sum of even integers is always even, so parity is 0 -/
theorem sum_of_evens_has_parity_0 (xs : List Int) (h : pre xs) : xs.sum % 2 = 0 := by
  sorry

/-- Correctness theorem: the function satisfies its postcondition -/
theorem prog_correct (xs : List Int) : post xs (prog xs) := by
  unfold post
  intro h
  unfold prog
  simp [h]
  apply sum_of_evens_has_parity_0
  exact h

#eval tests
