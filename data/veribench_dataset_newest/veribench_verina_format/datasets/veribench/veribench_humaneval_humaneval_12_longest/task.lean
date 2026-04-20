-- !benchmark @start import type=solution
import Mathlib
namespace LongestString
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def longest_precond (strings : List String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def longest (strings : List String) (h_precond : longest_precond (strings)) : Option String :=
  -- !benchmark @start code
  match strings with
  | [] => none
  | xs =>
    let maxlen := xs.map String.length |>.max?.getD 0
    xs.find? (fun s => s.length = maxlen)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def longest_postcond (strings : List String) (result : Option String) (h_precond : longest_precond (strings)) : Prop :=
  -- !benchmark @start postcond
  (longest [] (by simp) = none) ∧
  (∀ s, result = some s → ∀ s' ∈ strings, s.length ≥ s'.length) ∧
  (∀ s, result = some s → s ∈ strings) ∧
  (∀ s, result = some s →
      ∀ s' ∈ strings, s'.length = s.length → strings.idxOf s ≤ strings.idxOf s') ∧
  (strings ≠ [] → result.isSome)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def empty_list_prop : Prop := longest [] (by simp) = none

@[simp] theorem empty_list_thm : empty_list_prop := sorry

def maximal_prop (strings : List String) : Prop :=
  ∀ s, longest strings (by simp) = some s → ∀ s' ∈ strings, s.length ≥ s'.length

@[simp] theorem maximal_thm (strings : List String) : maximal_prop strings := sorry

def membership_prop (strings : List String) : Prop :=
  ∀ s, longest strings (by simp) = some s → s ∈ strings

@[simp] theorem membership_thm (strings : List String) : membership_prop strings := sorry

def first_occurrence_prop (strings : List String) : Prop :=
  ∀ s, longest strings (by simp) = some s →
    ∀ s' ∈ strings, s'.length = s.length → strings.idxOf s ≤ strings.idxOf s'

@[simp] theorem first_occurrence_thm (strings : List String) : first_occurrence_prop strings := sorry

def non_empty_result_prop (strings : List String) : Prop :=
  strings ≠ [] → (longest strings (by simp)).isSome

@[simp] theorem non_empty_result_thm (strings : List String) : non_empty_result_prop strings := sorry

-- !benchmark @end proof_aux

theorem longest_spec_satisfied (strings : List String) (h_precond : longest_precond (strings)) :
    longest_postcond (strings) (longest (strings) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof