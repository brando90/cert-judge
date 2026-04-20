-- !benchmark @start import type=solution
import Mathlib
namespace MyUppercase
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Converts a single character to uppercase -/
def toUpper (c : Char) : Char :=
  c.toUpper
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def myUppercase_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def myUppercase (s : String) (h_precond : myUppercase_precond (s)) : String :=
  -- !benchmark @start code
  s.map toUpper
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def myUppercase_postcond (s : String) (result : String) (h_precond : myUppercase_precond (s)) : Prop :=
  -- !benchmark @start postcond
  result = s.map toUpper
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Length preservation property**: Length is preserved. -/
def length_preservation_prop (s : String) : Prop := (myUppercase (s) (by simp)).length = s.length

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (s : String) : length_preservation_prop s := by
  sorry

/-- **Empty string property**: Uppercase of empty string is empty. -/
def empty_string_prop : Prop := myUppercase ("") (by simp) = ""

/-- **Empty string theorem**: Uppercase of empty string is empty. -/
@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

/-- **Idempotence property**: Applying uppercase twice is same as once. -/
def idempotent_prop (s : String) : Prop :=
  myUppercase (myUppercase (s) (by simp)) (by simp) = myUppercase (s) (by simp)

/-- **Idempotence theorem**: Applying uppercase twice is same as once. -/
@[simp] theorem idempotent_thm (s : String) : idempotent_prop s := by
  sorry

/-- **Single character property**: Uppercase of single character equals toUpper of that character. -/
def single_char_prop (c : Char) : Prop :=
  myUppercase (String.mk [c]) (by simp) = String.mk [toUpper c]

/-- **Single character theorem**: Uppercase of single character equals toUpper of that character. -/
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by
  sorry

/-- **Append distributivity property**: Uppercase of concatenation equals concatenation of uppercases. -/
def append_distributive_prop (s₁ s₂ : String) : Prop :=
  myUppercase (s₁ ++ s₂) (by simp) = myUppercase (s₁) (by simp) ++ myUppercase (s₂) (by simp)

/-- **Append distributivity theorem**: Uppercase of concatenation equals concatenation of uppercases. -/
@[simp] theorem append_distributive_thm (s₁ s₂ : String) : append_distributive_prop s₁ s₂ := by
  sorry
-- !benchmark @end proof_aux

theorem myUppercase_spec_satisfied (s : String) (h_precond : myUppercase_precond (s)) :
    myUppercase_postcond (s) (myUppercase (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof