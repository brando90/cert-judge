import VeriBench.Common
import Lean.Data.HashMap
import Mathlib.Tactic

namespace HumanEval23Strlen

/-- 
  Return length of given string
-/
def strlen (s : String) : Nat :=
  s.length

/-- Tests for strlen function -/
def tests : List (String × Nat) := [
  ("", 0),
  ("x", 1),
  ("asdasnakj", 9)
]

/-- Run tests for strlen function -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := strlen input
    if result == expected then
      IO.println s!"Test passed: strlen {repr input} = {result}"
    else
      IO.println s!"Test failed: strlen {repr input} = {result}, expected {expected}"

/-- Specification of strlen function -/
def strlenSpec (s : String) : Nat :=
  s.length

/-- Pre-condition for strlen function -/
def strlenPre (s : String) : Prop := True

/-- Post-condition for strlen function -/
def strlenPost (s : String) (result : Nat) : Prop :=
  result = s.length

/-- Correctness theorem for strlen function -/
theorem strlen_correct (s : String) (h : strlenPre s) : strlenPost s (strlen s) := by
  unfold strlenPost
  unfold strlen
  rfl

end HumanEval23Strlen
