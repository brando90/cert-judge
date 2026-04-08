import Batteries
import Lean.Data.Rat
open Batteries

/-- Return the first character of a non-empty string. -/
def getFirstChar (s : String) : String := 
  if s.length > 0 then
    s.get ⟨0, by simp [s.length > 0]⟩ |>.toString
  else
    panic! "Require non-empty string"

/-- The precondition: input must be a non-empty string. -/
def pre (s : String) : Bool := 
  s.length > 0

/-- The postcondition: result is a single character string that matches the first character of input. -/
def post (s : String) (result : String) : Bool :=
  pre s → result.length = 1 ∧ s.get ⟨0, by simp [pre s]⟩ |>.toString = result

/-- Test cases for getFirstChar function -/
def tests : List (String × String) :=
  [("hello", "h"), ("A", "A")]

theorem getFirstChar_correct (s : String) : post s (getFirstChar s) := by
  intro h_pre
  unfold getFirstChar
  simp [h_pre]
  apply And.intro
  · simp [String.length_toString]
  · rfl
  sorry

/-- Run tests for getFirstChar -/
def main : IO Unit := do
  for (input, expected) in tests do
    if pre input then
      let result := getFirstChar input
      if result = expected then
        IO.println s!"Test passed: getFirstChar {input} = {result}"
      else
        IO.println s!"Test failed: getFirstChar {input} = {result}, expected {expected}"
    else
      IO.println s!"Test skipped: {input} does not satisfy precondition"
  
  -- Test precondition violation
  try
    let _ := getFirstChar ""
    IO.println "Test failed: expected exception for empty string"
  catch e =>
    IO.println "Test passed: empty string raised exception as expected"
