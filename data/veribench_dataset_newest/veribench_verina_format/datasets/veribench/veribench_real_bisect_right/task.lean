-- !benchmark @start import type=solution
import Mathlib
namespace Bisect
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
def toKey {α γ : Type} [Coe α γ] (val : α) (key? : Option (α → γ)) : γ :=
  match key? with
  | some k => k val
  | none   => ↑val
-- !benchmark @end precond_aux

@[reducible, simp]
def bisect_right_imp_precond {α γ : Type} [LE γ] [Coe α γ] [Inhabited α]
    (a : Array α) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ)) : Prop :=
  -- !benchmark @start precond
  let hi := hi?.getD a.size
  lo ≤ hi ∧ hi ≤ a.size ∧
    ∀ i j, lo ≤ i → i ≤ j → j < hi → toKey a[i]! key? ≤ toKey a[j]! key?
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def bisect_right_imp {α γ : Type}
    (a : Array α) (x : γ) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (h_precond : bisect_right_imp_precond (a) (lo) (hi?) (key?))
    [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α] : Nat :=
  -- !benchmark @start code
  Id.run do
    let mut loM := lo
    let mut hiM := hi?.getD a.size

    while loM < hiM do
      let mid := (loM + hiM) / 2
      let val : γ := match key? with
        | some k => k a[mid]!
        | none   => ↑(a[mid]!)

      if x < val then
        hiM := mid
      else
        loM := mid + 1
    return loM
  -- !benchmark @end code

-- !benchmark @start postcond_aux
def left_partition_prop {α γ : Type} [LE γ] [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (idx lo : Nat) (key? : Option (α → γ)) : Prop :=
  ∀ i, lo ≤ i → i < idx → toKey a[i]! key? ≤ x

def right_partition_prop {α γ : Type} [LT γ] [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (idx hi : Nat) (key? : Option (α → γ)) : Prop :=
  ∀ i, idx ≤ i → i < hi → x < toKey a[i]! key?
-- !benchmark @end postcond_aux

@[reducible, simp]
def bisect_right_imp_postcond {α γ : Type} [LE γ] [LT γ] [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (result : Nat) (h_precond : bisect_right_imp_precond (a) (lo) (hi?) (key?)) : Prop :=
  -- !benchmark @start postcond
  let hi := hi?.getD a.size
  lo ≤ result ∧ result ≤ hi ∧
    left_partition_prop a x result lo key? ∧
    right_partition_prop a x result hi key?
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem bisect_left_partition_thm {α γ : Type}
    [LE γ] [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (lo hi : Nat) (key? : Option (α → γ))
    (h : bisect_right_imp_precond (a) (lo) (some hi) (key?)) :
    left_partition_prop a x (bisect_right_imp a x lo (some hi) key? (by sorry)) lo key? := by
  sorry

theorem bisect_right_partition_thm {α γ : Type}
    [LE γ] [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (lo hi : Nat) (key? : Option (α → γ))
    (h : bisect_right_imp_precond (a) (lo) (some hi) (key?)) :
    right_partition_prop a x (bisect_right_imp a x lo (some hi) key? (by sorry)) hi key? := by
  sorry
-- !benchmark @end proof_aux

theorem bisect_right_imp_spec_satisfied {α γ : Type}
    [LE γ] [LT γ] [DecidableRel (· < · : γ → γ → Prop)]
    [Coe α γ] [Inhabited α]
    (a : Array α) (x : γ) (lo : Nat) (hi? : Option Nat) (key? : Option (α → γ))
    (h_precond : bisect_right_imp_precond (a) (lo) (hi?) (key?)) :
    bisect_right_imp_postcond (a) (x) (lo) (hi?) (key?)
      (bisect_right_imp a x lo hi? key? h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof