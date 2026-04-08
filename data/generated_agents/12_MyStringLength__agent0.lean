import Lean.Data.HashMap

namespace StringLength

/-- True iff the input is a string. -/
def pre (s : Option String) : Prop :=
  s.isSome

/-- Return the length of s.
    Raises an error if the precondition is violated. -/
def prog (s : Option String) : Nat :=
  match s with
  | some str => str.length
  | none => panic! "Require string input"

/-- Specification: The output is the length of the input string. -/
def post (s : Option String) (result : Nat) : Prop :=
  pre s → ∃ str, s = some str ∧ result = str.length

theorem prog_correct (s : Option String) : post s (prog s) := by
  unfold post
  intro h
  unfold pre at h
  unfold prog
  cases s with
  | some str =>
    exists str
    simp
  | none =>
    contradiction
  sorry

/-- Tests for the string length function -/
def tests : IO Unit := do
  -- Basic unit test
  assert! (prog (some "hello") == 5)
  
  -- Edge unit test
  assert! (prog (some "") == 0)
  
  -- Negative tests would raise runtime errors in Lean
  -- We can't directly test these in pure code

/-- Run all tests -/
def main : IO Unit :=
  tests

end StringLength
