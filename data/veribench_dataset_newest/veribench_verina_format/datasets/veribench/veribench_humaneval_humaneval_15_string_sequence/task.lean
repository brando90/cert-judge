-- !benchmark @start import type=solution
import Mathlib
namespace StringSequence
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def string_sequence_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def string_sequence (n : Nat) (h_precond : string_sequence_precond (n)) : String :=
  -- !benchmark @start code
  if n = 0 then
    "0"
  else
    String.intercalate " " (List.range (n + 1) |>.map toString)
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def string_sequence_postcond (n : Nat) (result : String) (h_precond : string_sequence_precond (n)) : Prop :=
  -- !benchmark @start postcond
  let zero_case_prop : Prop := string_sequence (0) (by simp) = "0"
  let starts_with_zero_prop (n : Nat) : Prop := result.startsWith "0"
  let space_separated_prop (n : Nat) : Prop := n > 0 → result.contains ' '
  let contains_all_numbers_prop (n : Nat) : Prop :=
    ∀ k ≤ n, result.contains (toString k).front
  let non_empty_prop (n : Nat) : Prop := result.length > 0
  zero_case_prop ∧
    starts_with_zero_prop n ∧
    space_separated_prop n ∧
    contains_all_numbers_prop n ∧
    non_empty_prop n
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

def zero_case_prop : Prop := string_sequence (0) (by simp) = "0"
@[simp] theorem zero_case_thm : zero_case_prop := by sorry

def starts_with_zero_prop (n : Nat) (result : String) : Prop :=
  result.startsWith "0"
@[simp] theorem starts_with_zero_thm (n : Nat) :
    starts_with_zero_prop (n) (string_sequence (n) (by simp)) := by
  sorry

def space_separated_prop (n : Nat) (result : String) : Prop :=
  n > 0 → result.contains ' '
@[simp] theorem space_separated_thm (n : Nat) :
    space_separated_prop (n) (string_sequence (n) (by simp)) := by
  sorry

def contains_all_numbers_prop (n : Nat) (result : String) : Prop :=
  ∀ k ≤ n, result.contains (toString k).front
@[simp] theorem contains_all_numbers_thm (n : Nat) :
    contains_all_numbers_prop (n) (string_sequence (n) (by simp)) := by
  sorry

def non_empty_prop (n : Nat) (result : String) : Prop := result.length > 0
@[simp] theorem non_empty_thm (n : Nat) :
    non_empty_prop (n) (string_sequence (n) (by simp)) := by
  sorry

-- !benchmark @end proof_aux


theorem string_sequence_spec_satisfied (n : Nat) (h_precond : string_sequence_precond (n)) :
    string_sequence_postcond (n) (string_sequence (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof