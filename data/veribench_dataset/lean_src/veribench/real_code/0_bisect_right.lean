import Std

/-!
# VeriBench – Verified Bisection (Right-Biased Insertion Index)

File order:

1. Implementation
2. Unit tests (positive, edge, keyed)
3. Pre-condition
4. Property theorems
5. Post-condition (same order as theorems)
6. Correctness theorem `Pre → Post`
7. Insertion properties

All real proofs are left as `sorry` for the learner / model.

# Implementation

## `bisect_right` and `insort_right`

`bisect_right a x lo hi key?` returns the index `i` such that:
- all elements in `a[lo:i]` are `≤ x` in key space, and
- all elements in `a[i:hi]` are `> x`.

Insertion at `i` places `x` to the right of any equal elements, matching Python’s behavior.
-/


namespace Bisect

def bisect_right
    {α γ}
    (a   : Array α)
    (x   : γ)
    (lo  : Nat := 0)
    (hi? : Option Nat := none)
    (key?: Option (α → γ) := none)
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α] :
    Nat := Id.run do
  let hi := hi?.getD a.size
  match key? with
  | none =>
    let mut loM := lo
    let mut hiM := hi
    while loM < hiM do
      let mid := (loM + hiM) / 2
      let y : γ := (↑(a[mid]!) : γ)
      if x < y then
        hiM := mid
      else
        loM := mid + 1
    return loM
  | some key =>
    let mut loM := lo
    let mut hiM := hi
    while loM < hiM do
      let mid := (loM + hiM) / 2
      let y := key (a[mid]!)
      if x < y then
        hiM := mid
      else
        loM := mid + 1
    return loM

/-- Literal translation of Python's `insort_right` using `bisect_right`. -/
def insort_right
    {α γ}
    (a   : Array α)
    (x   : α)
    (lo  : Nat := 0)
    (hi? : Option Nat := none)
    (key?: Option (α → γ) := none)
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α] :
    Array α := Id.run do
  let idx :=
    match key? with
    | none      => bisect_right a ((↑x : γ)) lo hi? (key? := none)
    | some key  => bisect_right a (key x)    lo hi? (key? := some key)
  let left  := a.extract 0 idx
  let right := a.extract idx a.size
  return left ++ #[x] ++ right



/-!
# Tests
-/

-- Scoped coercions so tests compile
local instance : Coe Nat Nat    where coe := id
local instance : Coe String String where coe := id
local instance : Coe String Nat where coe := fun s => s.length


