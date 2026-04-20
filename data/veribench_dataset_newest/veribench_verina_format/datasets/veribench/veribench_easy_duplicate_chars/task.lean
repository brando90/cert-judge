-- !benchmark @start import type=solution
import Mathlib
namespace DuplicateChars
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def duplicateChars_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def duplicateChars (s : String) (h_precond : duplicateChars_precond (s)) : String :=
  -- !benchmark @start code
  String.mk <| s.data.foldr (fun c acc => c :: c :: acc) []
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def duplicateChars_postcond (s : String) (result : String) (h_precond : duplicateChars_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (result = duplicateChars (s) h_precond) ∧
  (duplicateChars "" (by simp) = "") ∧
  ((duplicateChars (s) h_precond).length = 2 * s.length) ∧
  (∀ c, duplicateChars (String.mk [c]) (by simp) = String.mk [c, c]) ∧
  (∀ c ∈ s.data, c ∈ (duplicateChars (s) h_precond).data) ∧
  ((duplicateChars (s) h_precond).length % 2 = 0)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

def empty_string_prop : Prop := duplicateChars "" (by simp) = ""

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def double_length_prop (s : String) : Prop :=
  (duplicateChars s (by simp)).length = 2 * s.length

@[simp] theorem double_length_thm (s : String) : double_length_prop s := by
  sorry

def single_char_prop (c : Char) : Prop :=
  duplicateChars (String.mk [c]) (by simp) = String.mk [c, c]

@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by
  sorry

def char_preservation_prop (s : String) : Prop :=
  ∀ c ∈ s.data, c ∈ (duplicateChars s (by simp)).data

@[simp] theorem char_preservation_thm (s : String) : char_preservation_prop s := by
  sorry

def even_length_prop (s : String) : Prop :=
  (duplicateChars s (by simp)).length % 2 = 0

@[simp] theorem even_length_thm (s : String) : even_length_prop s := by
  sorry

-- !benchmark @end proof_aux


theorem duplicateChars_spec_satisfied (s : String) (h_precond : duplicateChars_precond (s)) :
    duplicateChars_postcond (s) (duplicateChars (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof