import Lean
import Mathlib.Tactic

/-!
# Remove Digits from String

Remove all digit characters from a string.
-/

namespace RemoveDigits

/-- Check if a character is a digit -/
def isDigit (c : Char) : Bool :=
  '0' ≤ c ∧ c ≤ '9'

/-- Remove all digit characters from a string -/
def removeDigits (s : String) : String :=
  s.iter "" fun acc c => if isDigit c then acc else acc.push c

/-- Precondition: Input must be a string -/
def pre (s : String) : Prop := True

/-- Postcondition: Output string contains no digits -/
def post (s : String) (result : String) : Prop :=
  ∀ c, c ∈ result.data → ¬isDigit c

/-- Test cases for removeDigits -/
def tests : List (String × String) := [
  ("abc123def", "abcdef"),
  ("no numbers", "no numbers"),
  ("123", ""),
  ("", "")
]

/-- Run tests for removeDigits -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := removeDigits input
    if result != expected then
      throw (IO.userError s!"Test failed for input '{input}': expected '{expected}', got '{result}'")
  IO.println "All tests passed!"

/-- Correctness theorem: removeDigits satisfies its postcondition -/
theorem removeDigits_correct (s : String) (h : pre s) : post s (removeDigits s) := by
  intro c hc
  unfold removeDigits at hc
  simp [isDigit]
  sorry

end RemoveDigits
