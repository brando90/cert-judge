```lean
import Lean
import Batteries.Data.List.Basic

/-!
# VeriBench: Human Eval Problem 51 - Remove Vowels
-/

/-- `removeVowels` is a function that takes string and returns string without vowels. -/
def removeVowels (text : String) : String :=
  let vowels := ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
  text.toList.filter (fun c => !vowels.contains c) |> String.mk

/-- Specification for `removeVowels` -/
def removeVowelsSpec (text : String) : String :=
  let vowels := ['a', 'e', 'i', 'o', 'u']
  text.toList.filter (fun c => !vowels.contains c.toLower) |> String.mk

/-- Tests for `removeVowels` -/
def removeVowelsTests : List (String × String) := [
  ("", ""),
  ("abcdef\nghijklm", "bcdf\nghjklm"),
  ("fedcba", "fdcb"),
  ("eeeee", ""),
  ("acBAA", "cB"),
  ("EcBOO", "cB"),
  ("ybcd", "ybcd")
]

/-- Run the tests -/
#eval removeVowelsTests.all (fun (input, expected) => removeVowels input == expected)

/-- Precondition for `removeVowels` -/
def removeVowelsPre (_text : String) : Prop := True

/-- Postcondition for `removeVowels` -/
def removeVowelsPost (text : String) (result : String) : Prop :=
  result = removeVowelsSpec text

/-- Correctness theorem for `removeVowels` -/
theorem removeVowels_correct (text : String) :
  removeVowelsPre text → removeVowelsPost text (removeVowels text) := by
  intro _
  unfold removeVowelsPost
  unfold removeVowelsSpec
  unfold removeVowels
  sorry
```
