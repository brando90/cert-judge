import VeriBench

namespace DecodeShift

/-- Returns encoded string by shifting every character by 5 in the alphabet. -/
def encodeShift (s : String) : String :=
  String.mk <| s.toList.map fun ch =>
    let shifted := ((ch.toNat + 5 - 'a'.toNat) % 26) + 'a'.toNat
    Char.ofNat shifted

/-- Takes as input string encoded with encode_shift function. Returns decoded string. -/
def decodeShift (s : String) : String :=
  String.mk <| s.toList.map fun ch =>
    let shifted := ((ch.toNat - 5 - 'a'.toNat) % 26) + 'a'.toNat
    Char.ofNat shifted

/-- Pre-condition: All characters in the input string are lowercase letters. -/
def pre (s : String) : Prop :=
  ∀ c ∈ s.toList, 'a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat

/-- Post-condition: The result of decode_shift on a string encoded with encode_shift is the original string. -/
def post (s : String) (result : String) : Prop :=
  result = s

/-- Correctness theorem: Decoding an encoded string returns the original string. -/
theorem decodeShift_correct (s : String) (h : pre s) : post s (decodeShift (encodeShift s)) :=
  sorry

/-- Test cases for the decode_shift function. -/
def tests : List (String × String) := [
  ("fghij", "abcde"),
  ("qrstuvwxyzabcde", "lmnopqrstuvwxyz"),
  ("eeeeeeeeee", "zzzzzzzzz" ++ String.mk ['z'])
]

/-- Run the tests for decode_shift. -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := decodeShift input
    if result == expected then
      IO.println s!"Test passed for input {input}"
    else
      IO.println s!"Test failed for input {input}: expected {expected}, got {result}"

end DecodeShift
