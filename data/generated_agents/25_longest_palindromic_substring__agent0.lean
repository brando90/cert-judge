import Batteries
import VeriBench

namespace LongestPalindrome

def isPalindrome (s : String) : Bool :=
  let chars := s.toList
  chars == chars.reverse

/-- Find the longest palindromic substring in a string.
Edge cases:
- Empty string returns empty string.
- Non-string input is invalid and raises ValueError. -/
def longest_palindrome (s : String) : String :=
  if s.isEmpty then
    ""
  else
    let expandAroundCenter (left right : Nat) : String :=
      let rec expand (l r : Nat) : String :=
        if l >= s.length || r >= s.length || l > r then
          ""
        else if l == 0 && s.get! l == s.get! r then
          s.extract 0 (r+1)
        else if l == 0 then
          ""
        else if s.get! l == s.get! r then
          s.extract (l) (r+1)
        else
          s.extract (l+1) r
      
      expand left right
    
    let rec findLongest (i : Nat) (longest : String) : String :=
      if i >= s.length then
        longest
      else
        -- Check odd length palindromes
        let odd := expandAroundCenter i i
        let longest' := if odd.length > longest.length then odd else longest
        
        -- Check even length palindromes
        let even := if i + 1 < s.length then expandAroundCenter i (i+1) else ""
        let longest'' := if even.length > longest'.length then even else longest'
        
        findLongest (i+1) longest''
    
    findLongest 0 ""

-- Tests
#eval longest_palindrome "babad" -- "bab" or "aba"
#eval longest_palindrome "cbbd"  -- "bb"
#eval longest_palindrome "a"     -- "a"
#eval longest_palindrome ""      -- ""

-- Verification
def pre (s : String) : Prop := True

def post (s : String) (result : String) : Prop :=
  -- Result is a substring of the input
  (∃ (i j : Nat), i ≤ j ∧ j ≤ s.length ∧ result = s.extract i j) ∧ 
  -- Result is a palindrome
  isPalindrome result ∧
  -- Result is the longest palindrome substring
  (∀ (t : String), 
    (∃ (i j : Nat), i ≤ j ∧ j ≤ s.length ∧ t = s.extract i j) → 
    isPalindrome t → t.length ≤ result.length)

theorem longest_palindrome_correct (s : String) (h : pre s) : post s (longest_palindrome s) := by
  sorry

end LongestPalindrome
