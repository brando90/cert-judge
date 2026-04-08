import VeriBench

namespace LengthOfLongestSubstring

def pre (s : String) : Bool := true

/--
Find the length of the longest substring without repeating characters.
-/
def lengthOfLongestSubstring (s : String) : Nat :=
  if s.isEmpty then
    0
  else
    let rec findLongest (start : Nat) (pos : Nat) (maxLen : Nat) (charPos : Lean.HashMap Char Nat) : Nat :=
      if pos >= s.length then
        maxLen
      else
        let char := s.get ⟨pos, by simp [s.length, pos]; exact Nat.lt_of_lt_of_le (Nat.lt_succ_self pos) (by assumption)⟩
        let (newStart, newMaxLen) :=
          match charPos.find? char with
          | some lastPos =>
              if lastPos >= start then
                (lastPos + 1, maxLen)
              else
                (start, Nat.max maxLen (pos - start + 1))
          | none =>
              (start, Nat.max maxLen (pos - start + 1))
        findLongest newStart (pos + 1) newMaxLen (charPos.insert char pos)
    
    findLongest 0 0 0 {}

/--
Verify if a string has all unique characters.
-/
def verifyUniqueChars (s : String) : Bool :=
  let rec isUnique (pos : Nat) (seen : Lean.HashSet Char) : Bool :=
    if pos >= s.length then
      true
    else
      let char := s.get ⟨pos, by simp [s.length, pos]; exact Nat.lt_of_lt_of_le (Nat.lt_succ_self pos) (by assumption)⟩
      if seen.contains char then
        false
      else
        isUnique (pos + 1) (seen.insert char)
  
  isUnique 0 {}

/--
Specification for the longest substring without repeating characters.
-/
def post (s : String) (result : Nat) : Prop :=
  (s.isEmpty → result = 0) ∧
  (∃ start stop, start ≤ stop ∧ stop ≤ s.length ∧ 
     let substr := s.extract start stop;
     verifyUniqueChars substr = true ∧ 
     substr.length = result ∧
     (∀ start' stop', start' ≤ stop' ∧ stop' ≤ s.length →
       let substr' := s.extract start' stop';
       verifyUniqueChars substr' = true → substr'.length ≤ result))

theorem lengthOfLongestSubstring_correct (s : String) :
  pre s → post s (lengthOfLongestSubstring s) := by sorry

/-- Basic test -/
#eval lengthOfLongestSubstring "abcabcbb" -- 3

/-- Edge case -/
#eval lengthOfLongestSubstring "" -- 0

/-- Single character -/
#eval lengthOfLongestSubstring " " -- 1

/-- Two characters -/
#eval lengthOfLongestSubstring "au" -- 2

/-- Repeated characters -/
#eval lengthOfLongestSubstring "bbbbb" -- 1

/-- Mixed pattern -/
#eval lengthOfLongestSubstring "pwwkew" -- 3

/-- Additional test cases -/
#eval lengthOfLongestSubstring "aab" -- 2
#eval lengthOfLongestSubstring "dvdf" -- 3

end LengthOfLongestSubstring
