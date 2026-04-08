import Lean
import Std.Data.List.Basic

def isSpace (c : Char) : Bool :=
  c == ' '

def separate_paren_groups (paren_string : String) : List String :=
  let rec process (chars : List Char) (result : List String) (current : List Char) (depth : Nat) : List String :=
    match chars with
    | [] => result
    | c :: rest =>
      if isSpace c then
        process rest result current depth
      else if c == '(' then
        process rest result (current ++ [c]) (depth + 1)
      else if c == ')' then
        let new_current := current ++ [c]
        let new_depth := depth - 1
        if new_depth == 0 then
          process rest (result ++ [String.mk new_current]) [] 0
        else
          process rest result new_current new_depth
      else
        process rest result current depth
  process paren_string.toList [] [] 0

/-- Specification for separate_paren_groups:
    Given a string containing multiple groups of nested parentheses,
    separate those groups into a list of strings.
    Each group is balanced and not nested within another group.
    Spaces in the input string are ignored.
-/

def isBalancedParens (s : String) : Bool :=
  let rec check (chars : List Char) (count : Int) : Bool :=
    match chars with
    | [] => count == 0
    | c :: rest =>
      if c == '(' then check rest (count + 1)
      else if c == ')' then count > 0 && check rest (count - 1)
      else check rest count
  check s.toList 0

/-- Precondition: The input string should only contain parentheses and spaces -/
def separate_paren_groups_pre (s : String) : Prop :=
  s.all (fun c => c == '(' || c == ')' || c == ' ')

/-- Postcondition: 
    1. Each string in the result is balanced
    2. The concatenation of all strings in the result (ignoring spaces) equals the input string (ignoring spaces)
    3. Each string in the result starts with '(' and ends with ')'
-/
def separate_paren_groups_post (s : String) (result : List String) : Prop :=
  let noSpaces := String.mk (s.toList.filter (fun c => !isSpace c))
  let resultConcat := String.mk ((result.map String.toList).join)
  
  result.all isBalancedParens &&
  resultConcat == noSpaces &&
  result.all (fun group => 
    group.length > 0 && 
    group.get ⟨0, sorry⟩ == '(' && 
    group.get ⟨group.length - 1, sorry⟩ == ')')

theorem separate_paren_groups_correct (s : String) 
  (h : separate_paren_groups_pre s) : 
  separate_paren_groups_post s (separate_paren_groups s) := sorry

#eval separate_paren_groups "(()()) ((())) () ((())()())"
#eval separate_paren_groups "() (()) ((())) (((())))"
#eval separate_paren_groups "(()(())((())))"
#eval separate_paren_groups "( ) (( )) (( )( ))"

/-- Test cases for separate_paren_groups -/
def test_separate_paren_groups : IO Unit := do
  let test1 := separate_paren_groups "(()()) ((())) () ((())()())" == ["(()())", "((()))", "()", "((())()())"]
  let test2 := separate_paren_groups "() (()) ((())) (((())))" == ["()", "(())", "((()))", "(((())))"]
  let test3 := separate_paren_groups "(()(())((())))" == ["(()(())((())))" ]
  let test4 := separate_paren_groups "( ) (( )) (( )( ))" == ["()", "(())", "(()())"]
  
  IO.println s!"Test 1: {test1}"
  IO.println s!"Test 2: {test2}"
  IO.println s!"Test 3: {test3}"
  IO.println s!"Test 4: {test4}"
  
  if test1 && test2 && test3 && test4 then
    IO.println "All tests passed!"
  else
    IO.println "Some tests failed!"

#eval test_separate_paren_groups
