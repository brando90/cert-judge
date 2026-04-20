-- !benchmark @start import type=solution
import Mathlib
namespace AllPrefixes
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def all_prefixes_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def all_prefixes (s : String) (h_precond : all_prefixes_precond (s)) : List String :=
  -- !benchmark @start code
  let rec build_prefixes (n : Nat) (fuel : Nat) : List String :=
    match fuel with
    | 0 => []
    | fuel' + 1 =>
      if n > s.length then []
      else (s.take n) :: build_prefixes (n + 1) fuel'
  build_prefixes 1 (s.length)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string returns empty list. -/
def empty_string_prop : Prop := all_prefixes ("") (by simp) = []

/-- **Empty string theorem**: Empty string returns empty list. -/
@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

/-- **Single character property**: Single character returns list with that character. -/
def single_char_prop (c : Char) : Prop :=
  all_prefixes (String.mk [c]) (by simp) = [String.mk [c]]

/-- **Single character theorem**: Single character returns list with that character. -/
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by
  sorry

/-- **Length bound property**: Number of prefixes is at most string length. -/
def length_bound_prop (s : String) : Prop :=
  (all_prefixes (s) (by simp)).length ≤ s.length

/-- **Length bound theorem**: Number of prefixes is at most string length. -/
@[simp] theorem length_bound_thm (s : String) : length_bound_prop s := by
  sorry

/-- **Prefix validity property**: All returned strings are actual prefixes. -/
def prefix_validity_prop (s : String) : Prop :=
  ∀ p ∈ all_prefixes (s) (by simp), ∃ n, s.take n = p

/-- **Prefix validity theorem**: All returned strings are actual prefixes. -/
@[simp] theorem prefix_validity_thm (s : String) : prefix_validity_prop s := by
  sorry

/-- **Ordering property**: Prefixes are ordered by increasing length. -/
def ordering_prop (s : String) : Prop :=
  ∀ i j,
    i < j →
      j < (all_prefixes (s) (by simp)).length →
        (all_prefixes (s) (by simp))[i]!.length < (all_prefixes (s) (by simp))[j]!.length

/-- **Ordering theorem**: Prefixes are ordered by increasing length. -/
@[simp] theorem ordering_thm (s : String) : ordering_prop s := by
  sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def all_prefixes_postcond (s : String) (result : List String) (h_precond : all_prefixes_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (empty_string_prop) ∧
    (∀ c, single_char_prop c) ∧
      (length_bound_prop s) ∧ (prefix_validity_prop s) ∧ (ordering_prop s)
  -- !benchmark @end postcond

theorem all_prefixes_spec_satisfied (s : String) (h_precond : all_prefixes_precond (s)) :
    all_prefixes_postcond (s) (all_prefixes (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof