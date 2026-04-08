import VeriBench

namespace Remainder

/-- True iff a is a non-negative integer and b is a positive integer. -/
def pre (a b : Int) : Bool :=
  a ≥ 0 && b > 0

/-- Return the remainder when non-negative integer a is divided by positive integer b.
    
    Edge cases:
    - remainder(a, a) = 0 for any positive a
    - remainder(a, b) = a when a < b
    - The function raises ValueError if a is negative or b is not positive. -/
def prog (a b : Int) : Int :=
  if pre a b then
    a % b
  else
    panic! s!"Require a ≥ 0 and b > 0 (got a={a}, b={b})"

/-- The remainder is always non-negative and less than the divisor. -/
def post (a b : Int) (result : Int) : Bool :=
  result ≥ 0 && result < b

theorem prog_correct (a b : Int) (h : pre a b) : post a b (prog a b) := by
  simp [pre, post, prog, h]
  have h_mod := Int.mod_nonneg a (by omega)
  have h_mod_lt := Int.mod_lt a (by omega)
  exact ⟨h_mod, h_mod_lt⟩

/-- Test cases for the remainder function -/
def test : IO Unit := do
  -- Basic unit test
  VeriBench.assertEq (prog 7 3) 1
  
  -- Edge unit test
  VeriBench.assertEq (prog 3 7) 3
  
  -- Edge case: remainder(a, a) = 0 for any positive a
  VeriBench.assertEq (prog 5 5) 0
  
  -- Edge case: remainder(a, b) = a when a < b
  VeriBench.assertEq (prog 2 3) 2
  
  -- Verify that the postcondition holds for valid inputs
  VeriBench.assert (post 7 3 (prog 7 3))
  VeriBench.assert (post 3 7 (prog 3 7))
  
  -- Negative tests (pre-violations must raise errors)
  VeriBench.expectError (prog (-1) 3)
  VeriBench.expectError (prog 5 0)
  
  IO.println "All tests passed."

end Remainder
