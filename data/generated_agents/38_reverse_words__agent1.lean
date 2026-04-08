import VeriBench.Common
import Lean.Data.HashMap

namespace VeriBench.ReverseWords

def reverseString (s : String) : String :=
  String.mk (s.toList.reverse)

/-- Reverse each word in the string but preserve word order. -/
def reverseWords (s : String) : String :=
  String.join (List.intersperse " " ((s.split (· == ' ')).map reverseString))

/-!
## Tests
-/

def test1 : reverseWords "hello world" = "olleh dlrow" := by
  simp [reverseWords, reverseString]

def test2 : reverseWords "lean is great" = "nael si taerg" := by
  simp [reverseWords, reverseString]

def test3 : reverseWords "" = "" := by
  simp [reverseWords, reverseString]

/-!
## Specification and Correctness
-/

/-- Precondition: The input must be a string. -/
def pre (s : String) : Prop := True

/-- Postcondition: Each word in the input string is reversed, but word order is preserved. -/
def post (s : String) (result : String) : Prop :=
  let inputWords := s.split (· == ' ')
  let outputWords := result.split (· == ' ')
  inputWords.length = outputWords.length ∧
  List.zipWith (fun w1 w2 => w1 = reverseString w2) inputWords outputWords |>.all id

/-- The reverseWords function satisfies its specification. -/
theorem reverseWords_correct (s : String) (h : pre s) : post s (reverseWords s) := by
  sorry

end VeriBench.ReverseWords
