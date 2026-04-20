import Mathlib

namespace CyclicEncoding


def splitIntoGroups (chars : List Char) (n : Nat) : List (List Char) :=
  if chars.length < n then
    if chars.isEmpty then [] else [chars]
  else
    let group := chars.take n
    group :: splitIntoGroups (chars.drop n) n


def cycleGroup (group : List Char) : List Char :=
  if group.length = 3 then
    group.drop 1 ++ group.take 1
  else
    group


def encode_cyclic (s : String) : String :=
  let groups := splitIntoGroups s.data 3
  let cycled := groups.map cycleGroup
  String.mk (List.flatten cycled)


def decode_cyclic (s : String) : String :=
  encode_cyclic (encode_cyclic s)


def encode_cyclicImp (s : String) : String :=
  let chars := s.data
  let mut result : List Char := []
  let mut i := 0
  while i < chars.length do
    if i + 2 < chars.length then
      -- Full group of 3 characters - cycle them
      let c1 := chars[i]!
      let c2 := chars[i + 1]!
      let c3 := chars[i + 2]!
      result := result ++ [c2, c3, c1]
      i := i + 3
    else
      -- Remaining characters (less than 3) - keep as is
      result := result ++ chars.drop i
      break
  String.mk result



/-!
# Tests
-/

/-- expected: "bcaefd" -/
example : encode_cyclic "abcdef" = "bcaefd" := by native_decide
#eval encode_cyclic "abcdef" -- expected: "bcaefd"

/-- expected: "bca" -/
example : encode_cyclic "abc" = "bca" := by native_decide
#eval encode_cyclic "abc" -- expected: "bca"

/-!
# Tests: Edge Cases
-/

/-- empty string -/
example : encode_cyclic "" = "" := by native_decide
#eval encode_cyclic "" -- expected: ""

/-- four characters -/
example : encode_cyclic "abcd" = "bcad" := by native_decide
#eval encode_cyclic "abcd" -- expected: "bcad"

/-- two characters -/
example : encode_cyclic "ab" = "ab" := by native_decide
#eval encode_cyclic "ab" -- expected: "ab"

/-!
# Positive / Negative Test-Suite
-/

/-- positive: decode undoes encode for 6-char string -/
example : decode_cyclic (encode_cyclic "abcdef") = "abcdef" := by native_decide
#eval decode_cyclic (encode_cyclic "abcdef") -- expected: "abcdef"

/-- positive: decode undoes encode for short string -/
example : decode_cyclic (encode_cyclic "abc") = "abc" := by native_decide
#eval decode_cyclic (encode_cyclic "abc") -- expected: "abc"

/-- negative: encoding changes the string for 3+ char groups -/
example : ¬ (encode_cyclic "abc" = "abc") := by native_decide

/-- negative: different strings encode differently -/
example : ¬ (encode_cyclic "abc" = encode_cyclic "def") := by native_decide

/-!
# Positive / Negative Test-Suite
-/

/-- positive: four characters -/
example : encode_cyclicImp "abcd" = "bcad" := by native_decide
#eval encode_cyclicImp "abcd" -- expected: "bcad"

/-- negative: encoding changes the string -/
example : ¬ (encode_cyclicImp "abc" = "abc") := by native_decide

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem encode_cyclic_equivalence_thm (s : String) :
  encode_cyclic s = encode_cyclicImp s := sorry




end CyclicEncoding