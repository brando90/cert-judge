import Lean

namespace CountDistinctCharacters

/--
Given a string, find out how many distinct characters (regardless of case) does it consist of.
-/
def countDistinctCharacters (s : String) : Nat :=
  let lowerStr := s.toLower
  let chars := lowerStr.toList
  let uniqueChars := chars.eraseDups
  uniqueChars.length

/-- Specification for countDistinctCharacters -/
def countDistinctCharactersSpec (s : String) : Nat :=
  let lowerStr := s.toLower
  let chars := lowerStr.data
  let uniqueChars := List.eraseDups chars
  uniqueChars.length

/-- Precondition for countDistinctCharacters -/
def countDistinctCharactersPre (s : String) : Prop := True

/-- Postcondition for countDistinctCharacters -/
def countDistinctCharactersPost (s : String) (result : Nat) : Prop :=
  result = countDistinctCharactersSpec s

/-- Correctness theorem for countDistinctCharacters -/
theorem countDistinctCharactersCorrect (s : String) 
  (h : countDistinctCharactersPre s) : 
  countDistinctCharactersPost s (countDistinctCharacters s) := by
  unfold countDistinctCharactersPost
  unfold countDistinctCharactersSpec
  unfold countDistinctCharacters
  sorry

/-- Test suite -/
def tests : List (String × Nat) := [
  ("", 0),
  ("abcde", 5),
  ("abcdecadeCADE", 5),
  ("aaaaAAAAaaaa", 1),
  ("Jerry jERRY JeRRRY", 5),
  ("xyzXYZ", 3),
  ("Jerry", 4)
]

/-- Run the test suite -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := countDistinctCharacters input
    if result != expected then
      throw (IO.userError s!"Test failed for input {input}: expected {expected}, got {result}")
    else
      IO.println s!"Test passed for input {input}"

end CountDistinctCharacters
