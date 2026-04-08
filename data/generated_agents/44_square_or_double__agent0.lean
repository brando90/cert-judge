import Lean
import Mathlib.Data.Int.Basic

/-- Return n squared if n is even, otherwise return 2 times n. -/
def square_or_double (n : Int) : Int :=
  if n % 2 = 0 then n * n else 2 * n

/-- The precondition is that n is an integer, which is always true in Lean's type system. -/
def pre (n : Int) : Prop := True

/-- The postcondition states that the result is n^2 if n is even, otherwise 2n. -/
def post (n : Int) (result : Int) : Prop :=
  if n % 2 = 0 then result = n * n else result = 2 * n

theorem square_or_double_correct (n : Int) (h : pre n) :
  post n (square_or_double n) := by
  unfold pre post square_or_double
  split <;> simp
  sorry

/-- Test cases for square_or_double -/
def test_square_or_double : IO Unit := do
  -- Basic test
  if square_or_double 4 ≠ 16 then
    throw (IO.userError "Failed: square_or_double 4 should be 16")
  
  -- Edge case: zero
  if square_or_double 0 ≠ 0 then
    throw (IO.userError "Failed: square_or_double 0 should be 0")
  
  -- Odd number
  if square_or_double 5 ≠ 10 then
    throw (IO.userError "Failed: square_or_double 5 should be 10")
  
  -- Negative number
  if square_or_double (-3) ≠ -6 then
    throw (IO.userError "Failed: square_or_double -3 should be -6")

  IO.println "All tests passed."

#eval test_square_or_double
