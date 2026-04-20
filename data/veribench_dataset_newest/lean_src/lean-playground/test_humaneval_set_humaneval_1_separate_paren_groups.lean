import Mathlib

open List
namespace SeparateParenGroups


def separateParenGroups (parenString : String) : List String :=
  go parenString.toList [] [] 0
where
  
  go (chars : List Char)
     (acc : List (List Char))
     (cur : List Char)
     (depth : Int) : List String :=
    match chars with
    | [] => if depth == 0 then acc.map String.mk else []
    | c :: cs =>
      match c with
      | '(' => go cs acc (cur ++ [c]) (depth + 1)
      | ')' =>
        if depth <= 0 then []  -- Invalid: closing paren without matching open
        else
          let depth' := depth - 1
          let cur' := cur ++ [c]
          if depth' == 0 then
            go cs (acc ++ [cur']) [] 0
          else
            go cs acc cur' depth'
      | _ => go cs acc cur depth  -- Ignore non-parentheses characters


def separateParenGroupsImp (parenString : String) : List String := do
  let chars := parenString.toList
  let mut result : List String := []
  let mut current : List Char := []
  let mut depth : Int := 0
  
  for c in chars do
    match c with
    | '(' => 
      current := current ++ [c]
      depth := depth + 1
    | ')' =>
      if depth <= 0 then
        return []  -- Invalid input
      depth := depth - 1
      current := current ++ [c]
      if depth == 0 then
        result := result ++ [String.mk current]
        current := []
    | _ => continue  -- Ignore non-parentheses
  
  if depth != 0 then [] else result



/-!
# Tests
-/

/-- expected: ["(()())", "((()))", "()", "((())()())"] -/
example : separateParenGroups "(()()) ((())) () ((())()())" =
  ["(()())", "((()))", "()", "((())()())"] := by native_decide
#eval separateParenGroups "(()()) ((())) () ((())()())" -- expected: ["(()())", "((()))", "()", "((())()())"]

/-- expected: ["()", "(())", "(()())"] -/
example : separateParenGroups "( ) (( )) (( )( ))" =
  ["()", "(())", "(()())"] := by native_decide
#eval separateParenGroups "( ) (( )) (( )( ))" -- expected: ["()", "(())", "(()())"]

/-!
# Tests: Edge Cases
-/

/-- expected: [] -/
example : separateParenGroups "" = [] := by native_decide
#eval separateParenGroups "" -- expected: []

/-- expected: [] -/
example : separateParenGroups "   " = [] := by native_decide
#eval separateParenGroups "   " -- expected: []

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single balanced group -/
example : separateParenGroups "()" = ["()"] := by native_decide
#eval separateParenGroups "()" -- expected: ["()"]

/-- positive: multiple groups -/
example : separateParenGroups "()(())" = ["()", "(())"] := by native_decide
#eval separateParenGroups "()(())" -- expected: ["()", "(())"]

/-- negative: unbalanced parentheses return empty -/
example : ¬ (separateParenGroups "(" = ["("]) := by native_decide
#eval (decide (separateParenGroups "(" = ["("])) -- expected: false

/-- negative: unbalanced closing parentheses -/
example : ¬ (separateParenGroups ")" = [")"])  := by native_decide
#eval (decide (separateParenGroups ")" = [")"])) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single group -/
example : separateParenGroupsImp "()" = ["()"] := by native_decide
#eval separateParenGroupsImp "()" -- expected: ["()"]

/-- negative: unbalanced input gives empty result -/
example : ¬ (separateParenGroupsImp ")(" = [")("]) := by native_decide
#eval (decide (separateParenGroupsImp ")(" = [")("]))  -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem separateParenGroups_equivalence_thm (s : String) :
  separateParenGroups s = separateParenGroupsImp s := sorry




end SeparateParenGroups