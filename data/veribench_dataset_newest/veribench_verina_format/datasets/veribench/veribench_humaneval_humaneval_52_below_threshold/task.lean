-- !benchmark @start import type=solution
import Mathlib
namespace Humaneval52_BelowThreshold
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def belowThreshold_precond (l : List Nat) (t : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def belowThreshold (l : List Nat) (t : Nat) (h_precond : belowThreshold_precond (l) (t)) : Bool :=
  -- !benchmark @start code
  let rec loop : List Nat → Bool
    | []      => true
    | e :: es => if decide (t ≤ e) then false else loop es
  loop l
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def belowThreshold_postcond (l : List Nat) (t : Nat) (result : Bool)
    (h_precond : belowThreshold_precond (l) (t)) : Prop :=
  -- !benchmark @start postcond
  result = decide (∀ e, e ∈ l → e < t)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def spec_prop (l : List Nat) (t : Nat) : Prop :=
  belowThreshold l t (by simp) = decide (∀ e, e ∈ l → e < t)

@[simp] theorem spec_thm (l : List Nat) (t : Nat) : spec_prop l t := by
  sorry

def monotone_threshold_prop (l : List Nat) (t t' : Nat) : Prop :=
  belowThreshold l t (by simp) = true → t ≤ t' → belowThreshold l t' (by simp) = true

@[simp] theorem monotone_threshold_thm (l : List Nat) (t t' : Nat) :
  monotone_threshold_prop l t t' := by
  sorry

def counterexample_prop (l : List Nat) (t : Nat) : Prop :=
  (∃ e, e ∈ l ∧ e ≥ t) → belowThreshold l t (by simp) = false

@[simp] theorem counterexample_thm (l : List Nat) (t : Nat) :
  counterexample_prop l t := by
  sorry

def false_iff_exists_ge_prop (l : List Nat) (t : Nat) : Prop :=
  (belowThreshold l t (by simp) = false) ↔ (∃ e, e ∈ l ∧ e ≥ t)

@[simp] theorem false_iff_exists_ge_thm (l : List Nat) (t : Nat) :
  false_iff_exists_ge_prop l t := by
  sorry

def append_and_prop (xs ys : List Nat) (t : Nat) : Prop :=
  belowThreshold (xs ++ ys) t (by simp) =
    (belowThreshold xs t (by simp) && belowThreshold ys t (by simp))

@[simp] theorem append_and_thm (xs ys : List Nat) (t : Nat) :
  append_and_prop xs ys t := by
  sorry

def threshold_zero_prop (l : List Nat) : Prop :=
  belowThreshold l 0 (by simp) = decide (l = [])

@[simp] theorem threshold_zero_thm (l : List Nat) : threshold_zero_prop l := by
  sorry

def antitone_threshold_prop (l : List Nat) (t t' : Nat) : Prop :=
  belowThreshold l t (by simp) = false → t' ≤ t → belowThreshold l t' (by simp) = false

@[simp] theorem antitone_threshold_thm (l : List Nat) (t t' : Nat) :
  antitone_threshold_prop l t t' := by
  sorry

def reverse_invariant_prop (l : List Nat) (t : Nat) : Prop :=
  belowThreshold l t (by simp) = belowThreshold l.reverse t (by simp)

@[simp] theorem reverse_invariant_thm (l : List Nat) (t : Nat) :
  reverse_invariant_prop l t := by
  sorry

-- !benchmark @end proof_aux

theorem belowThreshold_spec_satisfied (l : List Nat) (t : Nat)
    (h_precond : belowThreshold_precond (l) (t)) :
    belowThreshold_postcond (l) (t) (belowThreshold (l) (t) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof
end Humaneval52_BelowThreshold