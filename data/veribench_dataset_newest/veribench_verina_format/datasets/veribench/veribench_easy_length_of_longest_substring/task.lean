-- !benchmark @start import type=solution
import Mathlib
namespace LongestSubstring
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def lengthOfLongestSubstring_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
/-- Check if a list has unique characters -/
def List.hasUniqueChars (chars : List Char) : Bool :=
  let rec aux (seen : List Char) (rest : List Char) : Bool :=
    match rest with
    | [] => true
    | h :: t =>
      if h ∈ seen then
        false
      else
        aux (h :: seen) t
  aux [] chars

/-- Check if a string has unique characters -/
def String.hasUniqueChars (s : String) : Bool :=
  List.hasUniqueChars s.toList
-- !benchmark @end code_aux


def lengthOfLongestSubstring (s : String) (h_precond : lengthOfLongestSubstring_precond (s)) : Nat :=
  -- !benchmark @start code
  if s.isEmpty then
    0
  else
    let chars := s.toList
    let n := chars.length
    let substrings := (List.range n).flatMap fun i =>
      (List.range (n - i + 1)).map fun len =>
        if i + len <= n then
          chars.drop i |>.take len
        else
          []
    let uniqueSubstrings := substrings.filter (fun sub => sub ≠ [] && List.hasUniqueChars sub)
    uniqueSubstrings.foldl (fun acc sub => max acc sub.length) 0
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def lengthOfLongestSubstring_postcond (s : String) (result : Nat)
    (h_precond : lengthOfLongestSubstring_precond (s)) : Prop :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string has length 0. -/
def empty_string_prop : Prop := lengthOfLongestSubstring "" (by simp) = 0

/-- **Empty string theorem**: Empty string has length 0. -/
@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

/-- **Single char property**: Single character has length 1. -/
def single_char_prop (c : Char) : Prop := lengthOfLongestSubstring c.toString (by simp) = 1

/-- **Single char theorem**: Single character has length 1. -/
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by
  sorry

/-- **Upper bound property**: Result is at most string length. -/
def upper_bound_prop (s : String) : Prop := lengthOfLongestSubstring s (by simp) ≤ s.length

/-- **Upper bound theorem**: Result is at most string length. -/
@[simp] theorem upper_bound_thm (s : String) : upper_bound_prop s := by
  sorry

/-- **Non-negative property**: Result is always non-negative. -/
def non_negative_prop (s : String) : Prop := lengthOfLongestSubstring s (by simp) ≥ 0

/-- **Non-negative theorem**: Result is always non-negative. -/
@[simp] theorem non_negative_thm (s : String) : non_negative_prop s := by
  sorry

/-- **Unique substring property**: If string has all unique chars, result equals string length. -/
def unique_substring_prop (s : String) : Prop :=
  String.hasUniqueChars s → lengthOfLongestSubstring s (by simp) = s.length

/-- **Unique substring theorem**: If string has all unique chars, result equals string length. -/
@[simp] theorem unique_substring_thm (s : String) : unique_substring_prop s := by
  sorry
-- !benchmark @end proof_aux


theorem lengthOfLongestSubstring_spec_satisfied (s : String)
    (h_precond : lengthOfLongestSubstring_precond (s)) :
    lengthOfLongestSubstring_postcond (s) (lengthOfLongestSubstring (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof