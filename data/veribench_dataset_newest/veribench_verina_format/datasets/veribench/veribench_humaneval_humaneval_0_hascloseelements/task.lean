-- !benchmark @start import type=solution
import Mathlib
namespace HasCloseElements

open List
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def hasCloseElements_precond (numbers : List Float) (threshold : Float) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def hasCloseElements (numbers : List Float) (threshold : Float)
    (h_precond : hasCloseElements_precond (numbers) (threshold)) : Bool :=
  -- !benchmark @start code
  match numbers with
  | [] => false
  | x :: xs =>
    if xs.any (fun y => Float.abs (x - y) < threshold) then
      true
    else
      hasCloseElements xs threshold (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- Property props/theorems moved here to preserve compilation of the postcondition.

def empty_list_prop (threshold : Float) : Prop :=
  hasCloseElements [] threshold (by simp) = false

@[simp] theorem empty_list_thm (threshold : Float) : empty_list_prop threshold := by
  sorry

def singleton_list_prop (x : Float) (threshold : Float) : Prop :=
  hasCloseElements [x] threshold (by simp) = false

@[simp] theorem singleton_list_thm (x : Float) (threshold : Float) : singleton_list_prop x threshold := by
  sorry

def threshold_mono_prop (numbers : List Float) (t₁ t₂ : Float) : Prop :=
  t₁ ≤ t₂ → hasCloseElements numbers t₁ (by simp) = true → hasCloseElements numbers t₂ (by simp) = true

@[simp] theorem threshold_mono_thm (numbers : List Float) (t₁ t₂ : Float) : threshold_mono_prop numbers t₁ t₂ := by
  sorry

def duplicates_prop (numbers : List Float) (t : Float) : Prop :=
  (∃ x, numbers.count x ≥ 2) ∧ t > 0 → hasCloseElements numbers t (by simp) = true

@[simp] theorem duplicates_thm (numbers : List Float) (t : Float) : duplicates_prop numbers t := by
  sorry

def nonpos_threshold_prop (numbers : List Float) (t : Float) : Prop :=
  t ≤ 0 → hasCloseElements numbers t (by simp) = false

@[simp] theorem nonpos_threshold_thm (numbers : List Float) (t : Float) : nonpos_threshold_prop numbers t := by
  sorry

def perm_invariant_prop (numbers numbers' : List Float) (t : Float) : Prop :=
  numbers ~ numbers' → hasCloseElements numbers t (by simp) = hasCloseElements numbers' t (by simp)

@[simp] theorem perm_invariant_thm (numbers numbers' : List Float) (t : Float) : perm_invariant_prop numbers numbers' t := by
  sorry

@[reducible, simp]
def hasCloseElements_postcond (numbers : List Float) (threshold : Float) (result : Bool)
    (h_precond : hasCloseElements_precond (numbers) (threshold)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop threshold) ∧
    (∀ x, singleton_list_prop x threshold) ∧
      (∀ t₁ t₂, threshold_mono_prop numbers t₁ t₂) ∧
        (duplicates_prop numbers threshold) ∧
          (nonpos_threshold_prop numbers threshold) ∧
            (∀ numbers', perm_invariant_prop numbers numbers' threshold)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem hasCloseElements_spec_satisfied (numbers : List Float) (threshold : Float)
    (h_precond : hasCloseElements_precond (numbers) (threshold)) :
    hasCloseElements_postcond (numbers) (threshold) (hasCloseElements (numbers) (threshold) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof