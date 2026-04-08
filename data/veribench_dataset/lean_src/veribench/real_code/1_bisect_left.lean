import Std

/-!
# VeriBench – Left-Biased Insertion Index (Insort-focused)

1. Implementation
2. Unit tests (positive, edge, keyed)
3. Pre-condition
4. Property theorems
5. Post-condition (same order as theorems)
6. Correctness theorem `Pre → Post`
7. Insertion properties

All real proofs are left as `sorry`.
-/

namespace Bisect

def bisect_left
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
      if y < x then
        loM := mid + 1
      else
        hiM := mid
    return loM
  | some key =>
    let mut loM := lo
    let mut hiM := hi
    while loM < hiM do
      let mid := (loM + hiM) / 2
      let y := key (a[mid]!)
      if y < x then
        loM := mid + 1
      else
        hiM := mid
    return loM


def insort_left
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
    | none      => bisect_left a ((↑x : γ)) lo hi? (key? := none)
    | some key  => bisect_left a (key x)    lo hi? (key? := some key)
  let left  := a.extract 0 idx
  let right := a.extract idx a.size
  return left ++ #[x] ++ right



/-!
# Tests
-/

-- Scoped coercions so tests compile
local instance : Coe Nat Nat        where coe := id
local instance : Coe String String  where coe := id
-- Use string length as the “key space” when needed
local instance : Coe String Nat     where coe := fun s => s.length

/-- expected: 2 -/
example : bisect_left (#[(1:Nat),2,4,4,10]) (4) = 2 := by native_decide
#eval bisect_left (#[(1:Nat),2,4,4,10]) (4)  -- expected: 2

/-- expected: 0 -/
example : bisect_left (#[(1:Nat),2,4,4,10]) (0) = 0 := by native_decide
#eval bisect_left (#[(1:Nat),2,4,4,10]) (0)  -- expected: 0

/-- expected: 5 -/
example : bisect_left (#[(1:Nat),2,4,4,10]) (99) = 5 := by native_decide
#eval bisect_left (#[(1:Nat),2,4,4,10]) (99) -- expected: 5

/-! Keyed (string length): lengths `[1,2,2,3]` → x=1→0, x=2→1, x=3→3. -/

/-- expected: 0 -/
example :
  bisect_left #["A","bb","CC","ddd"] (1) (key? := some (·.length)) = 0 := by
  native_decide
#eval bisect_left #["A","bb","CC","ddd"] (1) (key? := some (·.length))  -- expected: 0

/-- expected: 1 -/
example :
  bisect_left #["A","bb","CC","ddd"] (2) (key? := some (·.length)) = 1 := by
  native_decide
#eval bisect_left #["A","bb","CC","ddd"] (2) (key? := some (·.length))  -- expected: 1

/-- expected: 3 -/
example :
  bisect_left #["A","bb","CC","ddd"] (3) (key? := some (·.length)) = 3 := by
  native_decide
#eval bisect_left #["A","bb","CC","ddd"] (3) (key? := some (·.length))  -- expected: 3

/-- expected: #[1,2,4,4,4,10] -/
example :
  insort_left (γ := Nat) (#[(1:Nat),2,4,4,10]) 4
    = #[(1:Nat),2,4,4,4,10] := by
  native_decide
#eval insort_left (γ := Nat) (#[(1:Nat),2,4,4,10]) 4  -- expected: #[1,2,4,4,4,10]

/-- expected: #["A","bb","cC","CC","ddd"] -/
example :
  insort_left #["A","bb","CC","ddd"] "cC" (key? := some (fun s => s.toLower))
    = #["A","bb","cC","CC","ddd"] := by
  native_decide
#eval insort_left #["A","bb","CC","ddd"] "cC" (key? := some (fun s => s.toLower))
-- expected: #["A","bb","cC","CC","ddd"]



/-!
# Pre-Condition (slice sortedness)
-/

/-- Default projection when no key is provided. -/
def defaultProjL {α : Type u} {γ : Type v} [Coe α γ] : α → γ :=
  fun a => (↑a : γ)

/-- Project into key space (uses `key` if provided, else coercion). -/
def ProjL {α : Type u} {γ : Type v} (key? : Option (α → γ)) [Coe α γ] : α → γ :=
  key?.elim defaultProjL id

/-- `SortedSliceL a lo hi proj` means `a[lo:hi]` is nondecreasing under `proj`. -/
def SortedSliceL {α : Type u} {γ : Type v}
    (a : Array α) (lo hi : Nat) (proj : α → γ)
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)] [Inhabited α] : Prop :=
  ∀ i j, lo ≤ i → i ≤ j → j < hi → proj (a[i]!) ≤ proj (a[j]!)

/-- Bounds + sortedness precondition for `insort_left` on `a[lo:hi]`. -/
def PreL {α : Type u} {γ : Type v}
    (a : Array α) (lo hi : Nat) (key? : Option (α → γ))
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)] [Coe α γ] [Inhabited α] : Prop :=
  lo ≤ hi ∧ hi ≤ a.size ∧ SortedSliceL a lo hi (ProjL key?)



/-!
# Insertion Theorems (only for `insort_left`)
-/

/-- **Splice shape**: `insort_left` equals `left.push x ++ right` at the bisect index. -/
theorem insort_splice_shape_left
    {α γ} [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ)) :
  let idx :=
    match key? with
    | none     => bisect_left a ((↑xα : γ)) lo hi? (key? := none)
    | some key => bisect_left a (key xα)       lo hi? (key? := some key)
  insort_left a xα lo hi? key? =
    (a.extract 0 idx).push xα ++ a.extract idx a.size := by
  intro idx
  simp [insort_left, idx]
  rfl

/-- **Sortedness preserved on the slice (left)**:
If `a[lo:hi]` was sorted in key space, inserting at the bisect index keeps it sorted. -/
theorem insort_preserves_sorted_slice_left
    {α γ}
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (hpre : PreL a lo (hi?.getD a.size) key?) :
    let proj := ProjL key?
    let x  := match key? with | none => (↑xα : γ) | some key => key xα
    let i  := bisect_left a x lo hi? key?
    let a' := insort_left a xα lo hi? key?;
    SortedSliceL a' lo (i+1) proj ∧
    SortedSliceL a' (i+1) (hi?.getD a.size + 1) proj := by
  intro; intro; intro; intro; sorry

/-- **Insert partition (left)**:
After `insort_left`, elements before `i` are `< x` and elements at/after `i+1` are `≥ x`. -/
theorem insort_partition_after_insert_left
    {α γ}
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [LE γ] [DecidableRel (· ≤ · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (xα : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (hpre : PreL a lo (hi?.getD a.size) key?) :
    let proj := ProjL key?
    let x := match key? with | none => (↑xα : γ) | some key => key xα
    let i := bisect_left a x lo hi? key?
    let a' := insort_left a xα lo hi? key?;
    (∀ j, lo ≤ j → j < i → proj (a'[j]!) < x) ∧
    (∀ j, i+1 ≤ j → j < a'.size → x ≤ proj (a'[j]!)) := by
  sorry

end Bisect
