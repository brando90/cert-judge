import Mathlib.Data.Int.Basic
import Std

namespace VeriBench.SquareOrDouble

/-!
# Square or Double

If n is even return n^2 else return 2n, for integer n.

Edge cases:
- Works for zero.
- Non-integer inputs are invalid and raise ValueError.
-/

/-- Return n squared if n is even, otherwise return 2 times n. -/
def squareOrDouble (n : Int) : Int :=
  if n % 2 = 0 then n * n else 2 * n

/-- Precondition: n must be an integer. Since our function signature requires an Int,
    this is always satisfied in Lean. -/
def pre (_n : Int) : Prop := True

/-- Postcondition: If n is even, result is n^2; otherwise result is 2*n. -/
def post (n : Int) (result : Int) : Prop :=
  if n % 2 = 0 then result = n * n else result = 2 * n

/-- The function satisfies its postcondition when the precondition is met. -/
theorem squareOrDouble_correct (n : Int) (h : pre n) : post n (squareOrDouble n) := by
  unfold squareOrDouble
  unfold post
  simp
  sorry

/-- Test cases for the squareOrDouble function -/
def tests : List (Int × Int) := [
  (4, 16),   -- Basic case for even number
  (5, 10),   -- Basic case for odd number
  (0, 0)     -- Edge case: zero
]

/-- Verify that all test cases pass -/
example : tests.all (fun (input, expected) => squareOrDouble input = expected) := by
  simp [tests, squareOrDouble]
  decide

end VeriBench.SquareOrDouble
