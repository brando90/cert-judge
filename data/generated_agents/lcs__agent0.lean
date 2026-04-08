import Mathlib.Tactic.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic
import Std.Data.List.Basic

namespace VeriBench.LongestCommonSubsequence

inductive SeqType
  | Str
  | Lst

def isSubsequence {α : Type} [BEq α] (sub : List α) (seq : List α) : Bool :=
  match sub, seq with
  | [], _ => true
  | _, [] => false
  | h₁::t₁, h₂::t₂ => 
    if h₁ == h₂ then 
      isSubsequence t₁ t₂
    else 
      isSubsequence sub t₂

/-- Find the longest common subsequence of two lists using dynamic programming. -/
def longestCommonSubsequence {α : Type} [BEq α] (s1 s2 : List α) : List α :=
  let m := s1.length
  let n := s2.length
  
  -- Create DP table with empty lists
  let initDp := List.replicate (m + 1) (List.replicate (n + 1) [])
  
  -- Helper function to fill the DP table
  let fillDp := fun dp i j =>
    if i = 0 || j = 0 then
      dp
    else if s1[i - 1]? == s2[j - 1]? then
      -- If characters match, add to the diagonal result
      let prev := dp[i - 1]?[j - 1]?.getD []
      dp.set i (dp[i]?.getD []).set j (prev ++ [s1[i - 1]?.getD default])
    else
      -- Take the longer of the two options
      let up := dp[i - 1]?[j]?.getD []
      let left := dp[i]?[j - 1]?.getD []
      if up.length >= left.length then
        dp.set i (dp[i]?.getD []).set j up
      else
        dp.set i (dp[i]?.getD []).set j left
  
  -- Fill the DP table iteratively
  let dp := 
    (List.range (m + 1)).foldl (fun acc i =>
      (List.range (n + 1)).foldl (fun acc' j =>
        fillDp acc' i j
      ) acc
    ) initDp
  
  -- Return the result from the bottom-right cell
  dp[m]?[n]?.getD []

/-- Returns the length of the longest common subsequence. -/
def lcsLength {α : Type} [BEq α] (s1 s2 : List α) : Nat :=
  let m := s1.length
  let n := s2.length
  
  -- Create DP table with zeros
  let initDp := List.replicate (m + 1) (List.replicate (n + 1) 0)
  
  -- Helper function to fill the DP table
  let fillDp := fun dp i j =>
    if i = 0 || j = 0 then
      dp
    else if s1[i - 1]? == s2[j - 1]? then
      -- If characters match, add 1 to diagonal
      let prev := dp[i - 1]?[j - 1]?.getD 0
      dp.set i (dp[i]?.getD []).set j (prev + 1)
    else
      -- Take maximum of up and left
      let up := dp[i - 1]?[j]?.getD 0
      let left := dp[i]?[j - 1]?.getD 0
      dp.set i (dp[i]?.getD []).set j (max up left)
  
  -- Fill the DP table iteratively
  let dp := 
    (List.range (m + 1)).foldl (fun acc i =>
      (List.range (n + 1)).foldl (fun acc' j =>
        fillDp acc' i j
      ) acc
    ) initDp
  
  -- Return the result from the bottom-right cell
  dp[m]?[n]?.getD 0

/-!
  Specification and verification
-/

/-- Precondition: both inputs must be valid sequences (lists in Lean) -/
def pre {α : Type} (s1 s2 : List α) : Prop := True

/-- Postcondition: the result is a common subsequence of both inputs -/
def post {α : Type} [BEq α] (s1 s2 result : List α) : Prop :=
  isSubsequence result s1 = true ∧ 
  isSubsequence result s2 = true ∧
  ∀ (other : List α), isSubsequence other s1 = true → isSubsequence other s2 = true → 
    other.length ≤ result.length

/-- The longest common subsequence function satisfies its specification -/
theorem longestCommonSubsequence_correct {α : Type} [BEq α] (s1 s2 : List α) :
  pre s1 s2 → post s1 s2 (longestCommonSubsequence s1 s2) :=
sorry

/-- The lcs length function returns the correct length -/
theorem lcsLength_correct {α : Type} [BEq α] (s1 s2 : List α) :
  pre s1 s2 → lcsLength s1 s2 = (longestCommonSubsequence s1 s2).length :=
sorry

/-!
  Tests
-/

def stringToList (s : String) : List Char := s.toList

def listToString (l : List Char) : String := String.mk l

/-- Test cases for longest common subsequence -/
def testLCS : IO Unit := do
  -- Tests with lists of numbers
  assert! (longestCommonSubsequence [1, 2, 3, 4] [1, 3, 5] == [1, 3])
  assert! (longestCommonSubsequence [1, 2, 3, 4, 5] [2, 4, 6] == [2, 4])
  assert! (longestCommonSubsequence [3, 5, 7, 9] [1, 3, 6, 7, 8] == [3, 7])
  assert! (longestCommonSubsequence [1] [1, 2] == [1])
  assert! (longestCommonSubsequence [1, 2] [1] == [1])
  assert! (longestCommonSubsequence [1, 2, 3, 4, 5] [1, 2, 3] == [1, 2, 3])
  assert! (longestCommonSubsequence [1, 2, 3] [4, 5, 6] == [])
  assert! (longestCommonSubsequence [] [1, 2, 3] == [])
  assert! (longestCommonSubsequence [1, 2, 3] [] == [])
  assert! (longestCommonSubsequence [] [] == [])
  assert! (longestCommonSubsequence [1, 2, 3] [1, 2, 3] == [1, 2, 3])
  assert! (longestCommonSubsequence [1, 2, 3, 4, 5, 6] [1, 3, 4, 6, 7, 8] == [1, 3, 4, 6])
  
  -- Tests with characters
  let s1 := stringToList "ABCDGH"
  let s2 := stringToList "AEDFHR"
  assert! (listToString (longestCommonSubsequence s1 s2) == "ADH")
  
  let s3 := stringToList "AGGTAB"
  let s4 := stringToList "GXTXAYB"
  assert! (listToString (longestCommonSubsequence s3 s4) == "GTAB")
  
  let s5 := stringToList "abc"
  let s6 := stringToList "abc"
  assert! (listToString (longestCommonSubsequence s5 s6) == "abc")
  
  let s7 := stringToList "abc"
  let s8 := stringToList "def"
  assert! (listToString (longestCommonSubsequence s7 s8) == "")
  
  let s9 := stringToList "abc"
  let s10 := stringToList "aabbcc"
  assert! (listToString (longestCommonSubsequence s9 s10) == "abc")
  
  let s11 := stringToList "programming"
  let s12 := stringToList "grading"
  assert! (listToString (longestCommonSubsequence s11 s12) == "graing")
  
  IO.println "All LCS tests passed!"

/-- Test cases for LCS length function -/
def testLCSLength : IO Unit := do
  assert! (lcsLength [1, 2, 3, 4] [1, 3, 5] == 2)
  assert! (lcsLength [] [] == 0)
  assert! (lcsLength [] [1, 2, 3] == 0)
  assert! (lcsLength [1, 2, 3] [] == 0)
  
  let s1 := stringToList "ABCDGH"
  let s2 := stringToList "AEDFHR"
  assert! (lcsLength s1 s2 == 3)
  
  let s3 := stringToList "AGGTAB"
  let s4 := stringToList "GXTXAYB"
  assert! (lcsLength s3 s4 == 4)
  
  IO.println "All LCS length tests passed!"

def main : IO Unit := do
  testLCS
  testLCSLength

end VeriBench.LongestCommonSubsequence
