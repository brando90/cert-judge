```lean
def parseNestedParens (parenString : String) : List Nat :=
  let parseParenGroup (s : String) : Nat :=
    let rec loop (chars : List Char) (depth : Nat) (maxDepth : Nat) : Nat :=
      match chars with
      | [] => maxDepth
      | c :: cs =>
        if c == '(' then
          let newDepth := depth + 1
          loop cs newDepth (max newDepth maxDepth)
        else
          loop cs (depth - 1) maxDepth
    loop s.toList 0 0
  
  let groups := parenString.split (· == ' ')
  let nonEmptyGroups := groups.filter (fun g => g != "")
  nonEmptyGroups.map parseParenGroup

/-- 
Input to this function is a string represented multiple groups for nested parentheses separated by spaces.
For each of the group, output the deepest level of nesting of parentheses.
E.g. (()()) has maximum two levels of nesting while ((())) has three.
-/
theorem parseNestedParens_spec 
  (parenString : String) 
  (groups : List String := parenString.split (· == ' '))
  (nonEmptyGroups := groups.filter (fun g => g != "")) :
  parseNestedParens parenString = 
    nonEmptyGroups.map (fun group => 
      let rec findMaxDepth (chars : List Char) (depth : Nat) (maxDepth : Nat) : Nat :=
        match chars with
        | [] => maxDepth
        | c :: cs =>
          if c == '(' then
            let newDepth := depth + 1
            findMaxDepth cs newDepth (max newDepth maxDepth)
          else
            findMaxDepth cs (depth - 1) maxDepth
      findMaxDepth group.toList 0 0) :=
  sorry

#eval parseNestedParens "(()()) ((())) () ((())()())" -- [2, 3, 1, 3]
#eval parseNestedParens "() (()) ((())) (((())))" -- [1, 2, 3, 4]
#eval parseNestedParens "(()(())((())))" -- [4]

example : parseNestedParens "(()()) ((())) () ((())()())" = [2, 3, 1, 3] := rfl
example : parseNestedParens "() (()) ((())) (((())))" = [1, 2, 3, 4] := rfl
example : parseNestedParens "(()(())((())))" = [4] := rfl
```
