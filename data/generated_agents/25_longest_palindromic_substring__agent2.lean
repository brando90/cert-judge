import Lean.Data.RBMap

def isPalindrome (s : String) : Bool :=
  let chars := s.toList
  chars == chars.reverse

def expandAroundCenter (s : String) (left right : Nat) : String :=
  let rec loop (left : Int) (right : Nat) : (Int × Nat) :=
    if left >= 0 && right < s.length && s.get ⟨left.toNat, by sorry⟩ == s.get ⟨right, by sorry⟩ then
      loop (left - 1) (right + 1)
    else
      (left + 1, right)
  
  let (newLeft, newRight) := loop left.toInt right
  s.extract ⟨newLeft.toNat, by sorry⟩ ⟨newRight, by sorry⟩

def longest_palindrome_spec (s : String) : String :=
  if s.length = 0 then
    ""
  else
    let rec findLongest (i : Nat) (longest : String) : String :=
      if i >= s.length then
        longest
      else
        -- Check odd length palindromes
        let odd := expandAroundCenter s i i
        -- Check even length palindromes
        let even := expandAroundCenter s i (i + 1)
        
        let newLongest := 
          if odd.length > longest.length then odd
          else if even.length > longest.length then even
          else longest
        
        findLongest (i + 1) newLongest
    
    findLongest 0 ""

def pre (s : String) : Prop := True

def post (s : String) (result : String) : Prop :=
  -- Result is a palindrome
  isPalindrome result &&
  -- Result is a substring of s
  (∃ i j, i ≤ j && j ≤ s.length && result = s.extract ⟨i, by sorry⟩ ⟨j, by sorry⟩) &&
  -- No longer palindromic substring exists
  (∀ i j, i ≤ j && j ≤ s.length → 
    let substr := s.extract ⟨i, by sorry⟩ ⟨j, by sorry⟩
    isPalindrome substr → substr.length ≤ result.length)

def longest_palindrome (s : String) : String :=
  longest_palindrome_spec s

theorem longest_palindrome_correct (s : String) :
  pre s → post s (longest_palindrome s) :=
  sorry

#eval longest_palindrome "babad" -- Should return "bab" or "aba"
#eval longest_palindrome "cbbd"  -- Should return "bb"
#eval longest_palindrome "a"     -- Should return "a"
#eval longest_palindrome ""      -- Should return ""

example : longest_palindrome "babad" = "bab" ∨ longest_palindrome "babad" = "aba" := by
  simp [longest_palindrome]
  sorry

example : longest_palindrome "cbbd" = "bb" := by
  simp [longest_palindrome]
  sorry

example : longest_palindrome "a" = "a" := by
  simp [longest_palindrome]
  sorry

example : longest_palindrome "" = "" := by
  simp [longest_palindrome]
  sorry
