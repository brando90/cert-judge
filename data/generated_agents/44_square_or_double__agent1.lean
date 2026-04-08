import Lean.Data.RBMap
import Std.Data.RBMap

/-- Square or double a number based on parity.
    If n is even return n^2 else return 2*n, for integer n. -/
def square_or_double (n : Int) : Int :=
  if n % 2 == 0 then n * n else 2 * n

/-- Precondition for square_or_double: input must be an integer.
    This is always satisfied in Lean's type system. -/
def pre (n : Int) : Prop := True

/-- Postcondition for square_or_double: 
    if n is even, result is n^2, otherwise result is 2*n. -/
def post (n : Int) (result : Int) : Prop :=
  if n % 2 == 0 then result = n * n else result = 2 * n

/-- Square or double function preserves the postcondition. -/
theorem square_or_double_correct (n : Int) (h : pre n) : 
  post n (square_or_double n) := by
  unfold post square_or_double
  split <;> simp
  sorry

/-- Test cases for square_or_double -/
def test_square_or_double : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {square_or_double 4 == 16}"
  
  -- Edge case
  IO.println s!"Test 2: {square_or_double 0 == 0}"
  
  -- Odd number test
  IO.println s!"Test 3: {square_or_double 5 == 10}"
  
  -- Negative number test
  IO.println s!"Test 4: {square_or_double (-3) == -6}"

#eval test_square_or_double
