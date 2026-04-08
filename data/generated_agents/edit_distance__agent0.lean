import Mathlib.Data.List.Basic
import Mathlib.Tactic.Linarith

/-!
# Edit Distance (Levenshtein Distance)

This module provides a function to calculate the edit distance between two lists.
-/

namespace EditDistance

/-- Type to represent valid inputs to the edit_distance function -/
inductive Sequence (α : Type)
  | fromList : List α → Sequence α

/-- Convert a Sequence back to a List -/
def Sequence.toList {α : Type} : Sequence α → List α
  | Sequence.fromList l => l

/-- Compute the edit distance between two sequences -/
def edit_distance {α : Type} [BEq α] (s1 s2 : Sequence α) : Nat :=
  let l1 := s1.toList
  let l2 := s2.toList
  let m := l1.length
  let n := l2.length
  
  -- Create and initialize the DP table
  let initDp : Array (Array Nat) := 
    Array.mkArray (m + 1) (Array.mkArray (n + 1) 0)
      |> Array.mapIdx (fun i dp_row => 
          if i == 0 then 
            Array.mapIdx (fun j _ => j) dp_row
          else 
            dp_row.set! 0 i)
  
  -- Helper function to fill the DP table
  let fillDp : Array (Array Nat) → Array (Array Nat) := fun dp =>
    List.foldl (fun dp i =>
      List.foldl (fun dp j =>
        let cost := if l1[i-1]? == l2[j-1]? then 0 else 1
        let newValue := 
          min (dp[i-1]![j]! + 1)            -- deletion
            (min (dp[i]![j-1]! + 1)         -- insertion
                 (dp[i-1]![j-1]! + cost))   -- substitution
        dp.set! i (dp[i]!.set! j newValue)
      ) dp (List.range n |> List.map (· + 1))
    ) dp (List.range m |> List.map (· + 1))
  
  -- Fill the table and return the result
  let finalDp := fillDp initDp
  finalDp[m]![n]!

/-- Predicate that specifies the expected behavior of edit_distance -/
def edit_distance_spec {α : Type} [BEq α] (s1 s2 : Sequence α) (result : Nat) : Prop :=
  let l1 := s1.toList
  let l2 := s2.toList

  -- Base cases
  (l1.isEmpty → result = l2.length) ∧
  (l2.isEmpty → result = l1.length) ∧
  
  -- General case: result is the minimum number of operations
  result ≤ l1.length + l2.length ∧  -- Upper bound
  
  -- For non-empty lists, recursive relation holds
  (l1.length > 0 ∧ l2.length > 0 →
    (l1.head? = l2.head? → 
      result = edit_distance (Sequence.fromList l1.tail) (Sequence.fromList l2.tail)) ∧
    (l1.head? ≠ l2.head? → 
      result = 1 + min 
        (min
          (edit_distance (Sequence.fromList l1.tail) s2)                   -- deletion
          (edit_distance s1 (Sequence.fromList l2.tail)))                  -- insertion
        (edit_distance (Sequence.fromList l1.tail) (Sequence.fromList l2.tail)) -- substitution
    )
  )

/-- Correctness theorem for edit_distance -/
theorem edit_distance_correct {α : Type} [BEq α] (s1 s2 : Sequence α) : 
  edit_distance_spec s1 s2 (edit_distance s1 s2) := by
  sorry

/-- Tests for edit_distance -/
def test : IO Unit := do
  -- Basic functionality tests with strings
  assert! (edit_distance (Sequence.fromList ['h', 'e', 'l', 'l', 'o']) (Sequence.fromList ['h', 'e', 'l', 'l', 'o'])) = 0
  assert! (edit_distance (Sequence.fromList ['c', 'a', 't']) (Sequence.fromList ['b', 'a', 't'])) = 1
  assert! (edit_distance (Sequence.fromList ['c', 'a', 't']) (Sequence.fromList ['c', 'a', 't', 's'])) = 1
  assert! (edit_distance (Sequence.fromList ['c', 'a', 't', 's']) (Sequence.fromList ['c', 'a', 't'])) = 1
  assert! (edit_distance (Sequence.fromList ['c', 'a', 't']) (Sequence.fromList ['d', 'o', 'g'])) = 3
  assert! (edit_distance (Sequence.fromList ['k', 'i', 't', 't', 'e', 'n']) (Sequence.fromList ['s', 'i', 't', 't', 'i', 'n', 'g'])) = 3
  
  -- Edge cases
  assert! (edit_distance (Sequence.fromList []) (Sequence.fromList [])) = 0
  assert! (edit_distance (Sequence.fromList []) (Sequence.fromList ['a', 'b', 'c'])) = 3
  assert! (edit_distance (Sequence.fromList ['a', 'b']) (Sequence.fromList [])) = 2
  assert! (edit_distance (Sequence.fromList ['a']) (Sequence.fromList ['b'])) = 1
  
  -- Test with lists of integers
  assert! (edit_distance (Sequence.fromList [1, 2, 3]) (Sequence.fromList [1, 2, 3])) = 0
  assert! (edit_distance (Sequence.fromList [1, 2, 3]) (Sequence.fromList [1, 4, 3])) = 1
  assert! (edit_distance (Sequence.fromList [1, 2, 3, 4]) (Sequence.fromList [1, 3, 4])) = 1
  assert! (edit_distance (Sequence.fromList [1, 2, 3]) (Sequence.fromList [4, 5, 6])) = 3
  assert! (edit_distance (Sequence.fromList [1, 2, 3, 4, 5]) (Sequence.fromList [6, 7, 8])) = 5
  
  -- Longer sequences
  assert! (edit_distance (Sequence.fromList ['i', 'n', 't', 'e', 'n', 't', 'i', 'o', 'n']) 
                         (Sequence.fromList ['e', 'x', 'e', 'c', 'u', 't', 'i', 'o', 'n'])) = 5
  assert! (edit_distance (Sequence.fromList ['s', 'a', 't', 'u', 'r', 'd', 'a', 'y']) 
                         (Sequence.fromList ['s', 'u', 'n', 'd', 'a', 'y'])) = 3
  
  -- Same length, all different
  assert! (edit_distance (Sequence.fromList ['a', 'b', 'c']) (Sequence.fromList ['d', 'e', 'f'])) = 3
  assert! (edit_distance (Sequence.fromList ['x', 'y', 'z']) (Sequence.fromList ['a', 'b', 'c'])) = 3
  
  -- One character strings
  assert! (edit_distance (Sequence.fromList ['a']) (Sequence.fromList ['a'])) = 0
  assert! (edit_distance (Sequence.fromList ['a']) (Sequence.fromList ['b'])) = 1
  assert! (edit_distance (Sequence.fromList ['a']) (Sequence.fromList [])) = 1
  assert! (edit_distance (Sequence.fromList []) (Sequence.fromList ['a'])) = 1
  
  -- Repeated characters
  assert! (edit_distance (Sequence.fromList ['a', 'a', 'a']) (Sequence.fromList ['a', 'a'])) = 1
  assert! (edit_distance (Sequence.fromList ['a', 'a']) (Sequence.fromList ['a', 'a', 'a'])) = 1
  assert! (edit_distance (Sequence.fromList ['a', 'a', 'a', 'a']) (Sequence.fromList ['b', 'b', 'b', 'b'])) = 4
  
  IO.println "All tests passed!"

end EditDistance
