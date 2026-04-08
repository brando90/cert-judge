import Lean
import Std

namespace StringSequence

def string_sequence (n : Nat) : String := 
  String.intercalate " " (List.map toString (List.range (n + 1)))

def string_sequence_spec (n : Nat) : String := 
  String.intercalate " " (List.map toString (List.range (n + 1)))

theorem string_sequence_correct (n : Nat) : string_sequence n = string_sequence_spec n := by
  simp [string_sequence, string_sequence_spec]

def test_string_sequence : IO Unit := do
  assert! (string_sequence 0 == "0")
  assert! (string_sequence 3 == "0 1 2 3")
  assert! (string_sequence 10 == "0 1 2 3 4 5 6 7 8 9 10")
  IO.println "All tests passed!"

end StringSequence
