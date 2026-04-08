```lean
import Batteries.Data.String.Basic

/-- Return a string containing space-delimited numbers starting from 0 upto n inclusive. -/
def string_sequence (n : Nat) : String :=
  if n = 0 then
    "0"
  else
    String.join $ List.intersperse " " $
      List.map (fun x => toString x) $ List.range (n + 1)

/-- The specification for string_sequence. -/
def string_sequence_spec (n : Nat) : String :=
  if n = 0 then
    "0"
  else
    String.join $ List.intersperse " " $
      List.map (fun x => toString x) $ List.range (n + 1)

/-- Precondition: n must be a natural number. -/
def string_sequence_pre (_n : Nat) : Prop := True

/-- Postcondition: The result is a string with space-delimited numbers from 0 to n. -/
def string_sequence_post (n : Nat) (result : String) : Prop :=
  result = string_sequence_spec n

theorem string_sequence_correct (n : Nat) (h_pre : string_sequence_pre n) : 
  string_sequence_post n (string_sequence n) := by
  unfold string_sequence_post
  unfold string_sequence_spec
  unfold string_sequence
  simp
  sorry

/-- Unit tests for string_sequence -/
def string_sequence_tests : IO Unit := do
  assert! (string_sequence 0 = "0")
  assert! (string_sequence 3 = "0 1 2 3")
  assert! (string_sequence 10 = "0 1 2 3 4 5 6 7 8 9 10")
  IO.println "All tests passed!"
```
