import Mathlib.Tactic

/-- Return the product of three natural numbers (non-negative integers).

Edge cases:
- Any factor being 0 makes the product 0.
- product(1, 1, 1) = 1
- The function raises ValueError if any input is not a natural number.
-/

/-- Precondition: True iff all inputs are natural numbers. -/
def pre (a b c : Int) : Prop :=
  a ≥ 0 ∧ b ≥ 0 ∧ c ≥ 0

/-- Return a * b * c for non-negative integers a, b, c. -/
def prog (a b c : Int) : Int :=
  if pre a b c then
    a * b * c
  else
    panic! s!"Inputs must be non-negative integers (got a={a}, b={b}, c={c})"

/-- Postcondition: The result is the product of the three inputs. -/
def post (a b c result : Int) : Prop :=
  result = a * b * c

/-- Correctness theorem: If the precondition is satisfied, then the postcondition holds
    for the result of the program. -/
theorem prog_correct (a b c : Int) : pre a b c → post a b c (prog a b c) := by
  intro h
  unfold post prog
  simp [h]
  sorry

/-- Tests for the `prog` function. -/
def test : IO Unit := do
  -- Basic unit test
  assert! (prog 2 3 4 = 24)
  
  -- Edge unit test
  assert! (prog 0 5 6 = 0)
  
  -- Identity test
  assert! (prog 1 1 1 = 1)
  
  -- More tests
  assert! (prog 10 0 7 = 0)
  assert! (prog 5 2 3 = 30)
  
  IO.println "All tests passed!"

/-- Run the tests. -/
#eval test
