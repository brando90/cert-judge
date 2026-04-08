import VeriBench

namespace BisectRight

/-- The key function takes an element of type `α` and returns a value of type `β` -/
def KeyFn (α β : Type) := α → β

/-- Find the insertion point for `x` in sorted array `a` such that all elements in `a[:i]` have
    elements less than or equal to `x` and all elements in `a[i:]` have elements greater than `x`. -/
def bisect_right {α β : Type} [Ord β] (a : Array α) (x : β) (lo : Nat := 0) (hi : Option Nat := none) 
    (key : Option (KeyFn α β) := none) : Nat :=
  let hi := match hi with
    | none => a.size
    | some h => h

  match key with
  | none => 
    -- Without a key function, we directly compare values
    -- This requires α and β to be the same type
    let rec loop (lo : Nat) (hi : Nat) : Nat :=
      if lo < hi then
        let mid := (lo + hi) / 2
        if x < (a.get! mid : β) then  -- Type assertion
          loop lo mid
        else
          loop (mid + 1) hi
      else
        lo
    loop lo hi
  | some k =>
    -- With a key function, we compare in key space
    let rec loop (lo : Nat) (hi : Nat) : Nat :=
      if lo < hi then
        let mid := (lo + hi) / 2
        if x < k (a.get! mid) then
          loop lo mid
        else
          loop (mid + 1) hi
      else
        lo
    loop lo hi

/-- Insert item `x` into sorted array `a` while maintaining the sort order. -/
def insort_right {α β : Type} [Ord β] (a : Array α) (x : α) (lo : Nat := 0) (hi : Option Nat := none)
    (key : Option (KeyFn α β) := none) : Array α :=
  let idx := match key with
    | none => bisect_right a (x : β) lo hi none  -- Type assertion
    | some k => bisect_right a (k x) lo hi key
  a.insertAt! idx x

/-- Specification: bisect_right returns an index where all elements to the left are <= x 
    and all elements to the right are > x -/
def bisect_right_spec {α : Type} [Ord α] (a : Array α) (x : α) (lo : Nat) (hi : Option Nat) (result : Nat) : Prop :=
  let hi := match hi with
    | none => a.size
    | some h => h
  
  -- Result is within bounds
  lo ≤ result ∧ result ≤ hi ∧
  
  -- All elements to the left of result are <= x
  (∀ i, lo ≤ i ∧ i < result → a[i] ≤ x) ∧
  
  -- All elements to the right of result are > x
  (∀ i, result ≤ i ∧ i < hi → x < a[i])

/-- Theorem: bisect_right satisfies its specification -/
theorem bisect_right_correct {α : Type} [Ord α] (a : Array α) (x : α) (lo : Nat) (hi : Option Nat) :
  bisect_right_spec a x lo hi (bisect_right a x lo hi none) := by
  sorry

/-- Specification: After insort_right, the array remains sorted and contains the new element -/
def insort_right_spec {α : Type} [Ord α] (a : Array α) (x : α) (result : Array α) : Prop :=
  -- Result contains all elements from a plus x
  (∀ e, (e ∈ a.data ∨ e = x) ↔ e ∈ result.data) ∧
  
  -- Result is sorted
  (∀ i j, i < j → j < result.size → result[i] ≤ result[j])

/-- Theorem: insort_right satisfies its specification -/
theorem insort_right_correct {α : Type} [Ord α] (a : Array α) (x : α) :
  insort_right_spec a x (insort_right a x) := by
  sorry

/-- Test cases for bisect_right -/
def test_bisect_right : IO Bool := do
  -- Basic tests
  let a1 := #[1, 2, 4, 4, 10]
  let r1 := bisect_right a1 4
  let r2 := bisect_right a1 0
  let r3 := bisect_right a1 99
  
  -- Tests with key function
  let a2 : Array String := #["A", "bb", "CC", "ddd"]
  let key : KeyFn String Nat := String.length
  let r4 := bisect_right a2 1 0 none (some key)
  let r5 := bisect_right a2 2 0 none (some key)
  let r6 := bisect_right a2 3 0 none (some key)
  
  return r1 == 4 && r2 == 0 && r3 == 5 && r4 == 1 && r5 == 3 && r6 == 4

/-- Test cases for insort_right -/
def test_insort_right : IO Bool := do
  -- Test without key function
  let a1 := #[1, 2, 4, 4, 10]
  let a1' := insort_right a1 4
  
  -- Test with key function
  let a2 : Array String := #["A", "bb", "CC", "ddd"]
  let key : KeyFn String String := String.toLower
  let a2' := insort_right a2 "cC" 0 none (some key)
  
  return a1' == #[1, 2, 4, 4, 4, 10] && a2' == #["A", "bb", "CC", "cC", "ddd"]

end BisectRight

def main : IO Unit := do
  let r1 ← BisectRight.test_bisect_right
  let r2 ← BisectRight.test_insort_right
  IO.println s!"Tests passed: {r1 && r2}"
