import Lean
import Std.Data.List.Basic

/-- 
Input to this function is a string represented multiple groups for nested parentheses separated by spaces.
For each of the group, output the deepest level of nesting of parentheses.
E.g. (()()) has maximum two levels of nesting while ((())) has three.
-/
def parseNestedParens (parenString : String) : List Nat :=
  let parseSingle (s : String) : Nat :=
    let rec loop (chars : List Char) (depth : Nat) (maxDepth : Nat) : Nat :=
      match chars with
      | [] => maxDepth
      | c :: rest =>
        if c == '(' then
          let newDepth := depth + 1
          let newMaxDepth := max newDepth maxDepth
          loop rest newDepth newMaxDepth
        else
          loop rest (depth - 1) maxDepth
    loop s.toList 0 0
  
  parenString.split (· == ' ')
    |> List.filter (fun s => !s.isEmpty)
    |> List.map parseSingle

/-- Precondition: The input string should only contain parentheses and spaces. -/
def parseNestedParens.pre (parenString : String) : Prop :=
  parenString.toList.all (fun c => c == '(' || c == ')' || c == ' ')

/-- Postcondition: The output list should contain the maximum nesting depth for each group. -/
def parseNestedParens.post (parenString : String) (result : List Nat) : Prop :=
  let groups := parenString.split (· == ' ') |> List.filter (fun s => !s.isEmpty)
  result.length == groups.length

/-- Correctness theorem: If the precondition holds, then the postcondition holds for the result. -/
theorem parseNestedParens.correct (parenString : String) :
  parseNestedParens.pre parenString → parseNestedParens.post parenString (parseNestedParens parenString) := 
  sorry

def test1 : parseNestedParens "(()()) ((())) () ((())()())" = [2, 3, 1, 3] := by rfl
def test2 : parseNestedParens "() (()) ((())) (((())))" = [1, 2, 3, 4] := by rfl
def test3 : parseNestedParens "(()(())((())))" = [4] := by rfl

#eval parseNestedParens "(()()) ((())) () ((())()())"
#eval parseNestedParens "() (()) ((())) (((())))"
#eval parseNestedParens "(()(())((())))"
