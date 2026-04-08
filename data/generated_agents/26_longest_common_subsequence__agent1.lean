import VeriBench
open VeriBench

/--
Find the longest common subsequence between two strings.
A subsequence is a sequence that appears in the same relative order but not necessarily contiguous.
The comparison is case-sensitive.

Edge cases:
- Empty inputs yield empty LCS.
- Non-strings are invalid.
-/
def longest_common_subsequence (s1 s2 : String) : String :=
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    let m := s1.length
    let n := s2.length
    
    -- dp[i][j] = length of LCS of s1[:i] and s2[:j]
    let mut dp := Array.mkArray (m+1) (Array.mkArray (n+1) 0)
    -- direction[i][j] = 0 if match (diagonal), 1 if came from top, 2 if came from left
    let mut direction := Array.mkArray (m+1) (Array.mkArray (n+1) 0)
    
    for i in [1:m+1] do
      for j in [1:n+1] do
        if s1.get (i-1) == s2.get (j-1) then
          dp := dp.set! i (dp[i]!.set! j (dp[i-1]![j-1]! + 1))
          direction := direction.set! i (direction[i]!.set! j 0) -- diagonal
        else
          if dp[i-1]![j]! >= dp[i]![j-1]! then
            dp := dp.set! i (dp[i]!.set! j (dp[i-1]![j]!))
            direction := direction.set! i (direction[i]!.set! j 1) -- up
          else
            dp := dp.set! i (dp[i]!.set! j (dp[i]![j-1]!))
            direction := direction.set! i (direction[i]!.set! j 2) -- left
    
    -- Reconstruct from bottom-right
    let mut i := m
    let mut j := n
    let mut result := ""
    
    while i > 0 && j > 0 do
      if direction[i]![j]! == 0 then
        result := s1.get (i-1) ++ result
        i := i - 1
        j := j - 1
      else if direction[i]![j]! == 1 then
        i := i - 1
      else
        j := j - 1
    
    result

/-- Verify that `sub` is a subsequence of `sup` (case-sensitive). -/
def verifySubsequence (sub sup : String) : Bool :=
  if sub.isEmpty then
    true
  else if sup.isEmpty then
    false
  else
    let mut i := 0
    let mut j := 0
    while i < sub.length && j < sup.length do
      if sub.get i == sup.get j then
        i := i + 1
      j := j + 1
    i == sub.length

/-- Precondition for longest_common_subsequence -/
def pre (s1 s2 : String) : Prop := True

/-- Postcondition for longest_common_subsequence -/
def post (s1 s2 result : String) : Prop :=
  -- Result is a subsequence of both inputs
  verifySubsequence result s1 && verifySubsequence result s2 &&
  -- No longer subsequence exists
  (∀ other : String, verifySubsequence other s1 && verifySubsequence other s2 → other.length ≤ result.length)

/-- Correctness theorem for longest_common_subsequence -/
theorem longest_common_subsequence_correct (s1 s2 : String) :
  pre s1 s2 → post s1 s2 (longest_common_subsequence s1 s2) := sorry

/-- Tests for longest_common_subsequence -/
def test_longest_common_subsequence : IO Unit := do
  assertEq (longest_common_subsequence "abcde" "ace") "ace"
  assertEq (longest_common_subsequence "abc" "abc") "abc"
  assertEq (longest_common_subsequence "abc" "def") ""
  assertEq (longest_common_subsequence "" "") ""
  assertEq (longest_common_subsequence "ABCDGH" "AEDFHR") "ADH"
  assertEq (longest_common_subsequence "AGGTAB" "GXTXAYB") "GTAB"
  assertEq (longest_common_subsequence "Hello" "HELLO") "H"
  IO.println "All tests passed!"
