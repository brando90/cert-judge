import Mathlib

namespace CaesarCipher


def isLower (c : Char) : Bool :=
  'a' ≤ c && c ≤ 'z'


def shiftChar (c : Char) (n : Int) : Char :=
  if isLower c then
    let base : Int := (c.toNat : Int) - ('a'.toNat : Int)
    let shifted := ((base + n) % 26 + 26) % 26
    Char.ofNat (shifted.toNat + 'a'.toNat)
  else
    c


def encodeShift (s : String) : String :=
  String.mk (s.data.map (fun c => shiftChar c 5))


def decodeShift (s : String) : String :=
  String.mk (s.data.map (fun c => shiftChar c (-5)))


def encodeShiftImp (s : String) : String := Id.run do
  let chars := s.data
  let mut result := #[]
  for c in chars do
    result := result.push (shiftChar c 5)
  return String.mk result.toList


def decodeShiftImp (s : String) : String := Id.run do
  let chars := s.data
  let mut result := #[]
  for c in chars do
    result := result.push (shiftChar c (-5))
  return String.mk result.toList



/-!
# Tests
-/

/-- expected: "mjqqt" -/
example : encodeShift "hello" = "mjqqt" := by native_decide
#eval encodeShift "hello" -- expected: "mjqqt"

/-- expected: "fghcde" -/
example : encodeShift "abcxyz" = "fghcde" := by native_decide
#eval encodeShift "abcxyz" -- expected: "fghcde"

/-!
# Tests: Edge Cases
-/

/-- expected: "" -/
example : encodeShift "" = "" := by native_decide
#eval encodeShift "" -- expected: ""

/-- expected: "Hjqqt!" -/
example : encodeShift "Hello!" = "Hjqqt!" := by native_decide
#eval encodeShift "Hello!" -- expected: "Hjqqt!"

/-- expected: "123" -/
example : encodeShift "123" = "123" := by native_decide
#eval encodeShift "123" -- expected: "123"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: decode(encode("hello")) = "hello" -/
example : decodeShift (encodeShift "hello") = "hello" := by native_decide
#eval decodeShift (encodeShift "hello") -- expected: "hello"

/-- positive: encode("world") = "btwqi" -/
example : encodeShift "world" = "btwqi" := by native_decide
#eval encodeShift "world" -- expected: "btwqi"

/-- negative: encode("hello") ≠ "hello" -/
example : ¬ (encodeShift "hello" = "hello") := by native_decide
#eval (decide (encodeShift "hello" = "hello")) -- expected: false

/-- negative: encode("abc") ≠ "xyz" -/
example : ¬ (encodeShift "abc" = "xyz") := by native_decide
#eval (decide (encodeShift "abc" = "xyz")) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: encodeShiftImp("world") = "btwqi" -/
example : encodeShiftImp "world" = "btwqi" := by native_decide
#eval encodeShiftImp "world" -- expected: "btwqi"

/-- negative: encodeShiftImp("hello") ≠ "hello" -/
example : ¬ (encodeShiftImp "hello" = "hello") := by native_decide
#eval (decide (encodeShiftImp "hello" = "hello")) -- expected: false

/-- **Equivalence theorem**: functional and imperative encoding coincide. -/
theorem encodeShift_equivalence_thm (s : String) :
  encodeShift s = encodeShiftImp s := sorry

/-- **Decode equivalence theorem**: functional and imperative decoding coincide. -/
theorem decodeShift_equivalence_thm (s : String) :
  decodeShift s = decodeShiftImp s := sorry




end CaesarCipher