-- !benchmark @start import type=solution
import Mathlib
namespace MyStringLength
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myStringLength_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myStringLength (s : String) (h_precond : myStringLength_precond (s)) : Nat :=
  -- !benchmark @start code
  s.length
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myStringLength_postcond (s : String) (result : Nat) (h_precond : myStringLength_precond (s)) : Prop :=
  -- !benchmark @start postcond
  result = s.length
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def length_empty_prop : Prop := myStringLength "" (by simp) = 0

theorem length_empty_thm : length_empty_prop := by
  sorry

def length_single_prop (c : Char) : Prop := myStringLength (String.mk [c]) (by simp) = 1

theorem length_single_thm (c : Char) : length_single_prop c := by
  sorry

def length_nonneg_prop (s : String) : Prop := myStringLength s (by simp) ≥ 0

theorem length_nonneg_thm (s : String) : length_nonneg_prop s := by
  sorry

def length_append_prop (s₁ s₂ : String) : Prop :=
  myStringLength (s₁ ++ s₂) (by simp) = myStringLength s₁ (by simp) + myStringLength s₂ (by simp)

theorem length_append_thm (s₁ s₂ : String) : length_append_prop s₁ s₂ := by
  sorry

theorem length_zero_iff_empty (s : String) : myStringLength s (by simp) = 0 ↔ s = "" := by
  sorry

theorem length_push (s : String) (c : Char) :
    myStringLength (s.push c) (by simp) = myStringLength s (by simp) + 1 := by
  sorry

-- !benchmark @end proof_aux

theorem myStringLength_spec_satisfied (s : String) (h_precond : myStringLength_precond (s)) :
    myStringLength_postcond (s) (myStringLength (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof