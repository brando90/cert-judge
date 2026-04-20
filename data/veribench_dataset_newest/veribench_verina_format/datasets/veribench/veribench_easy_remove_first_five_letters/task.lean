-- !benchmark @start import type=solution
import Mathlib
namespace RemoveABCDEX
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Returns true if a character is one of 'a', 'b', 'c', 'd', 'e' -/
def isABCDEX (c : Char) : Bool :=
  c == 'a' || c == 'b' || c == 'c' || c == 'd' || c == 'e'
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def removeABCDEX_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def removeABCDEX (s : String) (h_precond : removeABCDEX_precond (s)) : String :=
  -- !benchmark @start code
  ⟨s.data.filter (fun c => ¬ isABCDEX c)⟩
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def removeABCDEX_postcond (s : String) (result : String) (h_precond : removeABCDEX_precond (s)) :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string remains empty. -/
def empty_string_prop : Prop := removeABCDEX "" (by simp) = ""

/-- **Empty string theorem**: Empty string remains empty. -/
@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

/-- **No target letters property**: Strings with no a,b,c,d,e remain unchanged. -/
def no_target_letters_prop (s : String) : Prop :=
  (∀ c ∈ s.data, c ≠ 'a' ∧ c ≠ 'b' ∧ c ≠ 'c' ∧ c ≠ 'd' ∧ c ≠ 'e') → removeABCDEX s (by simp) = s

/-- **No target letters theorem**: Strings with no a,b,c,d,e remain unchanged. -/
@[simp] theorem no_target_letters_thm (s : String) : no_target_letters_prop s := by
  sorry

/-- **Length bound property**: Result length is at most input length. -/
def length_bound_prop (s : String) : Prop :=
  (removeABCDEX s (by simp)).length ≤ s.length

/-- **Length bound theorem**: Result length is at most input length. -/
@[simp] theorem length_bound_thm (s : String) : length_bound_prop s := by
  sorry

/-- **Case sensitivity property**: Only lowercase a,b,c,d,e are removed. -/
def case_sensitivity_prop (s : String) : Prop :=
  ∀ c ∈ s.data,
    (c = 'A' ∨ c = 'B' ∨ c = 'C' ∨ c = 'D' ∨ c = 'E') → c ∈ (removeABCDEX s (by simp)).data

/-- **Case sensitivity theorem**: Only lowercase a,b,c,d,e are removed. -/
@[simp] theorem case_sensitivity_thm (s : String) : case_sensitivity_prop s := by
  sorry

/-- **Idempotence property**: Removing twice is same as once. -/
def idempotence_prop (s : String) : Prop :=
  removeABCDEX (removeABCDEX s (by simp)) (by simp) = removeABCDEX s (by simp)

/-- **Idempotence theorem**: Removing twice is same as once. -/
@[simp] theorem idempotence_thm (s : String) : idempotence_prop s := by
  sorry
-- !benchmark @end proof_aux

theorem removeABCDEX_spec_satisfied (s : String) (h_precond : removeABCDEX_precond (s)) :
    removeABCDEX_postcond (s) (removeABCDEX (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof