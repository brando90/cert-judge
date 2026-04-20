-- !benchmark @start import type=solution
import Mathlib
namespace SeparateParenGroups

open List
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def separateParenGroups_precond (parenString : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def separateParenGroups (parenString : String) (h_precond : separateParenGroups_precond (parenString)) : List String :=
  -- !benchmark @start code
  go parenString.toList [] [] 0
where
  go (chars : List Char) (acc : List (List Char)) (cur : List Char) (depth : Int) : List String :=
    match chars with
    | [] => acc.map String.mk
    | c :: cs =>
      match c with
      | '(' => go cs acc (cur ++ [c]) (depth + 1)
      | ')' =>
        let depth' := depth - 1
        let cur' := cur ++ [c]
        if depth' == 0 then
          go cs (acc ++ [cur']) [] 0
        else
          go cs acc cur' depth'
      | _ => go cs acc cur depth
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def separateParenGroups_postcond (parenString : String) (result : List String)
    (h_precond : separateParenGroups_precond (parenString)) : Prop :=
  -- !benchmark @start postcond
  let empty_string_prop : Prop := separateParenGroups "" (by simp) = []
  let single_group_prop : Prop := separateParenGroups "()" (by simp) = ["()"]
  let multiple_groups_prop : Prop := separateParenGroups "()(())" (by simp) = ["()", "(())"]
  let whitespace_ignored_prop : Prop := separateParenGroups "  () (())  " (by simp) = ["()", "(())"]
  let unbalanced_input_prop (s : String) : Prop :=
    (∃ c ∈ s.toList, c ∉ ['(', ')', ' ']) ∨ (s.toList.count '(' ≠ s.toList.count ')') →
      separateParenGroups s (by simp) = []
  (empty_string_prop) ∧
    (single_group_prop) ∧
    (multiple_groups_prop) ∧
    (whitespace_ignored_prop) ∧
    (unbalanced_input_prop parenString)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def empty_string_prop : Prop := separateParenGroups "" (by simp) = []

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def single_group_prop : Prop := separateParenGroups "()" (by simp) = ["()"]

@[simp] theorem single_group_thm : single_group_prop := by
  sorry

def multiple_groups_prop : Prop :=
  separateParenGroups "()(())" (by simp) = ["()", "(())"]

@[simp] theorem multiple_groups_thm : multiple_groups_prop := by
  sorry

def whitespace_ignored_prop : Prop :=
  separateParenGroups "  () (())  " (by simp) = ["()", "(())"]

@[simp] theorem whitespace_ignored_thm : whitespace_ignored_prop := by
  sorry

def unbalanced_input_prop (s : String) : Prop :=
  (∃ c ∈ s.toList, c ∉ ['(', ')', ' ']) ∨ (s.toList.count '(' ≠ s.toList.count ')') →
    separateParenGroups s (by simp) = []

@[simp] theorem unbalanced_input_thm (s : String) : unbalanced_input_prop s := by
  sorry

-- !benchmark @end proof_aux

theorem separateParenGroups_spec_satisfied (parenString : String)
    (h_precond : separateParenGroups_precond (parenString)) :
    separateParenGroups_postcond (parenString) (separateParenGroups (parenString) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof