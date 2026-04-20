-- !benchmark @start import type=solution
import Mathlib
namespace CountDistinctCharacters
-- !benchmark @end import

-- !benchmark @start solution_aux
open List String
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def countDistinctCharacters_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def countDistinctCharacters (s : String) (h_precond : countDistinctCharacters_precond (s)) : Nat :=
  -- !benchmark @start code
  let chars := s.toLower.toList
  let unique := chars.eraseDups
  unique.length
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def countDistinctCharacters_postcond (s : String) (result : Nat)
    (h_precond : countDistinctCharacters_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (result = countDistinctCharacters (s) h_precond) ∧
    (countDistinctCharacters "" (by simp) = 0) ∧
    (∀ s1 s2,
        (s1.toLower = s2.toLower →
          countDistinctCharacters (s1) (by simp) = countDistinctCharacters (s2) (by simp))) ∧
    (countDistinctCharacters (s) h_precond ≤ s.length) ∧
    (countDistinctCharacters (s) h_precond ≥ 0) ∧
    (∀ c, countDistinctCharacters (s.push c) (by simp) ≤ countDistinctCharacters (s) h_precond + 1)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def empty_string_prop : Prop := countDistinctCharacters "" (by simp) = 0
@[simp] theorem empty_string_thm : empty_string_prop := by sorry

def case_insensitive_prop (s1 s2 : String) : Prop :=
  s1.toLower = s2.toLower → countDistinctCharacters (s1) (by simp) = countDistinctCharacters (s2) (by simp)
@[simp] theorem case_insensitive_thm (s1 s2 : String) : case_insensitive_prop s1 s2 := by sorry

def upper_bound_prop (s : String) : Prop := countDistinctCharacters (s) (by simp) ≤ s.length
@[simp] theorem upper_bound_thm (s : String) : upper_bound_prop s := by sorry

def non_negative_prop (s : String) : Prop := countDistinctCharacters (s) (by simp) ≥ 0
@[simp] theorem non_negative_thm (s : String) : non_negative_prop s := by sorry

def monotonicity_prop (s : String) (c : Char) : Prop :=
  countDistinctCharacters (s.push c) (by simp) ≤ countDistinctCharacters (s) (by simp) + 1
@[simp] theorem monotonicity_thm (s : String) (c : Char) : monotonicity_prop s c := by sorry

-- !benchmark @end proof_aux

theorem countDistinctCharacters_spec_satisfied (s : String) (h_precond : countDistinctCharacters_precond (s)) :
    countDistinctCharacters_postcond (s) (countDistinctCharacters (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof