-- !benchmark @start import type=solution
import Mathlib
namespace ReplaceSpaces
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def replaceSpaces_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def replaceSpaces (s : String) (h_precond : replaceSpaces_precond (s)) : String :=
  -- !benchmark @start code
  s.map (fun c => if c = ' ' then '_' else c)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- Property Theorems (moved here so postcondition can reference them)

def empty_string_prop : Prop := replaceSpaces "" (by simp) = ""

@[simp] theorem empty_string_thm : empty_string_prop := sorry

def no_spaces_prop (s : String) : Prop :=
  ¬ (replaceSpaces s (by simp)).data.any (· = ' ')

@[simp] theorem no_spaces_thm (s : String) : no_spaces_prop s := sorry

def length_preserved_prop (s : String) : Prop :=
  (replaceSpaces s (by simp)).length = s.length

@[simp] theorem length_preserved_thm (s : String) : length_preserved_prop s := sorry

def space_replacement_prop (s : String) : Prop :=
  ∀ c ∈ s.data,
    c = ' ' →
      c ∉ (replaceSpaces s (by simp)).data ∧ '_' ∈ (replaceSpaces s (by simp)).data

@[simp] theorem space_replacement_thm (s : String) : space_replacement_prop s := sorry

def non_space_preservation_prop (s : String) : Prop :=
  ∀ c ∈ s.data, c ≠ ' ' → c ∈ (replaceSpaces s (by simp)).data

@[simp] theorem non_space_preservation_thm (s : String) : non_space_preservation_prop s := sorry

@[reducible, simp]
def replaceSpaces_postcond (s : String) (result : String) (h_precond : replaceSpaces_precond (s)) :=
  -- !benchmark @start postcond
  result = replaceSpaces s h_precond ∧
    (empty_string_prop) ∧
    (no_spaces_prop s) ∧
    (length_preserved_prop s) ∧
    (space_replacement_prop s) ∧
    (non_space_preservation_prop s)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem replaceSpaces_spec_satisfied (s : String) (h_precond : replaceSpaces_precond (s)) :
    replaceSpaces_postcond (s) (replaceSpaces (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof