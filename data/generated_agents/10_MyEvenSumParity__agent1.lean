import Std.Data.List.Basic

/-- Return the parity (0 or 1) of the sum of all elements in a list of even integers.

Edge cases:
- Sum of even numbers is always even (parity 0).
- Empty list sums to 0 (parity 0).
- The function raises ValueError if input contains non-even integers.
-/

namespace EvenParity

/-- Predicate that checks if a list contains only even integers -/
def pre (xs : List Int) : Prop :=
  ∀ x ∈ xs, x % 2 = 0

/-- Implementation to compute the parity of the sum of even integers -/
def prog (xs : List Int) : Option Int :=
  if h : pre xs then
    some (xs.foldl (· + ·) 0 % 2)
  else
    none

/-- Sum of even numbers always has parity 0 -/
theorem sum_even_parity_is_zero (xs : List Int) (h : pre xs) : 
    xs.foldl (· + ·) 0 % 2 = 0 := sorry

/-- Correctness theorem: the parity of a sum of even integers is always 0 -/
theorem prog_correct (xs : List Int) :
    pre xs → prog xs = some 0 := by
  intro h
  simp [prog, h]
  apply sum_even_parity_is_zero
  exact h

/-- Test cases for the function -/
def test : IO Unit := do
  -- Basic test case
  assert! (prog [2, 4, 6] = some 0)
  
  -- Edge case: empty list
  assert! (prog [] = some 0)
  
  -- Invalid inputs
  assert! (prog [1, 3, 5] = none)
  assert! (prog [2, 3, 4] = none)
  
  IO.println "All tests passed!"

end EvenParity
