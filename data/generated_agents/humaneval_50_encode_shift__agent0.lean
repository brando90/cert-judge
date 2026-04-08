/-
# VeriBench Problem: HumanEval/50

In this problem, we implement and verify functions for encoding and decoding strings
by shifting each character by 5 positions in the alphabet.
-/

import Lean.Data.HashMap
import Mathlib.Tactic

namespace HumanEval50

/-- Encodes a string by shifting every character by 5 in the alphabet. -/
def encodeShift (s : String) : String :=
  s.map fun ch => 
    if 'a' ≤ ch && ch ≤ 'z' then
      let shifted := ((ch.toNat + 5 - 'a'.toNat) % 26 + 'a'.toNat).toUInt8
      shifted.toChar
    else
      ch

/-- Decodes a string that was encoded with `encodeShift`. -/
def decodeShift (s : String) : String :=
  s.map fun ch => 
    if 'a' ≤ ch && ch ≤ 'z' then
      let shifted := ((ch.toNat - 5 - 'a'.toNat) % 26 + 'a'.toNat).toUInt8
      shifted.toChar
    else
      ch

/-- Predicate indicating if a character is a lowercase letter. -/
def isLowerLetter (c : Char) : Bool :=
  'a' ≤ c && c ≤ 'z'

/-- Predicate indicating if a string contains only lowercase letters. -/
def containsOnlyLowerLetters (s : String) : Bool :=
  s.all isLowerLetter

/-- Precondition for `encodeShift`: The input string should contain only lowercase letters. -/
def encodeShiftPre (s : String) : Prop :=
  containsOnlyLowerLetters s

/-- Postcondition for `encodeShift`: The result should contain only lowercase letters. -/
def encodeShiftPost (s : String) (result : String) : Prop :=
  containsOnlyLowerLetters result ∧ result.length = s.length

/-- Precondition for `decodeShift`: The input string should contain only lowercase letters. -/
def decodeShiftPre (s : String) : Prop :=
  containsOnlyLowerLetters s

/-- Postcondition for `decodeShift`: The result should contain only lowercase letters. -/
def decodeShiftPost (s : String) (result : String) : Prop :=
  containsOnlyLowerLetters result ∧ result.length = s.length

/-- The key property: decoding an encoded string gives back the original string. -/
theorem decodeShiftCorrectness (s : String) (h : encodeShiftPre s) :
  decodeShift (encodeShift s) = s := by
  sorry

/-- The key property: encoding a decoded string gives back the original string. -/
theorem encodeShiftCorrectness (s : String) (h : decodeShiftPre s) :
  encodeShift (decodeShift s) = s := by
  sorry

/-- Tests for the encode and decode functions -/
def tests : IO Unit := do
  let test1 := "hello"
  let encoded1 := encodeShift test1
  let decoded1 := decodeShift encoded1
  IO.println s!"Original: {test1}, Encoded: {encoded1}, Decoded: {decoded1}"
  assert! decoded1 == test1

  let test2 := "abcdefghijklmnopqrstuvwxyz"
  let encoded2 := encodeShift test2
  let decoded2 := decodeShift encoded2
  IO.println s!"Original: {test2}, Encoded: {encoded2}, Decoded: {decoded2}"
  assert! decoded2 == test2

  let test3 := "zzzzzz"
  let encoded3 := encodeShift test3
  let decoded3 := decodeShift encoded3
  IO.println s!"Original: {test3}, Encoded: {encoded3}, Decoded: {decoded3}"
  assert! decoded3 == test3

  IO.println "All tests passed!"

end HumanEval50
