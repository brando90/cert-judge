import Std.Data.List.Basic
import Std.Data.HashMap
open Std

/--
Find the length of the longest substring without repeating characters.

Examples:
- `lengthOfLongestSubstring "abcabcbb" = 3`
- `lengthOfLongestSubstring "bbbbb" = 1`
- `lengthOfLongestSubstring "pwwkew" = 3`
- `lengthOfLongestSubstring "" = 0`
- `lengthOfLongestSubstring " " = 1`
- `lengthOfLongestSubstring "au" = 2`
- `lengthOfLongestSubstring "aab" = 2`
- `lengthOfLongestSubstring "dvdf" = 3`
-/
def lengthOfLongestSubstring (s : String) : Nat :=
  if s.isEmpty then 0
  else
    let chars := s.toList
    let rec loop (charPos : HashMap Char Nat) (start : Nat) (end : Nat) (maxLen : Nat) : Nat :=
      if end >= chars.length then
        maxLen
      else
        let char := chars[end]!
        match charPos.find? char with
        | some pos =>
          if pos >= start then
            -- Move start to position after the last occurrence
            let newStart := pos + 1
            let newCharPos := charPos.insert char end
            loop newCharPos newStart (end + 1) maxLen
          else
            -- Update max length if current window is longer
            let newMaxLen := Nat.max maxLen (end - start + 1)
            let newCharPos := charPos.insert char end
            loop newCharPos start (end + 1) newMaxLen
        | none =>
          -- Update max length if current window is longer
          let newMaxLen := Nat.max maxLen (end - start + 1)
          let newCharPos := charPos.insert char end
          loop newCharPos start (end + 1) newMaxLen

    loop (HashMap.empty) 0 0 0

/-- Verify if a string has all unique characters. -/
def verifyUniqueChars (s : String) : Bool :=
  let chars := s.toList
  chars.length = chars.eraseDups.length

/-- Precondition: The input must be a string (always true in Lean) -/
def pre (_s : String) : Bool := true

/-- 
Postcondition: The result is a non-negative integer representing the length
of the longest substring without repeating characters.
-/
def post (s : String) (result : Nat) : Prop :=
  -- The result is always non-negative (guaranteed by Nat type)
  -- The result is 0 if the string is empty
  (s.isEmpty → result = 0) ∧
  -- The result is at most the length of the input string
  (result ≤ s.length) ∧
  -- There exists a substring of length 'result' with unique characters
  (∃ (i : Nat), i + result ≤ s.length ∧ verifyUniqueChars (s.extract i (i + result))) ∧
  -- No longer substring has unique characters
  (∀ (len : Nat), len > result → 
    ∀ (i : Nat), i + len ≤ s.length → ¬verifyUniqueChars (s.extract i (i + len)))

/-- The implementation satisfies the specification -/
theorem lengthOfLongestSubstring_correct (s : String) :
  pre s → post s (lengthOfLongestSubstring s) := by
  sorry

#eval lengthOfLongestSubstring "abcabcbb" -- 3
#eval lengthOfLongestSubstring "bbbbb" -- 1
#eval lengthOfLongestSubstring "pwwkew" -- 3
#eval lengthOfLongestSubstring "" -- 0
#eval lengthOfLongestSubstring " " -- 1
#eval lengthOfLongestSubstring "au" -- 2
#eval lengthOfLongestSubstring "aab" -- 2
#eval lengthOfLongestSubstring "dvdf" -- 3

example : lengthOfLongestSubstring "abcabcbb" = 3 := rfl
example : lengthOfLongestSubstring "bbbbb" = 1 := rfl
example : lengthOfLongestSubstring "pwwkew" = 3 := rfl
example : lengthOfLongestSubstring "" = 0 := rfl
example : lengthOfLongestSubstring " " = 1 := rfl
example : lengthOfLongestSubstring "au" = 2 := rfl
example : lengthOfLongestSubstring "aab" = 2 := rfl
example : lengthOfLongestSubstring "dvdf" = 3 := rfl
