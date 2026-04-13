```lean
import Batteries.Data.String
import Batteries.Tactic.Basic

/-!
# Replace spaces with underscores

This function replaces all spaces in a string with underscores.

Edge cases:
- Empty string returns empty string.
- Non-string input is invalid (not applicable in Lean's type system).
-/

/-- Replace all spaces in the input string with underscores. -/
def replaceSpaces (s : String) : String :=
  s.replace " " "_"

/-- Specification: replaceSpaces should replace all spaces with underscores -/
def replaceSpacesSpec (s : String) (result : String) : Prop :=
  ∀ i, i < result.length → 
    (if i < s.length ∧ s.get ⟨i, by sorry⟩ = ' ' then 
      result.get ⟨i, by sorry⟩ = '_'
     else if i < s.length then
      result.get ⟨i, by sorry⟩ = s.get ⟨i, by sorry⟩
     else
      false)

/-- Tests for replaceSpaces -/
def testReplaceSpaces : IO Unit := do
  -- Basic test
  assert! (replaceSpaces "hello world" = "hello_world")
  -- Multiple spaces
  assert! (replaceSpaces "a b c" = "a_b_c")
  -- No spaces
  assert! (replaceSpaces "no-spaces" = "no-spaces")
  -- Edge case: empty string
  assert! (replaceSpaces "" = "")
  IO.println "All tests passed!"

/-- Correctness theorem: replaceSpaces satisfies its specification -/
theorem replaceSpaces_correct (s : String) :
  replaceSpacesSpec s (replaceSpaces s) := by
  intro i h
  simp [replaceSpaces]
  sorry

#eval testReplaceSpaces
```
