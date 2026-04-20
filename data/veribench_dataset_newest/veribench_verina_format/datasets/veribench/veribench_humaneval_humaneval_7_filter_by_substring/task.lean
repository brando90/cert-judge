-- !benchmark @start import type=solution
import Mathlib
namespace FilterBySubstring

open List String
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def filterBySubstring_precond (strings : List String) (substring : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/--
Helper function to check if a list is a prefix of another list.
-/
private def startsWith (pre : List Char) (xs : List Char) : Bool :=
  match pre, xs with
  | [], _ => true
  | _, [] => false
  | p :: ps, x :: xs' => (p == x) && startsWith ps xs'

/--
Helper function to get a slice of a list from index i to j-1.
-/
private def slice (xs : List Char) (i j : Nat) : List Char :=
  let rec take (n : Nat) (ys : List Char) : List Char :=
    match n, ys with
    | 0, _ => []
    | _, [] => []
    | n + 1, y :: ys' => y :: take n ys'
  let rec drop (n : Nat) (ys : List Char) : List Char :=
    match n, ys with
    | 0, ys => ys
    | _, [] => []
    | n + 1, _ :: ys' => drop n ys'
  take (j - i) (drop i xs)

/--
Check if a string contains another string as a substring.

Given two strings `sub` and `s`, returns `true` if `sub` appears as a contiguous
substring within `s`. Empty substring is considered to be contained in any string.
-/
def isInfixOf (sub s : String) : Bool :=
  if sub.isEmpty then
    true
  else
    Id.run do
      let subList := sub.toList
      let sList   := s.toList
      let nSub    := subList.length
      let nS      := sList.length
      for i in [0:nS] do
        if i + nSub <= nS then
          let slice := slice sList i (i + nSub)
          if slice == subList then
            return true
        else
          break
      return false
-- !benchmark @end code_aux

def filterBySubstring (strings : List String) (substring : String)
    (h_precond : filterBySubstring_precond (strings) (substring)) : List String :=
  -- !benchmark @start code
  strings.filter (isInfixOf substring)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def filterBySubstring_postcond (strings : List String) (substring : String) (result : List String)
    (h_precond : filterBySubstring_precond (strings) (substring)) : Prop :=
  -- !benchmark @start postcond
  (∀ s, s ∈ result → s ∈ strings) ∧
  (∀ s, s ∈ result → isInfixOf substring s = true) ∧
  (∀ t, isInfixOf substring t = false → t ∉ result) ∧
  (∀ s, s ∈ strings ∧ isInfixOf substring s = true → s ∈ result) ∧
  (filterBySubstring strings "" (by simp) = strings)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
def result_in_original_prop (strings : List String) (sub : String) : Prop :=
  ∀ s, s ∈ filterBySubstring strings sub (by simp) → s ∈ strings

@[simp] theorem result_in_original_thm (strings : List String) (sub : String) :
    result_in_original_prop strings sub := by
  sorry

def satisfies_predicate_prop (strings : List String) (sub : String) : Prop :=
  ∀ s, s ∈ filterBySubstring strings sub (by simp) → isInfixOf sub s = true

@[simp] theorem satisfies_predicate_thm (strings : List String) (sub : String) :
    satisfies_predicate_prop strings sub := by
  sorry

def excludes_false_prop (strings : List String) (sub : String) : Prop :=
  ∀ t, isInfixOf sub t = false → t ∉ filterBySubstring strings sub (by simp)

@[simp] theorem excludes_false_thm (strings : List String) (sub : String) :
    excludes_false_prop strings sub := by
  sorry

def includes_all_prop (strings : List String) (sub : String) : Prop :=
  ∀ s, s ∈ strings ∧ isInfixOf sub s = true → s ∈ filterBySubstring strings sub (by simp)

@[simp] theorem includes_all_thm (strings : List String) (sub : String) :
    includes_all_prop strings sub := by
  sorry

def empty_substring_prop (strings : List String) : Prop :=
  filterBySubstring strings "" (by simp) = strings

@[simp] theorem empty_substring_thm (strings : List String) : empty_substring_prop strings := by
  sorry
-- !benchmark @end proof_aux

theorem filterBySubstring_spec_satisfied (strings : List String) (substring : String)
    (h_precond : filterBySubstring_precond (strings) (substring)) :
    filterBySubstring_postcond (strings) (substring)
      (filterBySubstring (strings) (substring) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof