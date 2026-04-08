import Mathlib.Data.String.Basic
import Mathlib.Data.Finset.Basic

/-- Given a string, find out how many distinct characters (regardless of case) does it consist of. -/
def countDistinctCharacters (s : String) : Nat :=
  (s.toLower.toList.toFinset).card

/-- Tests for countDistinctCharacters function -/
def countDistinctCharactersTests : List (String × Nat) :=
  [
    ("", 0),
    ("abcde", 5),
    ("abcde" ++ "cade" ++ "CADE", 5),
    ("aaaaAAAAaaaa", 1),
    ("Jerry jERRY JeRRRY", 5),
    ("xyzXYZ", 3),
    ("Jerry", 4)
  ]

/-- Run the tests for countDistinctCharacters function -/
#eval countDistinctCharactersTests.all (fun (input, expected) => countDistinctCharacters input == expected)

/-- Precondition for countDistinctCharacters: none, it works for any string -/
def countDistinctCharactersPre (s : String) : Prop := True

/-- Postcondition for countDistinctCharacters: 
    The result is the number of distinct characters in the string, ignoring case -/
def countDistinctCharactersPost (s : String) (result : Nat) : Prop :=
  result = (s.toLower.toList.toFinset).card

/-- Theorem: countDistinctCharacters satisfies its specification -/
theorem countDistinctCharactersCorrect (s : String) :
  countDistinctCharactersPre s → countDistinctCharactersPost s (countDistinctCharacters s) := by
  intro h
  unfold countDistinctCharactersPost
  unfold countDistinctCharacters
  sorry
