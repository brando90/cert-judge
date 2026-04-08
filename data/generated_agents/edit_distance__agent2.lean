import Lean.Data.Array
import Std.Data.List.Basic

namespace EditDistance

inductive Sequence
| String : String → Sequence
| ListInt : List Int → Sequence
| ListChar : List Char → Sequence

def pre (s1 s2 : Sequence) : Prop := True

/--
Computes the edit distance (Levenshtein distance) between two sequences.
The edit distance is the minimum number of single-element edits
(insertions, deletions, or substitutions) required to change one sequence into another.
-/
def editDistance (s1 s2 : Sequence) : Int :=
  match s1, s2 with
  | Sequence.String str1, Sequence.String str2 => 
    let list1 := str1.toList
    let list2 := str2.toList
    editDistanceList list1 list2
  | Sequence.ListInt list1, Sequence.ListInt list2 => 
    editDistanceList list1 list2
  | Sequence.ListChar list1, Sequence.ListChar list2 => 
    editDistanceList list1 list2
  | _, _ => 0 -- This case doesn't happen in valid inputs
where
  editDistanceList {α : Type} [BEq α] (s1 s2 : List α) : Int :=
    let m := s1.length
    let n := s2.length
    
    -- Create and initialize DP table
    let mut dp := Array.mkArray (m+1) (Array.mkArray (n+1) 0)
    
    -- Initialize base cases
    for i in [:m+1] do
      dp := dp.set! i (dp[i]!.set! 0 i)
    
    for j in [:n+1] do
      dp := dp.set! 0 (dp[0]!.set! j j)
    
    -- Fill the DP table
    for i in [1:m+1] do
      for j in [1:n+1] do
        let cost := if s1[i-1]! == s2[j-1]! then 0 else 1
        let val := min (dp[i-1]![j]! + 1) (min (dp[i]![j-1]! + 1) (dp[i-1]![j-1]! + cost))
        dp := dp.set! i (dp[i]!.set! j val)
    
    dp[m]![n]!

/-- Post-condition: edit distance is non-negative -/
def post (s1 s2 : Sequence) (result : Int) : Prop :=
  result ≥ 0

theorem editDistance_correct (s1 s2 : Sequence) (h : pre s1 s2) :
  post s1 s2 (editDistance s1 s2) := sorry

/-- Test cases for edit distance -/
def test : IO Unit := do
  -- Basic functionality tests with strings
  assert! (editDistance (Sequence.String "hello") (Sequence.String "hello") = 0)
  assert! (editDistance (Sequence.String "cat") (Sequence.String "bat") = 1)
  assert! (editDistance (Sequence.String "cat") (Sequence.String "cats") = 1)
  assert! (editDistance (Sequence.String "cats") (Sequence.String "cat") = 1)
  assert! (editDistance (Sequence.String "cat") (Sequence.String "dog") = 3)
  assert! (editDistance (Sequence.String "kitten") (Sequence.String "sitting") = 3)
  
  -- Edge cases
  assert! (editDistance (Sequence.String "") (Sequence.String "") = 0)
  assert! (editDistance (Sequence.String "") (Sequence.String "abc") = 3)
  assert! (editDistance (Sequence.String "ab") (Sequence.String "") = 2)
  assert! (editDistance (Sequence.String "a") (Sequence.String "b") = 1)
  
  -- Test with lists of integers
  assert! (editDistance (Sequence.ListInt [1, 2, 3]) (Sequence.ListInt [1, 2, 3]) = 0)
  assert! (editDistance (Sequence.ListInt [1, 2, 3]) (Sequence.ListInt [1, 4, 3]) = 1)
  assert! (editDistance (Sequence.ListInt [1, 2, 3, 4]) (Sequence.ListInt [1, 3, 4]) = 1)
  assert! (editDistance (Sequence.ListInt [1, 2, 3]) (Sequence.ListInt [4, 5, 6]) = 3)
  assert! (editDistance (Sequence.ListInt [1, 2, 3, 4, 5]) (Sequence.ListInt [6, 7, 8]) = 5)
  
  -- Test with character lists
  assert! (editDistance (Sequence.ListChar ['h', 'e', 'l', 'l', 'o']) (Sequence.ListChar ['h', 'e', 'l', 'l', 'o']) = 0)
  assert! (editDistance (Sequence.ListChar ['c', 'a', 't']) (Sequence.ListChar ['b', 'a', 't']) = 1)
  assert! (editDistance (Sequence.ListChar ['c', 'a', 't']) (Sequence.ListChar ['c', 'a', 't', 's']) = 1)
  assert! (editDistance (Sequence.ListChar ['c', 'a', 't', 's']) (Sequence.ListChar ['c', 'a', 't']) = 1)
  
  -- Longer sequences
  assert! (editDistance (Sequence.String "intention") (Sequence.String "execution") = 5)
  assert! (editDistance (Sequence.String "saturday") (Sequence.String "sunday") = 3)
  
  -- Same length, all different
  assert! (editDistance (Sequence.String "abc") (Sequence.String "def") = 3)
  assert! (editDistance (Sequence.String "xyz") (Sequence.String "abc") = 3)
  
  -- One character strings
  assert! (editDistance (Sequence.String "a") (Sequence.String "a") = 0)
  assert! (editDistance (Sequence.String "a") (Sequence.String "b") = 1)
  assert! (editDistance (Sequence.String "a") (Sequence.String "") = 1)
  assert! (editDistance (Sequence.String "") (Sequence.String "a") = 1)
  
  -- Repeated characters
  assert! (editDistance (Sequence.String "aaa") (Sequence.String "aa") = 1)
  assert! (editDistance (Sequence.String "aa") (Sequence.String "aaa") = 1)
  assert! (editDistance (Sequence.String "aaaa") (Sequence.String "bbbb") = 4)
  
  IO.println "All tests passed!"

#eval test

end EditDistance
