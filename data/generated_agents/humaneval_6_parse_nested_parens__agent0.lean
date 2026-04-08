```lean
import Lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic.Ring
import Std.Data.List.Basic

/--
  Computes the deepest level of nesting of parentheses in a string.
  For example, (()()) has maximum two levels of nesting while ((())) has three.
-/
def parseNestedParens (parenString : String) : List Nat :=
  let groups := parenString.split (· == ' ') |>.filter (fun s => !s.isEmpty)
  groups.map (fun group =>
    let chars := group.data
    let rec parseParenGroup (chars : List Char) (depth : Nat) (maxDepth : Nat) : Nat :=
      match chars with
      | [] => maxDepth
      | c::cs =>
        if c == '(' then
          let newDepth := depth + 1
          parseParenGroup cs newDepth (max newDepth maxDepth)
        else
          parseParenGroup cs (depth - 1) maxDepth
    parseParenGroup chars 0 0)

/--
  Specification for parseNestedParens.
  For each group of nested parentheses, returns the deepest level of nesting.
-/
def parseNestedParensSpec (parenString : String) : List Nat :=
  let groups := parenString.split (· == ' ') |>.filter (fun s => !s.isEmpty)
  groups.map (fun group =>
    let chars := group.data
    let rec parseParenGroup (chars : List Char) (depth : Nat) (maxDepth : Nat) : Nat :=
      match chars with
      | [] => maxDepth
      | c::cs =>
        if c == '(' then
          let newDepth := depth + 1
          parseParenGroup cs newDepth (max newDepth maxDepth)
        else
          parseParenGroup cs (depth - 1) maxDepth
    parseParenGroup chars 0 0)

/--
  Predicate to check if a string is a valid sequence of parentheses.
  A valid sequence has balanced parentheses and doesn't have negative depth.
-/
def isValidParenString (s : String) : Bool :=
  let chars := s.data
  let rec check (chars : List Char) (depth : Nat) : Bool :=
    match chars with
    | [] => depth == 0
    | c::cs =>
      if c == '(' then
        check cs (depth + 1)
      else if c == ')' then
        if depth == 0 then false
        else check cs (depth - 1)
      else
        check cs depth
  check chars 0

/--
  Predicate to check if a string consists of valid parentheses groups separated by spaces.
-/
def isValidParenGroups (s : String) : Bool :=
  let groups := s.split (· == ' ') |>.filter (fun s => !s.isEmpty)
  groups.all isValidParenString

theorem parseNestedParens_correct (s : String) (h : isValidParenGroups s) :
  parseNestedParens s = parseNestedParensSpec s := by
  sorry

#eval parseNestedParens "(()()) ((())) () ((())()())"  -- [2, 3, 1, 3]
#eval parseNestedParens "() (()) ((())) (((())))"      -- [1, 2, 3, 4]
#eval parseNestedParens "(()(())((())))"               -- [4]

-- Tests
def test_parseNestedParens : IO Unit := do
  assert! (parseNestedParens "(()()) ((())) () ((())()())" == [2, 3, 1, 3])
  assert! (parseNestedParens "() (()) ((())) (((())))" == [1, 2, 3, 4])
  assert! (parseNestedParens "(()(())((())))" == [4])
  IO.println "All tests passed!"

#eval test_parseNestedParens
```
