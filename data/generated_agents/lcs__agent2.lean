import Mathlib.Data.List.Basic

namespace VeriBench.LongestCommonSubsequence

/-!
# Longest Common Subsequence (LCS)

This module implements the longest common subsequence (LCS) algorithm
for lists using dynamic programming.

A subsequence is a sequence that can be derived from another sequence 
by deleting some or no elements without changing the order of the remaining elements.
-/

/--
Check if a subsequence is valid - meaning it can be derived by removing elements
from the original sequence without changing order.
-/
def isSubsequence {α : Type} [BEq α] (sub : List α) (orig : List α) : Bool :=
  let rec check (s : List α) (o : List α) : Bool :=
    match s, o with
    | [], _ => true
    | _, [] => false
    | x::xs, y::ys => if x == y then check xs ys else check s ys
  check sub orig

/--
Calculate the length of the longest common subsequence between two lists.
This is more efficient than computing the full subsequence when only the length is needed.
-/
def lcsLength {α : Type} [BEq α] (s1 s2 : List α) : Nat :=
  let m := s1.length
  let n := s2.length
  
  let rec buildTable (i j : Nat) (table : Array (Array Nat)) : Array (Array Nat) :=
    if i > m then table
    else if j > n then buildTable (i+1) 1 table
    else
      let newVal := 
        if i == 0 || j == 0 then 0
        else if s1[i-1]! == s2[j-1]! then table[i-1]![j-1]! + 1
        else Nat.max table[i-1]![j]! table[i]![j-1]!
      
      let newRow := if j == 1 then table.push (Array.mkArray (n+1) 0) else table
      let updatedTable := newRow.modify i (fun row => row.set! j newVal)
      buildTable i (j+1) updatedTable
  
  let initialTable := Array.mkArray 1 (Array.mkArray (n+1) 0)
  (buildTable 1 1 initialTable)[m]![n]!

/--
Find the longest common subsequence of two lists using dynamic programming.
Returns a list that is a subsequence of both input lists with maximum length.
-/
def longestCommonSubsequence {α : Type} [BEq α] (s1 s2 : List α) : List α :=
  let m := s1.length
  let n := s2.length
  
  -- First build a table of LCS lengths
  let rec buildTable (i j : Nat) (table : Array (Array Nat)) : Array (Array Nat) :=
    if i > m then table
    else if j > n then buildTable (i+1) 1 table
    else
      let newVal := 
        if i == 0 || j == 0 then 0
        else if s1[i-1]! == s2[j-1]! then table[i-1]![j-1]! + 1
        else Nat.max table[i-1]![j]! table[i]![j-1]!
      
      let newRow := if j == 1 then table.push (Array.mkArray (n+1) 0) else table
      let updatedTable := newRow.modify i (fun row => row.set! j newVal)
      buildTable i (j+1) updatedTable
  
  let initialTable := Array.mkArray 1 (Array.mkArray (n+1) 0)
  let table := buildTable 1 1 initialTable
  
  -- Backtrack to find the actual LCS
  let rec backtrack (i j : Nat) (result : List α) : List α :=
    if i == 0 || j == 0 then
      result
    else if s1[i-1]! == s2[j-1]! then
      backtrack (i-1) (j-1) (s1[i-1]! :: result)
    else if table[i-1]![j]! > table[i]![j-1]! then
      backtrack (i-1) j result
    else
      backtrack i (j-1) result
  
  backtrack m n []

/--
Precondition for LCS functions: both inputs must be valid lists
-/
def pre {α : Type} [BEq α] (s1 s2 : List α) : Prop := True

/--
Postcondition for LCS function:
1. Result is a subsequence of both inputs
2. Result has maximum possible length
-/
def post {α : Type} [BEq α] (s1 s2 result : List α) : Prop :=
  isSubsequence result s1 = true ∧ 
  isSubsequence result s2 = true ∧
  result.length = lcsLength s1 s2

/--
Theorem: The longestCommonSubsequence function satisfies its postcondition
-/
theorem longestCommonSubsequence_correct {α : Type} [BEq α] (s1 s2 : List α) 
  (h : pre s1 s2) : post s1 s2 (longestCommonSubsequence s1 s2) := by
  sorry

/--
Test cases for the LCS algorithm
-/
def testLongestCommonSubsequence : IO Unit := do
  let test1 := longestCommonSubsequence [1, 2, 3, 4] [1, 3, 5]
  IO.println s!"Test 1: {test1} (expected [1, 3])"
  assert! test1 == [1, 3]
  
  let test2 := longestCommonSubsequence [1, 2, 3, 4, 5] [2, 4, 6]
  IO.println s!"Test 2: {test2} (expected [2, 4])"
  assert! test2 == [2, 4]
  
  let test3 := longestCommonSubsequence [3, 5, 7, 9] [1, 3, 6, 7, 8]
  IO.println s!"Test 3: {test3} (expected [3, 7])"
  assert! test3 == [3, 7]
  
  let test4 := longestCommonSubsequence ([] : List Int) [1, 2, 3]
  IO.println s!"Test 4: {test4} (expected [])"
  assert! test4 == []
  
  let test5 := longestCommonSubsequence [1, 2, 3] ([] : List Int)
  IO.println s!"Test 5: {test5} (expected [])"
  assert! test5 == []
  
  let test6 := longestCommonSubsequence [1] [1, 2]
  IO.println s!"Test 6: {test6} (expected [1])"
  assert! test6 == [1]
  
  let test7 := longestCommonSubsequence [1, 2] [1]
  IO.println s!"Test 7: {test7} (expected [1])"
  assert! test7 == [1]
  
  let test8 := longestCommonSubsequence [1, 2, 3, 4, 5] [1, 2, 3]
  IO.println s!"Test 8: {test8} (expected [1, 2, 3])"
  assert! test8 == [1, 2, 3]
  
  let test9 := longestCommonSubsequence [1, 2, 3, 4, 5, 6] [1, 3, 4, 6, 7, 8]
  IO.println s!"Test 9: {test9} (expected [1, 3, 4, 6])"
  assert! test9 == [1, 3, 4, 6]
  
  let test10 := longestCommonSubsequence [1, 2, 3] [4, 5, 6]
  IO.println s!"Test 10: {test10} (expected [])"
  assert! test10 == []
  
  IO.println "All tests passed!"

/--
Test cases for the LCS length function
-/
def testLcsLength : IO Unit := do
  let test1 := lcsLength [1, 2, 3, 4] [1, 3, 5]
  IO.println s!"Length Test 1: {test1} (expected 2)"
  assert! test1 == 2
  
  let test2 := lcsLength [1, 2, 3, 4, 5] [2, 4, 6]
  IO.println s!"Length Test 2: {test2} (expected 2)"
  assert! test2 == 2
  
  let test3 := lcsLength ([] : List Int) [1, 2, 3]
  IO.println s!"Length Test 3: {test3} (expected 0)"
  assert! test3 == 0
  
  let test4 := lcsLength [1, 2, 3] [1, 2, 3]
  IO.println s!"Length Test 4: {test4} (expected 3)"
  assert! test4 == 3
  
  IO.println "All length tests passed!"

#eval testLongestCommonSubsequence
#eval testLcsLength

end VeriBench.LongestCommonSubsequence
