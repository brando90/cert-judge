import Mathlib

namespace AllPrefixes


def allPrefixes (s : String) : List String :=
  (List.range s.length).map (fun i => s.take (i + 1))


def allPrefixesImp (s : String) : List String :=
  let chars := s.toList
  let rec go (acc : List String) (prefix : List Char) (remaining : List Char) : List String :=
    match remaining with
    | [] => acc.reverse
    | c :: cs => 
      let newPrefix := prefix ++ [c]
      go (String.mk newPrefix :: acc) newPrefix cs
  if chars.isEmpty then [] else go [] [] chars



/-!
# Tests
-/

/-- expected: [] -/
example : allPrefixes "" = [] := by native_decide
#eval allPrefixes ""

/-- expected: ["a", "ab", "abc"] -/
example : allPrefixes "abc" = ["a", "ab", "abc"] := by native_decide
#eval allPrefixes "abc"

/-!
# Tests: Edge Cases
-/

/-- expected: ["a", "as", "asd", "asdf", "asdfg", "asdfgh"] -/
example : allPrefixes "asdfgh" = ["a", "as", "asd", "asdf", "asdfg", "asdfgh"] := by native_decide
#eval allPrefixes "asdfgh"

/-- expected: ["W", "WW", "WWW"] -/
example : allPrefixes "WWW" = ["W", "WW", "WWW"] := by native_decide
#eval allPrefixes "WWW"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single character -/
example : allPrefixes "x" = ["x"] := by native_decide
#eval allPrefixes "x" -- expected: ["x"]

/-- positive: two characters -/
example : allPrefixes "ab" = ["a", "ab"] := by native_decide
#eval allPrefixes "ab" -- expected: ["a", "ab"]

/-- negative: empty string gives empty list not singleton -/
example : ¬ (allPrefixes "" = [""]) := by native_decide
#eval (decide (allPrefixes "" = [""])) -- expected: false

/-- negative: result is sorted by length -/
example : ¬ (allPrefixes "abc" = ["abc", "ab", "a"]) := by native_decide
#eval (decide (allPrefixes "abc" = ["abc", "ab", "a"])) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single character -/
example : allPrefixesImp "x" = ["x"] := by native_decide
#eval allPrefixesImp "x" -- expected: ["x"]

/-- negative: order matters -/
example : ¬ (allPrefixesImp "abc" = ["abc", "ab", "a"]) := by native_decide
#eval (decide (allPrefixesImp "abc" = ["abc", "ab", "a"])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem allPrefixes_equivalence_thm (s : String) :
  allPrefixes s = allPrefixesImp s := sorry




end AllPrefixes