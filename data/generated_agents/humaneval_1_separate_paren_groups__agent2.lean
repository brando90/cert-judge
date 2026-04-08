```lean
import Lean
import Mathlib.Data.String.Basic
import Mathlib.Data.List.Basic

/-- 
Separates a string of nested parentheses into groups.
Each group is balanced (each open parenthesis has a matching close parenthesis) and
not nested within another group. Spaces in the input string are ignored.

For example, given '( ) (( )) (( )( ))', the function returns ['()', '(())', '(()())'].
-/
def separateParenGroups (parenString : String) : List String := 
  let rec loop (chars : List Char) (result : List String) (currentString : List Char) (currentDepth : Nat) :=
    match chars with
    | [] => result
    | c :: rest => 
      if c == '(' then 
        loop rest result (currentString ++ [c]) (currentDepth + 1)
      else if c == ')' then
        let newDepth := currentDepth - 1
        let newCurrentString := currentString ++ [c]
        if newDepth == 0 then
          loop rest (result ++ [String.mk newCurrentString]) [] 0
        else
          loop rest result newCurrentString newDepth
      else if c == ' ' then
        -- Ignore spaces
        loop rest result currentString currentDepth
      else
        -- Handle unexpected characters (just ignore them in this implementation)
        loop rest result currentString currentDepth
  
  loop parenString.toList [] [] 0

/--
Predicate that checks if a string is a balanced parenthesis group.
-/
def isBalancedParenGroup (s : String) : Bool :=
  let rec check (chars : List Char) (depth : Nat) : Bool :=
    match chars with
    | [] => depth == 0
    | c :: rest =>
      if c == '(' then check rest (depth + 1)
      else if c == ')' then 
        if depth == 0 then false
        else check rest (depth - 1)
      else check rest depth -- ignore other characters
  
  check s.toList 0

/--
Predicate that checks if a list of strings consists of balanced parenthesis groups.
-/
def areBalancedParenGroups (groups : List String) : Bool :=
  groups.all isBalancedParenGroup

/--
Specification: The result of separateParenGroups should be a list of balanced
parenthesis groups that, when joined, are equivalent to the input string with spaces removed.
-/
theorem separateParenGroups_spec (s : String) :
  let result := separateParenGroups s
  areBalancedParenGroups result ∧ 
  result.join = String.mk (s.toList.filter (· ≠ ' ')) := by
  sorry

/--
Tests for the separateParenGroups function
-/
def testSeparateParenGroups : IO Unit := do
  let test1 := separateParenGroups "(()()) ((())) () ((())()())"
  IO.println s!"Test 1: {test1}"
  assert! test1 == ["(()())", "((()))", "()", "((())()())"]
  
  let test2 := separateParenGroups "() (()) ((())) (((())))"
  IO.println s!"Test 2: {test2}"
  assert! test2 == ["()", "(())", "((()))", "(((())))"]
  
  let test3 := separateParenGroups "(()(())((())))"
  IO.println s!"Test 3: {test3}"
  assert! test3 == ["(()(())((())))" ]
  
  let test4 := separateParenGroups "( ) (( )) (( )( ))"
  IO.println s!"Test 4: {test4}"
  assert! test4 == ["()", "(())", "(()())"]
  
  IO.println "All tests passed!"

#eval testSeparateParenGroups
```
