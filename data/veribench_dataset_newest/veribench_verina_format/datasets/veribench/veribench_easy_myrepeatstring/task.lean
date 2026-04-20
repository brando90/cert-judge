-- !benchmark @start import type=solution
import Mathlib
namespace MyRepeatString
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myRepeatString_precond (s : String) (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myRepeatString (s : String) (n : Nat) (h_precond : myRepeatString_precond (s) (n)) : String :=
  -- !benchmark @start code
  match n with
  | 0 => ""
  | n + 1 => s ++ myRepeatString s n (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Zero repetition property**: Zero repetitions gives empty string. -/
def zero_repetition_prop (s : String) : Prop := myRepeatString s 0 (by simp) = ""

/-- **Zero repetition theorem**: Zero repetitions gives empty string. -/
theorem zero_repetition_thm (s : String) : zero_repetition_prop s := by
  sorry

/-- **One repetition property**: One repetition gives original string. -/
def one_repetition_prop (s : String) : Prop := myRepeatString s 1 (by simp) = s

/-- **One repetition theorem**: One repetition gives original string. -/
theorem one_repetition_thm (s : String) : one_repetition_prop s := by
  sorry

/-- **Length property**: Length of result is n times original length. -/
def length_prop (s : String) (n : Nat) : Prop :=
  (myRepeatString s n (by simp)).length = n * s.length

/-- **Length theorem**: Length of result is n times original length. -/
theorem length_thm (s : String) (n : Nat) : length_prop s n := by
  sorry

/-- **Empty string property**: Repeating empty string gives empty string. -/
def empty_string_prop (n : Nat) : Prop := myRepeatString "" n (by simp) = ""

/-- **Empty string theorem**: Repeating empty string gives empty string. -/
theorem empty_string_thm (n : Nat) : empty_string_prop n := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def myRepeatString_postcond (s : String) (n : Nat) (result : String) (h_precond : myRepeatString_precond (s) (n)) :=
  -- !benchmark @start postcond
  (zero_repetition_prop s) ∧
  (one_repetition_prop s) ∧
  (length_prop s n) ∧
  (empty_string_prop n)
  -- !benchmark @end postcond

theorem myRepeatString_spec_satisfied (s : String) (n : Nat) (h_precond : myRepeatString_precond (s) (n)) :
    myRepeatString_postcond (s) (n) (myRepeatString (s) (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof