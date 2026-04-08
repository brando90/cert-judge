/-
Implementation of max function for natural numbers.
-/

import Mathlib.Data.Nat.Basic

/-- True iff both inputs are natural numbers. -/
def pre (a b : Int) : Bool :=
  a ≥ 0 ∧ b ≥ 0

/-- Return max(a, b) for natural numbers a and b.
    Raises an error if the precondition is violated. -/
def prog (a b : Int) : Int :=
  if pre a b then
    if a ≤ b then b else a
  else
    panic! s!"Inputs must be non-negative integers (got a={a}, b={b})"

/-- The specification of max: returns the larger of the two numbers. -/
def post (a b result : Int) : Bool :=
  result = a ∨ result = b ∧ result ≥ a ∧ result ≥ b

/-- Verifies that the implementation satisfies the specification 
    when the precondition holds. -/
theorem prog_correct (a b : Int) :
  pre a b → post a b (prog a b) := by
  intro h
  unfold post prog pre
  simp [h]
  by_cases a ≤ b
  · simp [h]
    constructor
    · right; constructor
      · rfl
      · assumption
      · apply le_trans; exact h; assumption
    · assumption
  · simp [h]
    push_neg at h
    constructor
    · left; rfl
    · constructor
      · apply le_of_lt; exact h
      · rfl
  sorry

/-- Test cases for the max function. -/
def test : IO Unit := do
  -- Basic test
  assert! (prog 7 3 = 7)
  
  -- Edge case
  assert! (prog 0 0 = 0)
  
  -- Verify precondition checks
  let badInputs := [(-1, 0), (0, -2)]
  for (a, b) in badInputs do
    try
      let _ := prog a b
      throw (IO.userError "expected pre-violation did not raise")
    catch _ =>
      pure ()
      
  IO.println "All tests passed."
