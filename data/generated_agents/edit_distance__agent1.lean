import Std.Data.List.Basic
import Mathlib.Data.List.MinLength

namespace EditDistance

inductive Sequence (α : Type)
  | string : List α → Sequence α

def Sequence.isEmpty {α : Type} : Sequence α → Bool
  | Sequence.string [] => true
  | _ => false

def Sequence.length {α : Type} : Sequence α → Nat
  | Sequence.string xs => xs.length

def Sequence.fromString (s : String) : Sequence Char :=
  Sequence.string s.data

def Sequence.fromList {α : Type} (xs : List α) : Sequence α :=
  Sequence.string xs

def Sequence.toList {α : Type} : Sequence α → List α
  | Sequence.string xs => xs

def Sequence.get? {α : Type} (seq : Sequence α) (i : Nat) : Option α :=
  match seq with
  | Sequence.string xs => xs.get? i

def pre {α : Type} (s1 s2 : Sequence α) : Prop := True

def editDistance {α : Type} [DecidableEq α] (s1 s2 : Sequence α) : Nat :=
  let list1 := Sequence.toList s1
  let list2 := Sequence.toList s2
  
  let m := list1.length
  let n := list2.length
  
  -- Create a DP table initialized with zeros
  let rec buildTable (i : Nat) (j : Nat) (dp : List (List Nat)) : List (List Nat) :=
    if i > m then dp
    else if j > n then buildTable (i+1) 0 (dp.set! i (List.replicate (n+1) 0))
    else
      let newDpRow := 
        if j == 0 then
          -- First column: number of deletions
          dp.get! i |>.set! 0 i
        else if i == 0 then
          -- First row: number of insertions
          dp.get! 0 |>.set! j j
        else
          let dpRow := dp.get! i
          let dpPrevRow := dp.get! (i-1)
          if list1.get! (i-1) == list2.get! (j-1) then
            -- No operation needed
            dpRow.set! j (dpPrevRow.get! (j-1))
          else
            -- Minimum of deletion, insertion, substitution
            let deletion := dpPrevRow.get! j
            let insertion := dpRow.get! (j-1)
            let substitution := dpPrevRow.get! (j-1)
            dpRow.set! j (1 + min deletion (min insertion substitution))
      
      let newDp := dp.set! i newDpRow
      
      if j < n then buildTable i (j+1) newDp
      else buildTable (i+1) 0 newDp
  
  -- Initialize DP table with zeros
  let initialDp := List.replicate (m+1) (List.replicate (n+1) 0)
  
  -- Fill the DP table and return the bottom-right value
  let finalDp := buildTable 0 0 initialDp
  finalDp.get! m |>.get! n

def post {α : Type} [DecidableEq α] (s1 s2 : Sequence α) (result : Nat) : Prop :=
  -- The result is non-negative
  result ≥ 0 ∧
  -- If sequences are identical, distance is 0
  (s1 = s2 → result = 0) ∧
  -- If one sequence is empty, distance is length of the other
  (Sequence.isEmpty s1 → result = Sequence.length s2) ∧
  (Sequence.isEmpty s2 → result = Sequence.length s1) ∧
  -- Triangle inequality
  result ≤ Sequence.length s1 + Sequence.length s2

theorem editDistance_correct {α : Type} [DecidableEq α] (s1 s2 : Sequence α) 
    (h : pre s1 s2) : post s1 s2 (editDistance s1 s2) := by
  sorry

-- Tests
def test : IO Unit := do
  -- String tests
  let s1 := Sequence.fromString "hello"
  let s2 := Sequence.fromString "hello"
  IO.println s!"Test 1: {editDistance s1 s2}" -- Expected: 0
  
  let s3 := Sequence.fromString "cat"
  let s4 := Sequence.fromString "bat"
  IO.println s!"Test 2: {editDistance s3 s4}" -- Expected: 1
  
  let s5 := Sequence.fromString "cat"
  let s6 := Sequence.fromString "cats"
  IO.println s!"Test 3: {editDistance s5 s6}" -- Expected: 1
  
  let s7 := Sequence.fromString "cats"
  let s8 := Sequence.fromString "cat"
  IO.println s!"Test 4: {editDistance s7 s8}" -- Expected: 1
  
  let s9 := Sequence.fromString "cat"
  let s10 := Sequence.fromString "dog"
  IO.println s!"Test 5: {editDistance s9 s10}" -- Expected: 3
  
  let s11 := Sequence.fromString "kitten"
  let s12 := Sequence.fromString "sitting"
  IO.println s!"Test 6: {editDistance s11 s12}" -- Expected: 3
  
  -- Edge cases
  let s13 := Sequence.fromString ""
  let s14 := Sequence.fromString ""
  IO.println s!"Test 7: {editDistance s13 s14}" -- Expected: 0
  
  let s15 := Sequence.fromString ""
  let s16 := Sequence.fromString "abc"
  IO.println s!"Test 8: {editDistance s15 s16}" -- Expected: 3
  
  -- Integer list tests
  let l1 := Sequence.fromList [1, 2, 3]
  let l2 := Sequence.fromList [1, 2, 3]
  IO.println s!"Test 9: {editDistance l1 l2}" -- Expected: 0
  
  let l3 := Sequence.fromList [1, 2, 3]
  let l4 := Sequence.fromList [1, 4, 3]
  IO.println s!"Test 10: {editDistance l3 l4}" -- Expected: 1

end EditDistance
