import Mathlib.Data.List.Sort
import Mathlib.Data.List.Basic
import Mathlib.Data.List.MinMax

open List
namespace EditDistance


def min3 (a b c : Nat) : Nat :=
  min (min a b) c


def editDistanceAux [DecidableEq α] : List α → List α → Nat
  | [], [] => 0
  | [], ys => ys.length  -- insertions
  | xs, [] => xs.length  -- deletions
  | x :: xs, y :: ys =>
    if x = y then
      editDistanceAux xs ys
    else
      1 + min3
        (editDistanceAux xs (y :: ys))    -- deletion
        (editDistanceAux (x :: xs) ys)    -- insertion
        (editDistanceAux xs ys)           -- substitution


def editDistance [DecidableEq α] (s1 s2 : List α) : Nat :=
  editDistanceAux s1 s2


def editDistanceImp [DecidableEq α] (s1 s2 : List α) : Nat :=
  let m := s1.length
  let n := s2.length
  let arr1 := s1.toArray
  let arr2 := s2.toArray
  
  -- Create DP table
  let dp := Array.mkArray (m + 1) (Array.mkArray (n + 1) 0)
  
  -- Initialize base cases
  let dp := (Array.range (m + 1)).foldl (fun acc i => 
    acc.set! i (acc[i]!.set! 0 i)) dp
  let dp := (Array.range (n + 1)).foldl (fun acc j => 
    acc.set! 0 (acc[0]!.set! j j)) dp
    
  -- Fill DP table
  let dp := (Array.range m).foldl (fun acc i =>
    (Array.range n).foldl (fun acc' j =>
      let cost := if arr1[i]! = arr2[j]! then 0 else 1
      let val := min3 
        (acc'[i]![j + 1]! + 1)      -- deletion
        (acc'[i + 1]![j]! + 1)      -- insertion  
        (acc'[i]![j]! + cost)       -- substitution
      acc'.set! (i + 1) (acc'[i + 1]!.set! (j + 1) val)
    ) acc
  ) dp
  
  dp[m]![n]!

-- Lemma for auxiliary function properties

/-!
# Tests
-/

/-- expected: 1 -/
example : editDistance ['c', 'a', 't'] ['b', 'a', 't'] = 1 := by native_decide
#eval editDistance ['c', 'a', 't'] ['b', 'a', 't'] -- expected: 1

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : editDistance ([] : List Char) [] = 0 := by native_decide
#eval editDistance ([] : List Char) [] -- expected: 0

/-- expected: 0 -/
example : editDistance ['h', 'e', 'l', 'l', 'o'] ['h', 'e', 'l', 'l', 'o'] = 0 := by native_decide
#eval editDistance ['h', 'e', 'l', 'l', 'o'] ['h', 'e', 'l', 'l', 'o'] -- expected: 0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single substitution -/
example : editDistance ['c', 'a', 't'] ['b', 'a', 't'] = 1 := by native_decide
#eval editDistance ['c', 'a', 't'] ['b', 'a', 't'] -- expected: 1

/-- positive: single insertion -/
example : editDistance ['c', 'a', 't'] ['c', 'a', 't', 's'] = 1 := by native_decide
#eval editDistance ['c', 'a', 't'] ['c', 'a', 't', 's'] -- expected: 1

/-- negative: not equal to wrong distance -/
example : ¬ (editDistance ['c', 'a', 't'] ['d', 'o', 'g'] = 1) := by native_decide
#eval (decide (editDistance ['c', 'a', 't'] ['d', 'o', 'g'] = 1)) -- expected: false

/-- negative: not zero for different lists -/
example : ¬ (editDistance ['a'] ['b'] = 0) := by native_decide
#eval (decide (editDistance ['a'] ['b'] = 0)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single substitution -/
example : editDistanceImp ['a'] ['b'] = 1 := by native_decide
#eval editDistanceImp ['a'] ['b'] -- expected: 1

/-- negative: not zero for different lists -/
example : ¬ (editDistanceImp ['a'] ['b'] = 0) := by native_decide
#eval (decide (editDistanceImp ['a'] ['b'] = 0)) -- expected: false

/-- **Equivalence theorem**: functional and imperative edit distance coincide. -/
theorem editDistance_equivalence_thm {α : Type*} [DecidableEq α] (s1 s2 : List α) :
  editDistance s1 s2 = editDistanceImp s1 s2 := by
  rfl




end EditDistance