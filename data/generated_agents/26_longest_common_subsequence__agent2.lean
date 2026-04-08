/-- Longest common subsequence (LCS) for two strings.
A subsequence is a sequence that appears in the same relative order but not necessarily contiguous.
The comparison is case-sensitive.

Edge cases:
- Empty inputs yield empty LCS.
- Non-strings are invalid and raise ValueError.
-/

namespace LongestCommonSubsequence

/-- Verify that `sub` is a subsequence of `sup` (case-sensitive). -/
def isSubsequence (sub : String) (sup : String) : Bool :=
  let rec go (i j : Nat) : Bool :=
    if i ≥ sub.length then true
    else if j ≥ sup.length then false
    else if sub.get! i == sup.get! j then go (i+1) (j+1)
    else go i (j+1)
  go 0 0

/-- Precondition: Both inputs must be strings -/
def pre (s1 s2 : String) : Bool := true

/-- Postcondition: Result is a subsequence of both input strings and 
    no longer subsequence exists. -/
def post (s1 s2 result : String) : Bool :=
  isSubsequence result s1 && 
  isSubsequence result s2 && 
  (∀ other : String, isSubsequence other s1 && isSubsequence other s2 → other.length ≤ result.length)

/-- Find the longest common subsequence between two strings. -/
def longestCommonSubsequence (s1 s2 : String) : String :=
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    let m := s1.length
    let n := s2.length
    
    -- dp[i][j] = length of LCS of s1[:i] and s2[:j]
    let dp := Array.mkArray (m+1) (Array.mkArray (n+1) 0)
    -- direction[i][j] = 0 if match (diagonal), 1 if from top, 2 if from left
    let direction := Array.mkArray (m+1) (Array.mkArray (n+1) 0)
    
    -- Fill dp and direction tables
    let (dp, direction) := (0 : Nat).foldl
      (fun (dp, direction) i =>
        (0 : Nat).foldl
          (fun (dp, direction) j =>
            if i > 0 && j > 0 then
              if s1.get! (i-1) == s2.get! (j-1) then
                let dp := dp.set! i (dp.get! i |>.set! j ((dp.get! (i-1)).get! (j-1) + 1))
                let direction := direction.set! i (direction.get! i |>.set! j 0)
                (dp, direction)
              else if (dp.get! (i-1)).get! j >= (dp.get! i).get! (j-1) then
                let dp := dp.set! i (dp.get! i |>.set! j ((dp.get! (i-1)).get! j))
                let direction := direction.set! i (direction.get! i |>.set! j 1)
                (dp, direction)
              else
                let dp := dp.set! i (dp.get! i |>.set! j ((dp.get! i).get! (j-1)))
                let direction := direction.set! i (direction.get! i |>.set! j 2)
                (dp, direction)
            else
              (dp, direction))
          (dp, direction)
          (List.range (n+1)))
      (dp, direction)
      (List.range (m+1))
    
    -- Reconstruct result from bottom-right
    let rec reconstructLCS (i j : Nat) (acc : List Char) : List Char :=
      if i > 0 && j > 0 then
        let dir := (direction.get! i).get! j
        if dir == 0 then -- diagonal (match)
          reconstructLCS (i-1) (j-1) (s1.get! (i-1) :: acc)
        else if dir == 1 then -- up
          reconstructLCS (i-1) j acc
        else -- left
          reconstructLCS i (j-1) acc
      else
        acc
    
    let resultChars := reconstructLCS m n []
    String.mk resultChars

theorem longestCommonSubsequence_correct (s1 s2 : String) :
  pre s1 s2 → post s1 s2 (longestCommonSubsequence s1 s2) :=
  sorry

/-!
  Test cases for the longest common subsequence function
-/

#eval longestCommonSubsequence "abcde" "ace" -- "ace"
#eval longestCommonSubsequence "abc" "abc" -- "abc"
#eval longestCommonSubsequence "abc" "def" -- ""
#eval longestCommonSubsequence "" "" -- ""
#eval longestCommonSubsequence "ABCDGH" "AEDFHR" -- "ADH"
#eval longestCommonSubsequence "AGGTAB" "GXTXAYB" -- "GTAB"
#eval longestCommonSubsequence "Hello" "HELLO" -- "H"

end LongestCommonSubsequence
