-- !benchmark @start import type=solution
import Mathlib
namespace ParseMusic

open List String
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def parseMusic_precond (musicString : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def parseMusic (musicString : String) (h_precond : parseMusic_precond (musicString)) : List Nat :=
  -- !benchmark @start code
  if musicString.isEmpty then
    []
  else
    let notes := musicString.split (· = ' ')
    notes.filterMap fun note =>
      match note with
      | "o" => some 4
      | "o|" => some 2
      | ".|" => some 1
      | _ => none
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[simp] def empty_string_prop : Prop := parseMusic "" (by simp) = []

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def valid_notes_prop (musicString : String) : Prop :=
  ∀ n ∈ parseMusic musicString (by simp), n = 1 ∨ n = 2 ∨ n = 4

@[simp] theorem valid_notes_thm (musicString : String) : valid_notes_prop musicString := by
  sorry

@[simp] def invalid_notes_prop : Prop := parseMusic "invalid note" (by simp) = []

@[simp] theorem invalid_notes_thm : invalid_notes_prop := by
  sorry

@[simp] def mixed_notes_prop : Prop := parseMusic "o invalid .|" (by simp) = [4, 1]

@[simp] theorem mixed_notes_thm : mixed_notes_prop := by
  sorry

@[simp] def whole_note_prop : Prop := parseMusic "o" (by simp) = [4]

@[simp] theorem whole_note_thm : whole_note_prop := by
  sorry

@[reducible, simp]
def parseMusic_postcond (musicString : String) (result : List Nat)
    (h_precond : parseMusic_precond (musicString)) : Prop :=
  -- !benchmark @start postcond
  (empty_string_prop) ∧
    (valid_notes_prop musicString) ∧
      (invalid_notes_prop) ∧ (mixed_notes_prop) ∧ (whole_note_prop)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem parseMusic_spec_satisfied (musicString : String) (h_precond : parseMusic_precond (musicString)) :
    parseMusic_postcond (musicString) (parseMusic (musicString) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof