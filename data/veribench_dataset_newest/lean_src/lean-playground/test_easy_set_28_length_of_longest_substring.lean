import Mathlib

namespace LongestSubstring


def List.hasUniqueChars (chars : List Char) : Bool :=
  let rec aux (seen : List Char) (rest : List Char) : Bool :=
    match rest with
    | [] => true
    | h::t =>
      if h ∈ seen then
        false
      else
        aux (h::seen) t
  aux [] chars


def String.hasUniqueChars (s : String) : Bool :=
  List.hasUniqueChars s.toList


def List.allSubstrings (chars : List Char) : List (List Char) :=
  let n := chars.length
  (List.range n).flatMap fun i =>
    (List.range (n - i + 1)).filterMap fun len =>
      if len > 0 && i + len <= n then
        some (chars.drop i |>.take len)
      else
        none


def lengthOfLongestSubstring (s : String) : Nat :=
  if s.isEmpty then
    0
  else
    let chars := s.toList
    let substrings := List.allSubstrings chars
    let uniqueSubstrings := substrings.filter List.hasUniqueChars
    uniqueSubstrings.foldl (fun acc sub => max acc sub.length) 0


def lengthOfLongestSubstringImp (s : String) : Nat :=
  if s.isEmpty then 0
  else
    let chars := s.toList
    let n := chars.length
    let rec slidingWindow (start : Nat) (maxLen : Nat) : Nat :=
      if start >= n then maxLen
      else
        let rec expandWindow (curr : Nat) (seen : List Char) (currLen : Nat) : Nat :=
          if curr >= n then currLen
          else
            let char := chars.get! curr
            if char ∈ seen then currLen
            else expandWindow (curr + 1) (char :: seen) (currLen + 1)
        let windowLen := expandWindow start [] 0
        slidingWindow (start + 1) (max maxLen windowLen)
    slidingWindow 0 0



/-!
# Tests
-/

/-- expected: 3 -/
example : lengthOfLongestSubstring "abcabcbb" = 3 := by native_decide
#eval! lengthOfLongestSubstring "abcabcbb" -- expected: 3

/-- expected: 1 -/
example : lengthOfLongestSubstring "bbbbb" = 1 := by native_decide
#eval! lengthOfLongestSubstring "bbbbb" -- expected: 1

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : lengthOfLongestSubstring "" = 0 := by unfold lengthOfLongestSubstring; rfl
#eval! lengthOfLongestSubstring "" -- expected: 0

/-- expected: 1 -/
example : lengthOfLongestSubstring "a" = 1 := by native_decide
#eval! lengthOfLongestSubstring "a" -- expected: 1

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: all unique characters -/
example : lengthOfLongestSubstring "abcdef" = 6 := by native_decide
#eval! lengthOfLongestSubstring "abcdef" -- expected: 6

/-- positive: repeated pattern -/
example : lengthOfLongestSubstring "pwwkew" = 3 := by native_decide
#eval! lengthOfLongestSubstring "pwwkew" -- expected: 3

/-- negative: result should not exceed input length -/
example : ¬ (lengthOfLongestSubstring "abc" > "abc".length) := by native_decide
#eval! (decide (lengthOfLongestSubstring "abc" > "abc".length)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: all unique characters -/
example : lengthOfLongestSubstringImp "abcdef" = 6 := by native_decide
#eval! lengthOfLongestSubstringImp "abcdef" -- expected: 6

/-- negative: result should not exceed input length -/
example : ¬ (lengthOfLongestSubstringImp "abc" > "abc".length) := by native_decide
#eval! (decide (lengthOfLongestSubstringImp "abc" > "abc".length)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem lengthOfLongestSubstring_equivalence_thm (s : String) :
  lengthOfLongestSubstring s = lengthOfLongestSubstringImp s := sorry




end LongestSubstring