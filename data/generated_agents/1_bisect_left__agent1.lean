```lean
import Mathlib.Data.List.Basic
import Mathlib.Data.List.Lemmas

universe u v

namespace VeriBench

/--
  Return the index where to insert item x in list a, assuming a is sorted.

  The return value i is such that all e in a[:i] have e < x, and all e in
  a[i:] have e >= x.  So if x already appears in the list, a.insert(i, x) will
  insert just before the leftmost x already there.

  Optional args lo (default 0) and hi (default len(a)) bound the
  slice of a to be searched.

  A custom key function can be supplied to customize the sort order.
-/
def bisect_left {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : β) (lo : Nat := 0) (hi : Option Nat := none) 
    (key : Option (α → β) := none) : Nat :=
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let hi' := match hi with
      | none => a.length
      | some h => h
    match key with
    | none => 
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if a[mid]! < x then
            loop (mid + 1) hi
          else
            loop lo mid
        else
          lo
      loop lo hi'
    | some k => 
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if k (a[mid]!) < x then
            loop (mid + 1) hi
          else
            loop lo mid
        else
          lo
      loop lo hi'

/--
  Insert item x in list a, and keep it sorted assuming a is sorted.

  If x is already in a, insert it to the left of the leftmost x.

  Optional args lo (default 0) and hi (default len(a)) bound the
  slice of a to be searched.

  A custom key function can be supplied to customize the sort order.
-/
def insort_left {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) 
    (key : Option (α → β) := none) : List α :=
  let idx := match key with
    | none => bisect_left a x lo hi none
    | some k => bisect_left a (k x) lo hi key
  a.insertAt idx x

section Tests

def check_bisect : Bool :=
  -- Basic
  let test1 := bisect_left [1, 2, 4, 4, 10] 4 == 2
  let test2 := bisect_left [1, 2, 4, 4, 10] 0 == 0
  let test3 := bisect_left [1, 2, 4, 4, 10] 99 == 5

  -- With key=len on strings, compare in key space
  let key := fun s : String => s.length
  let cand_with_key (a : List String) (k : Nat) : Nat :=
    bisect_left a k 0 none (some key)

  -- lengths are [1, 2, 2, 3]
  let test4 := cand_with_key ["A", "bb", "CC", "ddd"] 1 == 0  -- first index with len >= 1
  let test5 := cand_with_key ["A", "bb", "CC", "ddd"] 2 == 1  -- first index with len >= 2
  let test6 := cand_with_key ["A", "bb", "CC", "ddd"] 3 == 3  -- first index with len >= 3

  test1 && test2 && test3 && test4 && test5 && test6

def check_insort : Bool :=
  let lst := insort_left [1, 2, 4, 4, 10] 4
  let test1 := lst == [1, 2, 4, 4, 4, 10]

  let strLower (s : String) : String := s.toLower
  let lst2 := insort_left ["A", "bb", "CC", "ddd"] "cC" (key := some strLower)
  let test2 := lst2 == ["A", "bb", "cC", "CC", "ddd"]
  
  test1 && test2

#eval check_bisect
#eval check_insort

end Tests

section Specification

/-- Precondition for bisect_left: lo must be non-negative and hi must be at most the length of the list -/
def bisect_left_pre {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : β) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) : Prop :=
  lo ≥ 0 ∧ match hi with
  | none => true
  | some h => h ≤ a.length

/-- 
  Postcondition for bisect_left: 
  1. The returned index is between lo and hi (or list length if hi is none)
  2. All elements before the index are < x (in key space if key is provided)
  3. All elements at or after the index are ≥ x (in key space if key is provided)
-/
def bisect_left_post {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : β) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) (result : Nat) : Prop :=
  let hi' := match hi with
  | none => a.length
  | some h => h
  
  result ≥ lo ∧ result ≤ hi' ∧
  match key with
  | none => 
    (∀ i, lo ≤ i → i < result → a[i]! < x) ∧
    (∀ i, result ≤ i → i < hi' → ¬(a[i]! < x))
  | some k => 
    (∀ i, lo ≤ i → i < result → k a[i]! < x) ∧
    (∀ i, result ≤ i → i < hi' → ¬(k a[i]! < x))

/-- Precondition for insort_left: same as bisect_left -/
def insort_left_pre {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : α) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) : Prop :=
  bisect_left_pre a x lo hi key

/-- 
  Postcondition for insort_left:
  1. The result is the original list with x inserted at the correct position
  2. If the list was sorted, the result remains sorted
-/
def insort_left_post {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : α) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) (result : List α) : Prop :=
  let idx := match key with
    | none => bisect_left a x lo hi none
    | some k => bisect_left a (k x) lo hi key
  
  result = a.insertAt idx x ∧
  (List.Sorted (·<·) a → List.Sorted (·<·) result)

theorem bisect_left_correct {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : β) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) :
    bisect_left_pre a x lo hi key → 
    bisect_left_post a x lo hi key (bisect_left a x lo hi key) :=
  sorry

theorem insort_left_correct {α : Type u} {β : Type v} [LT α] [LT β] 
    (a : List α) (x : α) (lo : Nat) (hi : Option Nat) 
    (key : Option (α → β)) :
    insort_left_pre a x lo hi key → 
    insort_left_post a x lo hi key (insort_left a x lo hi key) :=
  sorry

end Specification

end VeriBench
```
