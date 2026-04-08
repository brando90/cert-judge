import Lean.Data.Array
import Std.Data.Array.Basic

/-! # Longest Common Subsequence -/

/-- A type for sequences that can be either strings or lists. -/
inductive Seq (α : Type)
  | Str : String → Seq α
  | List : List α → Seq α

/-- Convert a Seq to a List for uniform processing. -/
def Seq.toList {α : Type} : Seq α → List (Option α)
  | Seq.Str s => s.data.map Option.some
  | Seq.List l => l.map Option.some

/-- Check if a Seq is a string. -/
def Seq.isString {α : Type} : Seq α → Bool
  | Seq.Str _ => true
  | _ => false

/-- Precondition for longest_common_subsequence. -/
def longest_common_subsequence_pre {α : Type} (s1 s2 : Seq α) : Prop := True

/-- Implementation of longest common subsequence using dynamic programming. -/
def longest_common_subsequence {α : Type} [BEq α] (s1 s2 : Seq α) : Seq α := 
  let l1 := s1.toList
  let l2 := s2.toList
  
  let m := l1.length
  let n := l2.length
  
  -- Create and fill DP table
  let dp := Array.mkArray (m + 1) (Array.mkArray (n + 1) [])
  let dp := (List.range (m+1)).foldl (fun dp i => 
    (List.range (n+1)).foldl (fun dp j => 
      if i = 0 || j = 0 then 
        dp 
      else if l1[i-1]? = l2[j-1]? then
        let prev := dp[i-1]![j-1]!
        dp.set! i j (prev ++ [l1[i-1]!])
      else
        let prev1 := dp[i-1]![j]!
        let prev2 := dp[i][j-1]!
        if prev1.length >= prev2.length then
          dp.set! i j prev1
        else
          dp.set! i j prev2
    ) dp
  ) dp
  
  let result := dp[m]![n]!
  
  -- Convert back to the appropriate type
  if s1.isString && s2.isString then
    let chars := result.filterMap id
    Seq.Str (String.mk chars)
  else
    Seq.List (result.filterMap id)

/-- Postcondition: The result is a common subsequence of s1 and s2. -/
def longest_common_subsequence_post {α : Type} [BEq α] (s1 s2 result : Seq α) : Prop :=
  match result with
  | Seq.Str r =>
    -- Result is a string, so s1 and s2 should be strings
    ∃ (s1' s2' : String), 
      s1 = Seq.Str s1' ∧ 
      s2 = Seq.Str s2' ∧
      isSubsequenceOf r s1' ∧
      isSubsequenceOf r s2'
  | Seq.List r =>
    -- Result is a list
    ∃ (l1 l2 : List α),
      (s1 = Seq.List l1 ∨ s1 = Seq.Str (toString l1)) ∧
      (s2 = Seq.List l2 ∨ s2 = Seq.Str (toString l2)) ∧
      isSubsequenceOf r l1 ∧
      isSubsequenceOf r l2
where
  /-- Check if s is a subsequence of t (for strings). -/
  isSubsequenceOf (s t : String) : Prop := 
    isSubsequenceOf s.data t.data
  
  /-- Check if s is a subsequence of t (for lists). -/
  isSubsequenceOf {α : Type} [BEq α] (s t : List α) : Prop :=
    ∃ (indices : List Nat),
      indices.length = s.length ∧
      List.Sorted (· < ·) indices ∧
      List.zipWith (fun x i => t[i]? = some x) s indices |>.all id

/-- Length of the longest common subsequence. -/
def lcs_length {α : Type} [BEq α] (s1 s2 : Seq α) : Nat :=
  let l1 := s1.toList
  let l2 := s2.toList
  
  let m := l1.length
  let n := l2.length
  
  -- Create and fill DP table for lengths only
  let dp := Array.mkArray (m + 1) (Array.mkArray (n + 1) 0)
  let dp := (List.range (m+1)).foldl (fun dp i => 
    (List.range (n+1)).foldl (fun dp j => 
      if i = 0 || j = 0 then 
        dp 
      else if l1[i-1]? = l2[j-1]? then
        dp.set! i j (dp[i-1]![j-1]! + 1)
      else
        let prev1 := dp[i-1]![j]!
        let prev2 := dp[i][j-1]!
        dp.set! i j (max prev1 prev2)
    ) dp
  ) dp
  
  dp[m]![n]!

/-- Correctness theorem for longest_common_subsequence. -/
theorem longest_common_subsequence_correct {α : Type} [BEq α] (s1 s2 : Seq α) 
  (h : longest_common_subsequence_pre s1 s2) : 
  longest_common_subsequence_post s1 s2 (longest_common_subsequence s1 s2) := by
  sorry

/-- Test cases for longest_common_subsequence. -/
def testLCS : IO Unit := do
  -- Test with strings
  let testStr1 := longest_common_subsequence (Seq.Str "ABCDGH") (Seq.Str "AEDFHR")
  match testStr1 with
  | Seq.Str s => IO.println s -- Should print "ADH"
  | _ => IO.println "Unexpected result type"

  -- Test with lists
  let testList1 := longest_common_subsequence (Seq.List [1, 2, 3, 4]) (Seq.List [1, 3, 5])
  match testList1 with
  | Seq.List l => IO.println l -- Should print [1, 3]
  | _ => IO.println "Unexpected result type"

  -- Test with empty inputs
  let testEmpty := longest_common_subsequence (Seq.Str "") (Seq.Str "abc")
  match testEmpty with
  | Seq.Str s => IO.println s -- Should print ""
  | _ => IO.println "Unexpected result type"

  -- Test length function
  IO.println (lcs_length (Seq.Str "ABCDGH") (Seq.Str "AEDFHR")) -- Should print 3
  IO.println (lcs_length (Seq.List [1, 2, 3, 4]) (Seq.List [1, 3, 5])) -- Should print 2

/-- Run the tests. -/
#eval testLCS
