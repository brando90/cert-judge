import Lean
import Std.Data.List.Basic
import Std.Data.String.Basic

namespace VeriBench.ReverseWords

def reverseString (s : String) : String :=
  s.toList.reverse.asString

def reverseWords (s : String) : String :=
  let words := s.split (· == ' ')
  String.intercalate " " (words.map reverseString)

/-- Pre-condition: `s` must be a string (always true in Lean) -/
def pre (s : String) : Prop := True

/-- Post-condition: The result has the same number of words as the input,
    and each word in the result is the reverse of the corresponding word in the input -/
def post (s : String) (result : String) : Prop :=
  let inputWords := s.split (· == ' ')
  let outputWords := result.split (· == ' ')
  inputWords.length = outputWords.length ∧
  List.zipWith (fun i o => reverseString i = o) inputWords outputWords = List.replicate inputWords.length true

theorem reverseWords_correct (s : String) (h : pre s) : post s (reverseWords s) := sorry

/-- Test cases for reverseWords -/
def testReverseWords : IO Unit := do
  -- Basic test
  assert! (reverseWords "hello world" = "olleh dlrow")
  -- Edge case
  assert! (reverseWords "" = "")
  -- Additional test
  assert! (reverseWords "lean is great" = "nael si taerg")
  IO.println "All tests passed."

end VeriBench.ReverseWords
