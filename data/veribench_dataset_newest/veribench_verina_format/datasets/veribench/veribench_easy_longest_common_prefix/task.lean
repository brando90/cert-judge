-- !benchmark @start import type=solution
import Mathlib
namespace LongestCommonPrefix
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def longestCommonPrefix_precond (strs : List String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

/-- Get minimum length among a list of strings -/
def List.minLength (strs : List String) : Nat :=
  match strs with
  | [] => 0
  | h :: t => t.foldl (fun acc s => min acc s.length) h.length

/-- Check if all strings start with a given prefix -/
def List.allStartWith (p : String) (strs : List String) : Bool :=
  strs.all (fun s => s.startsWith p)

-- !benchmark @end code_aux

def longestCommonPrefix (strs : List String) (h_precond : longestCommonPrefix_precond (strs)) : String :=
  -- !benchmark @start code
  match strs with
  | [] => ""
  | [s] => s
  | h :: t =>
    let minLen := List.minLength (h :: t)
    if minLen = 0 then
      ""
    else
      let chars := h.toList
      let rec findPrefix (i : Nat) : String :=
        if i >= minLen then
          String.mk (chars.take i)
        else
          let c := chars[i]!
          if t.all (fun s => s.toList[i]! = c) then
            findPrefix (i + 1)
          else
            String.mk (chars.take i)
      termination_by minLen - i
      findPrefix 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def longestCommonPrefix_postcond (strs : List String) (result : String)
    (h_precond : longestCommonPrefix_precond (strs)) :=
  -- !benchmark @start postcond
  (longestCommonPrefix [] (by simp) = "") ∧
    (∀ s, longestCommonPrefix [s] (by simp) = s) ∧
    (∀ s ∈ strs, result.isPrefixOf s) ∧
    (∀ t : String, t.length > result.length → ∃ s ∈ strs, ¬t.isPrefixOf s) ∧
    (("" ∈ strs) → result = "")
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

/-- **Empty list property**: Longest common prefix of empty list is empty string. -/
def empty_list_prop : Prop := longestCommonPrefix [] (by simp) = ""

/-- **Empty list theorem**: Longest common prefix of empty list is empty string. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Single string property**: Longest common prefix of single string is that string. -/
def single_string_prop (s : String) : Prop := longestCommonPrefix [s] (by simp) = s

/-- **Single string theorem**: Longest common prefix of single string is that string. -/
@[simp] theorem single_string_thm (s : String) : single_string_prop s := by
  sorry

/-- **Prefix property**: Result is a prefix of all input strings. -/
def prefix_prop (strs : List String) : Prop :=
  ∀ s ∈ strs, (longestCommonPrefix strs (by simp)).isPrefixOf s

/-- **Prefix theorem**: Result is a prefix of all input strings. -/
@[simp] theorem prefix_thm (strs : List String) : prefix_prop strs := by
  sorry

/-- **Maximality property**: No longer string is a common prefix. -/
def maximality_prop (strs : List String) : Prop :=
  ∀ t : String,
    t.length > (longestCommonPrefix strs (by simp)).length → ∃ s ∈ strs, ¬t.isPrefixOf s

/-- **Maximality theorem**: No longer string is a common prefix. -/
@[simp] theorem maximality_thm (strs : List String) : maximality_prop strs := by
  sorry

/-- **Empty string handling property**: If any string is empty, result is empty. -/
def empty_string_prop (strs : List String) : Prop := ("" ∈ strs) → longestCommonPrefix strs (by simp) = ""

/-- **Empty string handling theorem**: If any string is empty, result is empty. -/
@[simp] theorem empty_string_thm (strs : List String) : empty_string_prop strs := by
  sorry

-- !benchmark @end proof_aux

theorem longestCommonPrefix_spec_satisfied (strs : List String)
    (h_precond : longestCommonPrefix_precond (strs)) :
    longestCommonPrefix_postcond (strs) (longestCommonPrefix (strs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof