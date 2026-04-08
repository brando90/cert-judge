import VeriBench

namespace LongestCommonSubsequence

/--
  Verify that `sub` is a subsequence of `sup` (case-sensitive).
-/
def isSubsequenceOf (sub sup : String) : Bool :=
  let rec loop (i j : Nat) : Bool :=
    if i >= sub.length then
      true
    else if j >= sup.length then
      false
    else if sub.get ⟨i⟩ == sup.get ⟨j⟩ then
      loop (i+1) (j+1)
    else
      loop i (j+1)
  loop 0 0

/--
  Find the longest common subsequence between two strings.
  A subsequence is a sequence that appears in the same relative order but not necessarily contiguous.
  The comparison is case-sensitive.
-/
def longestCommonSubsequence (s1 s2 : String) : String :=
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    let m := s1.length
    let n := s2.length
    
    -- dp[i][j] = length of LCS of s1[:i] and s2[:j]
    let dp := Array.mk (Array.mkArray (m+1) (Array.mkArray (n+1) 0))
    
    -- direction[i][j] = 0 if match (diagonal), 1 if came from top, 2 if came from left
    let direction := Array.mk (Array.mkArray (m+1) (Array.mkArray (n+1) 0))
    
    let dp := Array.foldl (fun dp i =>
      Array.foldl (fun dp j =>
        if s1.get ⟨i-1⟩ == s2.get ⟨j-1⟩ then
          let dp := dp.set! i (dp.get! i |>.set! j (dp.get! (i-1) |>.get! (j-1) + 1))
          dp.set! i (dp.get! i |>.set! j (dp.get! (i-1) |>.get! (j-1) + 1))
        else
          if dp.get! (i-1) |>.get! j >= dp.get! i |>.get! (j-1) then
            let dp := dp.set! i (dp.get! i |>.set! j (dp.get! (i-1) |>.get! j))
            let direction := direction.set! i (direction.get! i |>.set! j 1)
            dp
          else
            let dp := dp.set! i (dp.get! i |>.set! j (dp.get! i |>.get! (j-1)))
            let direction := direction.set! i (direction.get! i |>.set! j 2)
            dp
      ) dp (List.range n |>.map (·+1))
    ) dp (List.range m |>.map (·+1))
    
    -- Reconstruct from bottom-right
    let rec buildResult (i j : Nat) (acc : List Char) : List Char :=
      if i == 0 || j == 0 then
        acc
      else if direction.get! i |>.get! j == 0 then
        buildResult (i-1) (j-1) (s1.get ⟨i-1⟩ :: acc)
      else if direction.get! i |>.get! j == 1 then
        buildResult (i-1) j acc
      else
        buildResult i (j-1) acc
    
    let resultChars := buildResult m n []
    String.mk resultChars

/--
  Precondition for the longestCommonSubsequence function.
  Both inputs must be strings.
-/
def pre (s1 s2 : String) : Prop := True

/--
  Postcondition for the longestCommonSubsequence function.
  The result must be a subsequence of both input strings,
  and it must be the longest such subsequence.
-/
def post (s1 s2 result : String) : Prop :=
  isSubsequenceOf result s1 ∧ 
  isSubsequenceOf result s2 ∧
  (∀ other : String, isSubsequenceOf other s1 → isSubsequenceOf other s2 → other.length ≤ result.length)

/--
  Test cases for the longestCommonSubsequence function.
-/
def tests : List (String × String × String) := [
  ("abcde", "ace", "ace"),
  ("abc", "abc", "abc"),
  ("abc", "def", ""),
  ("", "", ""),
  ("ABCDGH", "AEDFHR", "ADH"),
  ("AGGTAB", "GXTXAYB", "GTAB"),
  ("Hello", "HELLO", "H")
]

/--
  Verify that the longestCommonSubsequence function satisfies its specification.
-/
theorem longestCommonSubsequence_correct (s1 s2 : String) (h : pre s1 s2) :
  post s1 s2 (longestCommonSubsequence s1 s2) := by
  sorry

end LongestCommonSubsequence

/--
  Benchmark for the longestCommonSubsequence function.
-/
def LongestCommonSubsequence.benchmark : VeriBench.Benchmark := {
  name := "LongestCommonSubsequence"
  fn := longestCommonSubsequence
  tests := tests.map (fun (s1, s2, expected) => ((s1, s2), expected))
  correctnessTheorem := longestCommonSubsequence_correct
}
