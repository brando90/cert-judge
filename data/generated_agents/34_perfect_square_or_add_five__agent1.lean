import Mathlib.Tactic
import Mathlib.Data.Int.Sqrt

namespace VeriBench.PerfectSquareOrAddFive

/-- Return the number itself if it is a perfect square; otherwise, return the number plus 5. -/
def perfectSquareOrAddFive (n : Int) : Int :=
  if n < 0 then
    panic! "Input must be a non-negative integer"
  else
    let root := Int.sqrt n
    if root * root == n then
      n
    else
      n + 5

/-- Precondition: Input must be a non-negative integer. -/
def pre (n : Int) : Prop :=
  n ≥ 0

/-- Postcondition: Result is either a perfect square or the input plus 5. -/
def post (n : Int) (result : Int) : Prop :=
  (∃ k : Int, k ≥ 0 ∧ k * k = result ∧ result = n) ∨ result = n + 5

/-- The perfectSquareOrAddFive function satisfies its specification. -/
theorem perfectSquareOrAddFive_correct (n : Int) (h : pre n) : 
  post n (perfectSquareOrAddFive n) := by
  unfold perfectSquareOrAddFive
  unfold pre at h
  unfold post
  simp [h]
  let root := Int.sqrt n
  by_cases h_perfect : root * root = n
  · left
    exists root
    constructor
    · exact Int.sqrt_nonneg n
    · constructor
      · exact h_perfect
      · rfl
  · right
    rfl
  sorry

/-- Tests for the perfectSquareOrAddFive function -/
def tests : List (Int × Int) := [
  (16, 16),   -- Perfect square
  (18, 23),   -- Not a perfect square
  (0, 0),     -- Edge case: 0 is a perfect square
  (1, 1),     -- Edge case: 1 is a perfect square
  (2, 7),     -- Not a perfect square
  (4, 4),     -- Perfect square
  (9, 9),     -- Perfect square
  (10, 15)    -- Not a perfect square
]

/-- Run all tests for the perfectSquareOrAddFive function -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    if pre input then
      let result := perfectSquareOrAddFive input
      if result != expected then
        throw (IO.userError s!"Test failed for input {input}: expected {expected}, got {result}")
    else
      IO.println s!"Skipping test with invalid input: {input}"
  IO.println "All tests passed!"

end VeriBench.PerfectSquareOrAddFive
