-- !benchmark @start import type=solution
import Mathlib
namespace LongestCommonSubsequence
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def longestCommonSubsequence_precond (s1 : String) (s2 : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

/-- Check if a list is a subsequence of another -/
def List.isSubsequence [DecidableEq α] (sub : List α) (sup : List α) : Bool :=
  match sub, sup with
  | [], _ => true
  | _, [] => false
  | h₁::t₁, h₂::t₂ =>
    if h₁ = h₂ then
      isSubsequence t₁ t₂
    else
      isSubsequence (h₁::t₁) t₂

/-- Check if a string is a subsequence of another -/
def String.isSubsequence (sub : String) (sup : String) : Bool :=
  List.isSubsequence sub.toList sup.toList

-- !benchmark @end code_aux


def longestCommonSubsequence (s1 : String) (s2 : String)
    (h_precond : longestCommonSubsequence_precond (s1) (s2)) : String :=
  -- !benchmark @start code
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    -- Simplified implementation: find common characters in order
    let chars1 := s1.toList
    let chars2 := s2.toList
    let rec findCommon (l1 l2 : List Char) (acc : List Char) : List Char :=
      match l1, l2 with
      | [], _ => acc.reverse
      | _, [] => acc.reverse
      | h1::t1, h2::t2 =>
        if h1 = h2 then
          findCommon t1 t2 (h1::acc)
        else
          let try1 := findCommon t1 (h2::t2) acc
          let try2 := findCommon (h1::t1) t2 acc
          if try1.length >= try2.length then try1 else try2
    String.mk (findCommon chars1 chars2 [])
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def longestCommonSubsequence_postcond (s1 : String) (s2 : String) (result : String)
    (h_precond : longestCommonSubsequence_precond (s1) (s2)) :=
  -- !benchmark @start postcond
  (∀ s, empty_string_prop s) ∧
  (subsequence_prop s1 s2) ∧
  (self_lcs_prop s1) ∧
  (commutativity_prop s1 s2) ∧
  (length_bound_prop s1 s2)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

/-- **Empty string property**: LCS with empty string is empty string. -/
def empty_string_prop (s : String) : Prop :=
  longestCommonSubsequence (s) ("") (by simp) = "" ∧
    longestCommonSubsequence ("") (s) (by simp) = ""

/-- **Empty string theorem**: LCS with empty string is empty string. -/
@[simp] theorem empty_string_thm (s : String) : empty_string_prop s := by
  sorry

/-- **Subsequence property**: Result is a subsequence of both inputs. -/
def subsequence_prop (s1 s2 : String) : Prop :=
  let lcs := longestCommonSubsequence (s1) (s2) (by simp)
  String.isSubsequence lcs s1 ∧ String.isSubsequence lcs s2

/-- **Subsequence theorem**: Result is a subsequence of both inputs. -/
@[simp] theorem subsequence_thm (s1 s2 : String) : subsequence_prop s1 s2 := by
  sorry

/-- **Self LCS property**: LCS of a string with itself equals the string. -/
def self_lcs_prop (s : String) : Prop :=
  longestCommonSubsequence (s) (s) (by simp) = s

/-- **Self LCS theorem**: LCS of a string with itself equals the string. -/
@[simp] theorem self_lcs_thm (s : String) : self_lcs_prop s := by
  sorry

/-- **Commutativity property**: LCS is commutative. -/
def commutativity_prop (s1 s2 : String) : Prop :=
  longestCommonSubsequence (s1) (s2) (by simp) =
    longestCommonSubsequence (s2) (s1) (by simp)

/-- **Commutativity theorem**: LCS is commutative. -/
@[simp] theorem commutativity_thm (s1 s2 : String) : commutativity_prop s1 s2 := by
  sorry

/-- **Length bound property**: LCS length is bounded by minimum of input lengths. -/
def length_bound_prop (s1 s2 : String) : Prop :=
  (longestCommonSubsequence (s1) (s2) (by simp)).length ≤ min s1.length s2.length

/-- **Length bound theorem**: LCS length is bounded by minimum of input lengths. -/
@[simp] theorem length_bound_thm (s1 s2 : String) : length_bound_prop s1 s2 := by
  sorry

-- !benchmark @end proof_aux


theorem longestCommonSubsequence_spec_satisfied (s1 : String) (s2 : String)
    (h_precond : longestCommonSubsequence_precond (s1) (s2)) :
    longestCommonSubsequence_postcond (s1) (s2)
      (longestCommonSubsequence (s1) (s2) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof