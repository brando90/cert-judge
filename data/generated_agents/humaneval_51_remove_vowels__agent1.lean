```lean
import Lean
import Std.Data.List.Basic

/--
  `remove_vowels` is a function that takes string and returns string without vowels.
-/
def remove_vowels (text : String) : String :=
  let vowels : List Char := ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
  let chars := text.toList
  let filtered := chars.filter (fun c => !vowels.contains c)
  String.mk filtered

/-- Test cases for `remove_vowels` -/
def remove_vowels_tests : List (String × String) := [
  ("", ""),
  ("abcdef\nghijklm", "bcdf\nghjklm"),
  ("fedcba", "fdcb"),
  ("eeeee", ""),
  ("acBAA", "cB"),
  ("EcBOO", "cB"),
  ("ybcd", "ybcd")
]

/-- Run the test cases -/
#eval remove_vowels_tests.all (fun (input, expected) => remove_vowels input == expected)

/-- Predicate to check if a character is a vowel -/
def isVowel (c : Char) : Bool :=
  let lc := c.toLower
  ['a', 'e', 'i', 'o', 'u'].contains lc

/-- Specification for `remove_vowels` -/
def remove_vowels_spec (text : String) : String :=
  let chars := text.toList
  let filtered := chars.filter (fun c => !isVowel c)
  String.mk filtered

/-- Lemma: `remove_vowels` satisfies its specification -/
theorem remove_vowels_correct (text : String) : 
  remove_vowels text = remove_vowels_spec text := by
  sorry
```
