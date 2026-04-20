-- !benchmark @start import type=solution
import Mathlib
namespace HowManyTimes
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def how_many_times_precond (string : String) (substring : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

partial def how_many_times (string : String) (substring : String)
    (h_precond : how_many_times_precond (string) (substring)) : Nat :=
  -- !benchmark @start code
  if substring.length = 0 then 0
  else if substring.length > string.length then 0
  else
    let rec count_at_pos (pos : String.Pos) (acc : Nat) : Nat :=
      if pos.byteIdx + substring.length > string.length then
        acc
      else
        let current := string.extract pos ⟨pos.byteIdx + substring.length⟩
        if current = substring then
          count_at_pos ⟨pos.byteIdx + 1⟩ (acc + 1)
        else
          count_at_pos ⟨pos.byteIdx + 1⟩ acc
    count_at_pos ⟨0⟩ 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string has zero occurrences. -/
def empty_string_prop (substring : String) : Prop :=
  how_many_times "" substring (by simp) = 0

/-- **Empty string theorem**: Empty string has zero occurrences. -/
@[simp] theorem empty_string_thm (substring : String) : empty_string_prop substring := by
  sorry

/-- **Empty substring property**: Empty substring has zero occurrences. -/
def empty_substring_prop (string : String) : Prop :=
  how_many_times string "" (by simp) = 0

/-- **Empty substring theorem**: Empty substring has zero occurrences. -/
@[simp] theorem empty_substring_thm (string : String) : empty_substring_prop string := by
  sorry

/-- **Non-negative property**: Count is always non-negative. -/
def non_negative_prop (string substring : String) : Prop :=
  how_many_times string substring (by simp) ≥ 0

/-- **Non-negative theorem**: Count is always non-negative. -/
@[simp] theorem non_negative_thm (string substring : String) : non_negative_prop string substring := by
  sorry

/-- **Upper bound property**: Count is bounded by string length. -/
def upper_bound_prop (string substring : String) : Prop :=
  substring.length > 0 → how_many_times string substring (by simp) ≤ string.length

/-- **Upper bound theorem**: Count is bounded by string length. -/
@[simp] theorem upper_bound_thm (string substring : String) : upper_bound_prop string substring := by
  sorry

/-- **Longer pattern property**: If substring is longer than string, count is zero. -/
def longer_pattern_prop (string substring : String) : Prop :=
  substring.length > string.length → how_many_times string substring (by simp) = 0

/-- **Longer pattern theorem**: If substring is longer than string, count is zero. -/
@[simp] theorem longer_pattern_thm (string substring : String) : longer_pattern_prop string substring := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def how_many_times_postcond (string : String) (substring : String) (result : Nat)
    (h_precond : how_many_times_precond (string) (substring)) : Prop :=
  -- !benchmark @start postcond
  (empty_string_prop substring) ∧
    (empty_substring_prop string) ∧
    (non_negative_prop string substring) ∧
    (upper_bound_prop string substring) ∧
    (longer_pattern_prop string substring)
  -- !benchmark @end postcond

theorem how_many_times_spec_satisfied (string : String) (substring : String)
    (h_precond : how_many_times_precond (string) (substring)) :
    how_many_times_postcond (string) (substring) (how_many_times (string) (substring) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof