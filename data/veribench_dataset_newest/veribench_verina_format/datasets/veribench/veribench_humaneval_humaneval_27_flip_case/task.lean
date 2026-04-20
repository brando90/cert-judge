-- !benchmark @start import type=solution
import Mathlib
namespace FlipCase
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def flipCase_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def flipCase (s : String) (h_precond : flipCase_precond (s)) : String :=
  -- !benchmark @start code
  s.map fun c =>
    if c.isLower then c.toUpper
    else if c.isUpper then c.toLower
    else c
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- Property definitions & theorems (used by the postcondition)
def empty_string_prop : Prop := flipCase "" (by simp) = ""

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def length_preservation_prop (s : String) : Prop :=
  (flipCase s (by simp)).length = s.length

@[simp] theorem length_preservation_thm (s : String) : length_preservation_prop s := by
  sorry

def involution_prop (s : String) : Prop :=
  flipCase (flipCase s (by simp)) (by simp) = s

@[simp] theorem involution_thm (s : String) : involution_prop s := by
  sorry

def non_letter_preservation_prop (s : String) : Prop :=
  ∀ i c, s.get? i = some c → ¬c.isAlpha → (flipCase s (by simp)).get? i = some c

@[simp] theorem non_letter_preservation_thm (s : String) : non_letter_preservation_prop s := by
  sorry

def case_flip_prop (s : String) : Prop :=
  ∀ i c, s.get? i = some c → c.isAlpha →
    (c.isLower → (flipCase s (by simp)).get? i = some c.toUpper) ∧
    (c.isUpper → (flipCase s (by simp)).get? i = some c.toLower)

@[simp] theorem case_flip_thm (s : String) : case_flip_prop s := by
  sorry

@[reducible, simp]
def flipCase_postcond (s : String) (result : String) (h_precond : flipCase_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (empty_string_prop) ∧
  (length_preservation_prop s) ∧
  (involution_prop s) ∧
  (non_letter_preservation_prop s) ∧
  (case_flip_prop s)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem flipCase_spec_satisfied (s : String) (h_precond : flipCase_precond (s)) :
    flipCase_postcond (s) (flipCase (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof