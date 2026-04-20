-- !benchmark @start import type=solution
import Mathlib
namespace RemoveDigits
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Check if a character is a digit -/
def isDigit (c : Char) : Bool :=
  c.val ≥ '0'.val ∧ c.val ≤ '9'.val
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def removeDigits_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def removeDigits (s : String) (h_precond : removeDigits_precond (s)) : String :=
  -- !benchmark @start code
  String.mk (s.data.filter (fun c => ¬ isDigit c))
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def removeDigits_postcond (s : String) (result : String) (h_precond : removeDigits_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (result = removeDigits (s) h_precond)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
def empty_string_prop : Prop := removeDigits ("") (by simp) = ""

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def no_digits_prop (s : String) : Prop :=
  (∀ c ∈ s.data, ¬isDigit c) → removeDigits (s) (by simp) = s

@[simp] theorem no_digits_thm (s : String) : no_digits_prop s := by
  sorry

def all_digits_prop (s : String) : Prop :=
  (∀ c ∈ s.data, isDigit c) → removeDigits (s) (by simp) = ""

@[simp] theorem all_digits_thm (s : String) : all_digits_prop s := by
  sorry

def length_bound_prop (s : String) : Prop :=
  (removeDigits (s) (by simp)).length ≤ s.length

@[simp] theorem length_bound_thm (s : String) : length_bound_prop s := by
  sorry

def no_digits_in_result_prop (s : String) : Prop :=
  ∀ c ∈ (removeDigits (s) (by simp)).data, ¬ isDigit c

@[simp] theorem no_digits_in_result_thm (s : String) : no_digits_in_result_prop s := by
  sorry
-- !benchmark @end proof_aux

theorem removeDigits_spec_satisfied (s : String) (h_precond : removeDigits_precond (s)) :
    removeDigits_postcond (s) (removeDigits (s) h_precond) h_precond := by
  -- !benchmark @start proof
  simp [removeDigits_postcond]
  -- !benchmark @end proof
end RemoveDigits