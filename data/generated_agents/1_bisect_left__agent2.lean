```lean
import Std.Data.List.Basic
import Mathlib.Data.List.Sort

def bisectLeft [Ord α] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) : Nat :=
  let hi' := match hi with
    | none => a.length
    | some h => h
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let rec loop (lo hi : Nat) : Nat :=
      if lo < hi then
        let mid := (lo + hi) / 2
        if a[mid]! < x then
          loop (mid + 1) hi
        else
          loop lo mid
      else
        lo
    loop lo hi'

def bisectLeftKey [Ord β] (a : List α) (x : β) (lo : Nat := 0) (hi : Option Nat := none) (key : α → β) : Nat :=
  let hi' := match hi with
    | none => a.length
    | some h => h
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let rec loop (lo hi : Nat) : Nat :=
      if lo < hi then
        let mid := (lo + hi) / 2
        if key a[mid]! < x then
          loop (mid + 1) hi
        else
          loop lo mid
      else
        lo
    loop lo hi'

def insortLeft [Ord α] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) : List α :=
  let idx := bisectLeft a x lo hi
  a.insertAt idx x

def insortLeftKey [Ord β] (a : List α) (x : α) (lo : Nat := 0) (hi : Option Nat := none) (key : α → β) : List α :=
  let idx := bisectLeftKey a (key x) lo hi key
  a.insertAt idx x

-- Specifications and Proofs

/-- The index returned by `bisectLeft` is between `lo` and `hi` -/
theorem bisectLeft_in_range [Ord α] (a : List α) (x : α) (lo hi : Nat) :
  lo ≤ bisectLeft a x lo (some hi) ∧ bisectLeft a x lo (some hi) ≤ hi := by
  sorry

/-- For all elements in a[:i], they are < x -/
theorem bisectLeft_all_lt [Ord α] (a : List α) (x : α) (lo hi : Nat) :
  let i := bisectLeft a x lo (some hi)
  ∀ j, lo ≤ j → j < i → a[j]! < x := by
  sorry

/-- For all elements in a[i:], they are >= x -/
theorem bisectLeft_all_ge [Ord α] (a : List α) (x : α) (lo hi : Nat) :
  let i := bisectLeft a x lo (some hi)
  ∀ j, i ≤ j → j < hi → a[j]! ≥ x := by
  sorry

/-- The list after insortLeft remains sorted if it was sorted before -/
theorem insortLeft_sorted [Ord α] (a : List α) (x : α) (lo hi : Nat) :
  List.Sorted (· ≤ ·) a → List.Sorted (· ≤ ·) (insortLeft a x lo (some hi)) := by
  sorry

-- Tests

def checkBisect : Bool :=
  -- Basic
  bisectLeft [1, 2, 4, 4, 10] 4 == 2 &&
  bisectLeft [1, 2, 4, 4, 10] 0 == 0 &&
  bisectLeft [1, 2, 4, 4, 10] 99 == 5 &&
  
  -- With key function
  bisectLeftKey ["A", "bb", "CC", "ddd"] 1 0 none String.length == 0 &&
  bisectLeftKey ["A", "bb", "CC", "ddd"] 2 0 none String.length == 1 &&
  bisectLeftKey ["A", "bb", "CC", "ddd"] 3 0 none String.length == 3

def checkInsort : Bool :=
  let lst1 := insortLeft [1, 2, 4, 4, 10] 4
  let lst2 := insortLeftKey ["A", "bb", "CC", "ddd"] "cC" 0 none (λ s => s.toLower)
  
  lst1 == [1, 2, 4, 4, 4, 10] &&
  lst2 == ["A", "bb", "cC", "CC", "ddd"]

#eval checkBisect
#eval checkInsort
```
