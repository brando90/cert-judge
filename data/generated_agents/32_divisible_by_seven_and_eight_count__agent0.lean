import Lean
import Std.Data.List.Basic

def isDivisibleBy (n m : Int) : Bool :=
  n % m == 0

/-- 
Count numbers divisible by both 7 and 8 in a list of integers.

Edge cases:
- Empty list returns 0.
-/
def countDivBy7And8 (xs : List Int) : Nat :=
  xs.foldl (fun count x => if isDivisibleBy x 7 && isDivisibleBy x 8 then count + 1 else count) 0

/-- Precondition: input must be a list of integers -/
def pre (xs : List Int) : Prop := True

/-- Postcondition: output is the count of elements divisible by both 7 and 8 -/
def post (xs : List Int) (result : Nat) : Prop :=
  result = xs.filter (fun x => isDivisibleBy x 7 && isDivisibleBy x 8) |>.length

/-- Correctness theorem for countDivBy7And8 -/
theorem countDivBy7And8_correct (xs : List Int) :
  pre xs → post xs (countDivBy7And8 xs) := by
  intro _
  unfold post
  unfold countDivBy7And8
  sorry

/-- Tests for countDivBy7And8 -/
def tests : IO Unit := do
  -- Basic test
  assert! (countDivBy7And8 [56, 14, 28, 112] = 2)
  -- No elements divisible by both
  assert! (countDivBy7And8 [1, 2, 3, 4] = 0)
  -- With zero (divisible by both)
  assert! (countDivBy7And8 [0, 56, 84] = 2)
  -- Empty list
  assert! (countDivBy7And8 [] = 0)
  IO.println "All tests passed!"

#eval tests
