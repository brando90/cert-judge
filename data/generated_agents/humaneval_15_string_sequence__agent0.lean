import Lean
import Mathlib.Tactic.Basic

/--
  Return a string containing space-delimited numbers starting from 0 upto n inclusive.
-/
def string_sequence (n : Nat) : String :=
  if n = 0 then
    "0"
  else
    String.intercalate " " (List.map toString (List.range (n + 1)))

/--
  Specification for `string_sequence`.
  
  Returns a string containing space-delimited numbers starting from 0 up to n inclusive.
-/
def string_sequence_spec (n : Nat) : String :=
  if n = 0 then
    "0"
  else
    String.intercalate " " (List.map toString (List.range (n + 1)))

/--
  Proof that `string_sequence` satisfies its specification.
-/
theorem string_sequence_correct (n : Nat) : 
  string_sequence n = string_sequence_spec n := by
  simp [string_sequence, string_sequence_spec]
  sorry

-- Tests
example : string_sequence 0 = "0" := by rfl
example : string_sequence 3 = "0 1 2 3" := by rfl
example : string_sequence 10 = "0 1 2 3 4 5 6 7 8 9 10" := by rfl
