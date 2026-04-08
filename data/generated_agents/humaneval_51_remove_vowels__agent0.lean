```lean
import Lean.Data.HashMap

def removeVowels (text : String) : String :=
  let vowels := #['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
  let chars := text.toList.filter (fun c => !vowels.contains c)
  String.mk chars

def isVowel (c : Char) : Bool :=
  let lowerC := c.toLower
  lowerC == 'a' || lowerC == 'e' || lowerC == 'i' || lowerC == 'o' || lowerC == 'u'

/-- `removeVowels` removes all vowels from a string. -/
theorem removeVowels_spec (text : String) : 
  removeVowels text = String.mk (text.toList.filter (fun c => !isVowel c)) := by
  sorry

/-- Tests for `removeVowels` -/
def removeVowels_tests : List (String × String) := [
  ("", ""),
  ("abcdef\nghijklm", "bcdf\nghjklm"),
  ("fedcba", "fdcb"),
  ("eeeee", ""),
  ("acBAA", "cB"),
  ("EcBOO", "cB"),
  ("ybcd", "ybcd")
]

/-- Run the tests for `removeVowels` -/
def testRemoveVowels : IO Unit := do
  for (input, expected) in removeVowels_tests do
    let result := removeVowels input
    if result != expected then
      throw (IO.userError s!"Test failed for input '{input}': expected '{expected}', got '{result}'")
  IO.println "All tests passed!"

#eval testRemoveVowels
```
