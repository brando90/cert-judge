import Std.Data.List
open Std.Data.List

namespace VeriBench.BisectLeft

def bisect_left {α β : Type} [LT α] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) : Nat :=
  if lo < 0 then
    0 -- Lean doesn't allow negative indices, so we return 0 instead of raising an error
  else
    let hi' := match hi with
      | none => a.length
      | some h => h
    
    let rec search (lo : Nat) (hi : Nat) : Nat :=
      if lo >= hi then
        lo
      else
        let mid := (lo + hi) / 2
        if a[mid]! < x then
          search (mid + 1) hi
        else
          search lo mid
    
    search lo hi'

def bisect_left_key {α β : Type} [LT β] (a : List α) (x : β) (lo : Nat := 0) (hi : Option Nat := none) (key : α → β) : Nat :=
  if lo < 0 then
    0 -- Lean doesn't allow negative indices, so we return 0 instead of raising an error
  else
    let hi' := match hi with
      | none => a.length
      | some h => h
    
    let rec search (lo : Nat) (hi : Nat) : Nat :=
      if lo >= hi then
        lo
      else
        let mid := (lo + hi) / 2
        if key (a[mid]!) < x then
          search (mid + 1) hi
        else
          search lo mid
    
    search lo hi'

def insort_left {α : Type} [LT α] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) : List α :=
  let idx := bisect_left a x lo hi
  a.insertAt idx x

def insort_left_key {α β : Type} [LT β] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) (key : α → β) : List α :=
  let idx := bisect_left_key a (key x) lo hi key
  a.insertAt idx x

/-- bisect_left returns an index i where all elements a[:i] < x and all elements a[i:] >= x -/
def bisect_left_spec {α : Type} [LT α] (a : List α) (x : α) (lo : Nat) (hi : Option Nat) (result : Nat) : Prop :=
  let hi' := match hi with
    | none => a.length
    | some h => h
  
  lo <= result ∧ result <= hi' ∧
  (∀ i, lo <= i ∧ i < result → a[i]! < x) ∧
  (∀ i, result <= i ∧ i < hi' → ¬(a[i]! < x))

/-- bisect_left_key returns an index i where all elements key(a[:i]) < x and all elements key(a[i:]) >= x -/
def bisect_left_key_spec {α β : Type} [LT β] (a : List α) (x : β) (lo : Nat) (hi : Option Nat) (key : α → β) (result : Nat) : Prop :=
  let hi' := match hi with
    | none => a.length
    | some h => h
  
  lo <= result ∧ result <= hi' ∧
  (∀ i, lo <= i ∧ i < result → key (a[i]!) < x) ∧
  (∀ i, result <= i ∧ i < hi' → ¬(key (a[i]!) < x))

theorem bisect_left_correct {α : Type} [LT α] (a : List α) (x : α) (lo : Nat) (hi : Option Nat) :
  bisect_left_spec a x lo hi (bisect_left a x lo hi) := by
  sorry

theorem bisect_left_key_correct {α β : Type} [LT β] (a : List α) (x : β) (lo : Nat) (hi : Option Nat) (key : α → β) :
  bisect_left_key_spec a x lo hi key (bisect_left_key a x lo hi key) := by
  sorry

/-- insort_left inserts x into a sorted list a, maintaining the sort order -/
def insort_left_spec {α : Type} [LT α] [DecidableRel (α := α) LT.lt] (a : List α) (x : α) (lo : Nat) (hi : Option Nat) (result : List α) : Prop :=
  -- Result has one more element than a
  result.length = a.length + 1 ∧
  -- Result contains x
  x ∈ result ∧
  -- Result is sorted if a was sorted
  (List.Sorted LT.lt a → List.Sorted LT.lt result)

theorem insort_left_correct {α : Type} [LT α] [DecidableRel (α := α) LT.lt] (a : List α) (x : α) (lo : Nat) (hi : Option Nat) :
  insort_left_spec a x lo hi (insort_left a x lo hi) := by
  sorry

/-- Tests for bisect_left -/
def test_bisect_left : Bool :=
  -- Basic tests
  let t1 := bisect_left [1, 2, 4, 4, 10] 4 == 2
  let t2 := bisect_left [1, 2, 4, 4, 10] 0 == 0
  let t3 := bisect_left [1, 2, 4, 4, 10] 99 == 5
  
  -- With key function
  let strList := ["A", "bb", "CC", "ddd"]
  let t4 := bisect_left_key strList 1 0 none String.length == 0
  let t5 := bisect_left_key strList 2 0 none String.length == 1
  let t6 := bisect_left_key strList 3 0 none String.length == 3
  
  t1 && t2 && t3 && t4 && t5 && t6

/-- Tests for insort_left -/
def test_insort_left : Bool :=
  let lst1 := insort_left [1, 2, 4, 4, 10] 4
  let t1 := lst1 == [1, 2, 4, 4, 4, 10]
  
  t1

#eval test_bisect_left
#eval test_insort_left

end VeriBench.BisectLeft
