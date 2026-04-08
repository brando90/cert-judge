```lean
import Std.Data.List.Basic

/--
Separates groups of nested parentheses into separate strings.
Each group is balanced (each open brace is properly closed) and not nested within other groups.
Spaces in the input string are ignored.
-/
def separateParenGroups (parenString : String) : List String :=
  let rec processString (chars : List Char) (result : List String) (currentString : List Char) (currentDepth : Nat) : List String :=
    match chars with
    | [] => result
    | c :: rest =>
      if c == '(' then
        processString rest result (currentString ++ ['(']) (currentDepth + 1)
      else if c == ')' then
        let newCurrentString := currentString ++ [')']
        let newDepth := currentDepth - 1
        if newDepth == 0 then
          processString rest (result ++ [String.mk newCurrentString]) [] 0
        else
          processString rest result newCurrentString newDepth
      else if c == ' ' then
        -- Ignore spaces
        processString rest result currentString currentDepth
      else
        -- Other characters (shouldn't happen in this problem)
        processString rest result currentString currentDepth
  
  processString parenString.toList [] [] 0

/-!
## Specification
-/

/-- 
Predicate indicating if a string has balanced parentheses
-/
def hasBalancedParens (s : String) : Bool :=
  let rec checkBalance (chars : List Char) (count : Int) : Bool :=
    match chars with
    | [] => count == 0
    | c :: rest =>
      if c == '(' then checkBalance rest (count + 1)
      else if c == ')' then 
        if count <= 0 then false
        else checkBalance rest (count - 1)
      else checkBalance rest count
  checkBalance s.toList 0

/--
Predicate indicating if a character is a parenthesis
-/
def isParenChar (c : Char) : Bool :=
  c == '(' || c == ')'

/--
Predicate indicating if a string contains only parentheses and spaces
-/
def containsOnlyParensAndSpaces (s : String) : Bool :=
  s.toList.all (fun c => isParenChar c || c == ' ')

/--
Predicate indicating if a string is a valid parentheses group (balanced and contains only parentheses)
-/
def isValidParenGroup (s : String) : Bool :=
  hasBalancedParens s && s.toList.all isParenChar

/--
Precondition for separateParenGroups:
The input string should contain only parentheses and spaces,
and have balanced parentheses overall.
-/
def separateParenGroups.pre (input : String) : Prop :=
  containsOnlyParensAndSpaces input && hasBalancedParens input

/--
Postcondition for separateParenGroups:
1. Each group in the result is a valid parentheses group
2. The concatenation of all groups equals the input string with spaces removed
-/
def separateParenGroups.post (input : String) (output : List String) : Prop :=
  (output.all isValidParenGroup) && 
  (String.mk (input.toList.filter (fun c => c != ' ')) = String.join output)

/-!
## Correctness theorem
-/

theorem separateParenGroups.correct (input : String) :
  separateParenGroups.pre input → 
  separateParenGroups.post input (separateParenGroups input) :=
  sorry

/-!
## Tests
-/

#eval separateParenGroups "(()()) ((())) () ((())()())"
-- ["(()())", "((()))", "()", "((())()())"]

#eval separateParenGroups "() (()) ((())) (((())))"
-- ["()", "(())", "((()))", "(((())))" ]

#eval separateParenGroups "(()(())((())))"
-- ["(()(())((())))" ]

#eval separateParenGroups "( ) (( )) (( )( ))"
-- ["()", "(())", "(()())" ]

example : separateParenGroups "(()()) ((())) () ((())()())" = ["(()())", "((()))", "()", "((())()())"] := rfl
example : separateParenGroups "() (()) ((())) (((())))" = ["()", "(())", "((()))", "(((())))" ] := rfl
example : separateParenGroups "(()(())((())))" = ["(()(())((())))" ] := rfl
example : separateParenGroups "( ) (( )) (( )( ))" = ["()", "(())", "(()())" ] := rfl
```