/-- expected: 4 -/
example : bisect_right (#[(1:Nat),2,4,4,10]) (4) = 4 := by native_decide
#eval bisect_right (#[(1:Nat),2,4,4,10]) (4)  -- expected: 4

/-- expected: 0 -/
example : bisect_right (#[(1:Nat),2,4,4,10]) (0) = 0 := by native_decide
#eval bisect_right (#[(1:Nat),2,4,4,10]) (0)  -- expected: 0

/-- expected: 5 -/
example : bisect_right (#[(1:Nat),2,4,4,10]) (99) = 5 := by native_decide
#eval bisect_right (#[(1:Nat),2,4,4,10]) (99) -- expected: 5

/-!
# Tests: Keyed (string length)
-/

/-- expected: 1 -/
example :
  bisect_right #["A","bb","CC","ddd"] (1) (key? := some (·.length)) = 1 := by
  native_decide
#eval bisect_right #["A","bb","CC","ddd"] (1) (key? := some (·.length))  -- expected: 1

/-- expected: 3 -/
example :
  bisect_right #["A","bb","CC","ddd"] (2) (key? := some (·.length)) = 3 := by
  native_decide
#eval bisect_right #["A","bb","CC","ddd"] (2) (key? := some (·.length))  -- expected: 3

/-- expected: 4 -/
example :
  bisect_right #["A","bb","CC","ddd"] (3) (key? := some (·.length)) = 4 := by
  native_decide
#eval bisect_right #["A","bb","CC","ddd"] (3) (key? := some (·.length))  -- expected: 4

/-!
# Positive / Negative Test-Suite (insertion)
-/

/-- expected: #[1,2,4,4,4,10] -/
example :
  insort_right (γ := Nat) (#[(1:Nat),2,4,4,10]) 4
    = #[(1:Nat),2,4,4,4,10] := by
  native_decide
#eval insort_right (γ := Nat) (#[(1:Nat),2,4,4,10]) 4  -- expected: #[1,2,4,4,4,10]

/-- expected: #["A","bb","CC","cC","ddd"] -/
example :
  insort_right #["A","bb","CC","ddd"] "cC" (key? := some (fun s => s.toLower))
    = #["A","bb","CC","cC","ddd"] := by
  native_decide
#eval insort_right #["A","bb","CC","ddd"] "cC" (key? := some (fun s => s.toLower))
-- expected: #["A","bb","CC","cC","ddd"]

/-!
# Pre-Condition
-/

/-- Default projection when no key is provided. -/
def defaultProj {α : Type u} {γ : Type v} [Coe α γ] : α → γ :=
  fun a => (↑a : γ)

/-- Project into key space (uses `key` if provided, else coercion). -/
def Proj {α : Type u} {γ : Type v} (key? : Option (α → γ)) [Coe α γ] : α → γ :=
  key?.elim defaultProj id

/-- `SortedSlice a lo hi proj` means `a[lo:hi]` is nondecreasing under `proj`. -/
def SortedSlice {α : Type u} {γ : Type v}
    (a : Array α) (lo hi : Nat) (proj : α → γ)
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)] [Inhabited α] : Prop :=
  ∀ i j, lo ≤ i → i ≤ j → j < hi → proj (a[i]!) ≤ proj (a[j]!)

/-- Bounds + sortedness precondition for `bisect_right`. -/
def Pre {α : Type u} {γ : Type v}
    (a : Array α) (lo hi : Nat) (key? : Option (α → γ))
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)] [Coe α γ] [Inhabited α] : Prop :=
  lo ≤ hi ∧ hi ≤ a.size ∧ SortedSlice a lo hi (Proj key?)



/-!
# Insertion Properties (`insort_right`)
-/

/-- **Splice shape**: `insort_right` equals `left.push x ++ right` at the bisect index. -/
theorem insort_splice_shape
    {α γ} [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ)) :
  let idx :=
    match key? with
    | none     => bisect_right a ((↑xα : γ)) lo hi? (key? := none)
    | some key => bisect_right a (key xα)       lo hi? (key? := some key)
  insort_right a xα lo hi? key? =
    (a.extract 0 idx).push xα ++ a.extract idx a.size := by
  intro idx
  simp [insort_right, idx]
  rfl

/-- **Sortedness preserved on the slice**:
If `a[lo:hi]` was sorted in key space, inserting at the bisect index keeps it sorted. -/
theorem insort_preserves_sorted_slice
    {α γ}
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (hpre : Pre a lo (hi?.getD a.size) key?) :
    let x  := match key? with | none => (↑xα : γ) | some key => key xα
    let i  := bisect_right a x lo hi? key?
    let a' := insort_right a xα lo hi? key?;
    SortedSlice a' lo (i+1) (Proj key?) ∧
    SortedSlice a' (i+1) (hi?.getD a.size + 1) (Proj key?) := by
  -- `let`-bindings are part of the goal; no additional `intro`s needed.
  sorry

/-- **Insert partition**:
After `insort_right`, elements before `i` are `≤ x` and elements at/after `i+1` are `> x`. -/
theorem insort_partition_after_insert
    {α γ}
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (hpre : Pre a lo (hi?.getD a.size) key?) :
    let proj := Proj key?
    let x := match key? with | none => (↑xα : γ) | some key => key xα
    let i := bisect_right a x lo hi? key?
    let a' := insort_right a xα lo hi? key?;
    (∀ j, lo ≤ j → j < i → proj (a'[j]!) ≤ x) ∧
    (∀ j, i+1 ≤ j → j < a'.size → x < proj (a'[j]!)) := by
  -- Same note: the `let`-bindings are already in the goal context.
  sorry


end Bisect
