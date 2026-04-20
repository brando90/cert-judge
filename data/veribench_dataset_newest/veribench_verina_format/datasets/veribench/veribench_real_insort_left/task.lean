-- !benchmark @start import type=solution
import Mathlib
namespace Insort
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def insort_left_imp_precond {α γ : Type} [LE γ] [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (x : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ)) : Prop :=
  -- !benchmark @start precond
  let hi := hi?.getD a.size
  lo ≤ hi ∧ hi ≤ a.size ∧
    ∀ i j, lo ≤ i → i ≤ j → j < hi → toKey a[i]! key? ≤ toKey a[j]! key?
  -- !benchmark @end precond

-- !benchmark @start code_aux

/-- Helper: Project an element into key space -/
def toKey {α γ : Type} [Coe α γ] (val : α) (key? : Option (α → γ)) : γ :=
  match key? with
  | some k => k val
  | none   => ↑val

/-- Helper: Imperative Bisect Left -/
def bisect_left_imp {α γ : Type}
    (a : Array α) (x : γ) (lo : Nat := 0) (hi? : Option Nat := none) (key? : Option (α → γ) := none)
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α] : Nat :=
  Id.run do
    let mut loM := lo
    let mut hiM := hi?.getD a.size
    while loM < hiM do
      let mid := (loM + hiM) / 2
      let val : γ := match key? with
        | some k => k a[mid]!
        | none   => ↑(a[mid]!)
      if val < x then
        loM := mid + 1
      else
        hiM := mid
    return loM

-- !benchmark @end code_aux

def insort_left_imp {α γ : Type}
    (a : Array α) (x : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (h_precond : insort_left_imp_precond (a) (x) (lo) (hi?) (key?)) : Array α :=
  -- !benchmark @start code
  Id.run do
    let x_key := toKey x key?
    let idx := bisect_left_imp a x_key lo hi? key?
    if h : idx ≤ a.size then
      return a.insertIdx idx x
    else
      return a
  -- !benchmark @end code

-- !benchmark @start postcond_aux

def size_prop {α : Type} (a res : Array α) : Prop :=
  res.size = a.size + 1

def sorted_prop {α γ : Type} [LE γ] [Coe α γ] [Inhabited α]
    (res : Array α) (lo hi : Nat) (key? : Option (α → γ)) : Prop :=
  ∀ i j, lo ≤ i → i ≤ j → j < (hi + 1) → toKey res[i]! key? ≤ toKey res[j]! key?

-- !benchmark @end postcond_aux

@[reducible, simp]
def insort_left_imp_postcond {α γ : Type} [LE γ] [LT γ] [Coe α γ] [Inhabited α]
    (a : Array α) (x : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (result : Array α)
    (h_precond : insort_left_imp_precond (a) (x) (lo) (hi?) (key?)) : Prop :=
  -- !benchmark @start postcond
  size_prop a result ∧
    sorted_prop result lo (hi?.getD a.size) key?
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem insort_left_imp_spec_satisfied {α γ : Type}
    [LE γ] [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (x : α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (h_precond : insort_left_imp_precond (a) (x) (lo) (hi?) (key?)) :
    insort_left_imp_postcond (a) (x) (lo) (hi?) (key?)
      (insort_left_imp (a) (x) (lo) (hi?) (key?) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof