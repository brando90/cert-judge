-- !benchmark @start import type=solution
import Mathlib
namespace ParseNestedParens

open List String
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def parseNestedParens_precond (parenString : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

/--
Helper function to compute the maximum nesting depth of a single group
of parentheses.
-/
def parseParenGroup (s : String) : Nat :=
  go s.toList 0 0
where
  go (cs : List Char) (currDepth maxDepth : Nat) : Nat :=
    match cs with
    | [] => maxDepth
    | c :: rest =>
      if c = '(' then
        let currDepth' := currDepth + 1
        let maxDepth' := if currDepth' > maxDepth then currDepth' else maxDepth
        go rest currDepth' maxDepth'
      else if c = ')' then
        let currDepth' := currDepth - 1
        go rest currDepth' maxDepth
      else
        go rest currDepth maxDepth

-- !benchmark @end code_aux

def parseNestedParens (parenString : String) (h_precond : parseNestedParens_precond (parenString)) : List Nat :=
  -- !benchmark @start code
  let groups := parenString.split (· = ' ')
  let filtered := groups.filter (·.length > 0)
  filtered.map parseParenGroup
  -- !benchmark @end code

-- !benchmark @start postcond_aux

/-- **Empty string property**: Empty string returns empty list. -/
def empty_string_prop : Prop := parseNestedParens "" (by simp) = []

/-- **Single group property**: Single group returns singleton list. -/
def single_group_prop (s : String) : Prop :=
  (∀ c ∈ s.toList, c = '(' ∨ c = ')') →
    parseNestedParens s (by simp) = [parseParenGroup s]

/-- **Length preservation property**: Number of groups equals number of results. -/
def length_preservation_prop (parenString : String) : Prop :=
  let groups := parenString.split (· = ' ')
  let filtered := groups.filter (·.length > 0)
  (parseNestedParens parenString (by simp)).length = filtered.length

/-- **Group independence property**: Each group is processed independently. -/
def group_independence_prop (s1 s2 : String) : Prop :=
  parseNestedParens (s1 ++ " " ++ s2) (by simp) =
    parseNestedParens s1 (by simp) ++ parseNestedParens s2 (by simp)

/-- **Non-negative depth property**: All depths are non-negative. -/
def non_negative_depth_prop (parenString : String) : Prop :=
  ∀ d ∈ parseNestedParens parenString (by simp), d ≥ 0

-- !benchmark @end postcond_aux

@[reducible, simp]
def parseNestedParens_postcond (parenString : String) (result : List Nat)
    (h_precond : parseNestedParens_precond (parenString)) : Prop :=
  -- !benchmark @start postcond
  (empty_string_prop) ∧
    (∀ s, single_group_prop s) ∧
    (length_preservation_prop parenString) ∧
    (∀ s1 s2, group_independence_prop s1 s2) ∧
    (non_negative_depth_prop parenString)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

@[simp] theorem single_group_thm (s : String) : single_group_prop s := by
  sorry

@[simp] theorem length_preservation_thm (parenString : String) : length_preservation_prop parenString := by
  sorry

@[simp] theorem group_independence_thm (s1 s2 : String) : group_independence_prop s1 s2 := by
  sorry

@[simp] theorem non_negative_depth_thm (parenString : String) : non_negative_depth_prop parenString := by
  sorry

-- !benchmark @end proof_aux

theorem parseNestedParens_spec_satisfied (parenString : String)
    (h_precond : parseNestedParens_precond (parenString)) :
    parseNestedParens_postcond (parenString) (parseNestedParens (parenString) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof