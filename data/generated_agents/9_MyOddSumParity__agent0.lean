```lean
import Std.Data.List.Basic

namespace OddSumParity

/-- Check if a number is odd -/
def isOdd (n : Int) : Bool := n % 2 = 1

/-- Precondition: xs is a non-empty list of odd integers -/
def pre (xs : List Int) : Prop := 
  xs ≠ [] ∧ ∀ x ∈ xs, isOdd x

/-- Return the parity (0 or 1) of the sum of all elements in a list of odd integers -/
def prog (xs : List Int) : Int :=
  if h : pre xs then
    (xs.foldl (· + ·) 0) % 2
  else
    panic! "Require non-empty list of odd integers"

/-- Post-condition: result is either 0 or 1 -/
def post (xs : List Int) (result : Int) : Prop :=
  result = 0 ∨ result = 1

/-- The result is 1 if and only if the list has an odd number of elements -/
theorem parity_equals_count_parity (xs : List Int) (h : pre xs) :
  prog xs = (xs.length % 2) := sorry

/-- The correctness theorem: if precondition is met, the result satisfies the post-condition -/
theorem prog_correct (xs : List Int) (h : pre xs) : 
  post xs (prog xs) := sorry

/-- Test cases -/
def test : IO Unit := do
  assert! (prog [1, 3, 5] = 1)
  assert! (prog [1] = 1)
  assert! (prog [1, 3, 5, 7] = 0)
  assert! (prog [1, 3] = 0)
  IO.println "All tests passed!"

end OddSumParity
```
