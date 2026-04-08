import Mathlib.Data.List.Basic
import Mathlib.Tactic.Basic

namespace BisectInsort

/-- 
Return the index where to insert item x in list a, assuming a is sorted.

The return value i is such that all e in a[:i] have e <= x, and all e in
a[i:] have e > x.  So if x already appears in the list, a.insert(i, x) will
insert just after the rightmost x already there.

Optional args lo (default 0) and hi (default len(a)) bound the
slice of a to be searched.

A custom key function can be supplied to customize the sort order.
-/
def bisectRight {α β : Type} [Ord β] (a : List α) (x : β) (lo : Nat := 0) (hi : Option Nat := none) 
    (key : Option (α → β) := none) : Nat :=
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let hi := match hi with
      | none => a.length
      | some h => h
    match key with
    | none =>
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if x < a[mid]! then
            loop lo mid
          else
            loop (mid + 1) hi
        else
          lo
      loop lo hi
    | some k =>
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if x < k (a[mid]!) then
            loop lo mid
          else
            loop (mid + 1) hi
        else
          lo
      loop lo hi

/--
Insert item x in list a, and keep it sorted assuming a is sorted.

If x is already in a, insert it to the right of the rightmost x.

Optional args lo (default 0) and hi (default len(a)) bound the
slice of a to be searched.

A custom key function can be supplied to customize the sort order.
-/
def insortRight {α β : Type} [Ord β] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none)
    (key : Option (α → β) := none) : List α :=
  let idx := match key with
    | none => bisectRight a x lo hi none
    | some k => bisectRight a (k x) lo hi key
  a.insertAt idx x

/-- Specification: bisectRight returns an index where all elements before it are ≤ x 
    and all elements after it are > x -/
def bisectRightSpec {α : Type} [Ord α] (a : List α) (x : α) (lo hi : Nat) (result : Nat) : Prop :=
  lo ≤ result ∧ result ≤ hi ∧
  (∀ i, lo ≤ i ∧ i < result → a[i]! ≤ x) ∧
  (∀ i, result ≤ i ∧ i < hi → x < a[i]!)

/-- Specification with key function: bisectRight returns an index where all elements 
    before it have key ≤ x and all elements after it have key > x -/
def bisectRightKeySpec {α β : Type} [Ord β] (a : List α) (x : β) (lo hi : Nat) (key : α → β) (result : Nat) : Prop :=
  lo ≤ result ∧ result ≤ hi ∧
  (∀ i, lo ≤ i ∧ i < result → key (a[i]!) ≤ x) ∧
  (∀ i, result ≤ i ∧ i < hi → x < key (a[i]!))

/-- Specification: insortRight inserts x at the right position in a sorted list -/
def insortRightSpec {α : Type} [Ord α] (a : List α) (x : α) (result : List α) : Prop :=
  ∃ idx, result = a.insertAt idx x ∧
  (∀ i, i < idx → a[i]! ≤ x) ∧
  (∀ i, idx ≤ i ∧ i < a.length → x < a[i]!)

/-- Theorem: bisectRight satisfies its specification -/
theorem bisectRight_correct {α : Type} [Ord α] (a : List α) (x : α) (lo hi : Nat) 
    (h1 : lo ≤ hi) (h2 : hi ≤ a.length) :
    bisectRightSpec a x lo hi (bisectRight a x lo (some hi) none) := by
  sorry

/-- Theorem: bisectRight with key function satisfies its specification -/
theorem bisectRight_key_correct {α β : Type} [Ord β] (a : List α) (x : β) (lo hi : Nat) (key : α → β)
    (h1 : lo ≤ hi) (h2 : hi ≤ a.length) :
    bisectRightKeySpec a x lo hi key (bisectRight a x lo (some hi) (some key)) := by
  sorry

/-- Theorem: insortRight satisfies its specification -/
theorem insortRight_correct {α : Type} [Ord α] (a : List α) (x : α) :
    insortRightSpec a x (insortRight a x) := by
  sorry

/-- Test cases for bisectRight -/
def test_bisect_right : Bool :=
  -- Basic tests
  bisectRight [1, 2, 4, 4, 10] 4 == 4 &&
  bisectRight [1, 2, 4, 4, 10] 0 == 0 &&
  bisectRight [1, 2, 4, 4, 10] 99 == 5 &&
  
  -- With key function (length)
  let stringList := ["A", "bb", "CC", "ddd"]
  let key := (fun s => s.length)
  bisectRight stringList 1 0 none (some key) == 1 &&
  bisectRight stringList 2 0 none (some key) == 3 &&
  bisectRight stringList 3 0 none (some key) == 4

/-- Test cases for insortRight -/
def test_insort_right : Bool :=
  let lst1 := [1, 2, 4, 4, 10]
  insortRight lst1 4 == [1, 2, 4, 4, 4, 10] &&
  
  let lst2 := ["A", "bb", "CC", "ddd"]
  let key := (fun s => s.toLower)
  insortRight lst2 "cC" 0 none (some key) == ["A", "bb", "CC", "cC", "ddd"]

#eval test_bisect_right
#eval test_insort_right

end BisectInsort
