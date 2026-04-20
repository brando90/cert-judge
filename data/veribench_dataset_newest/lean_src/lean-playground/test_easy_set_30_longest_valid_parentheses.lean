import Mathlib

namespace ValidParentheses


def List.isValidParentheses (chars : List Char) : Bool :=
  let rec aux (count : Nat) (rest : List Char) : Bool :=
    match rest with
    | [] => count = 0
    | h::t =>
      match h with
      | '(' => aux (count + 1) t
      | ')' =>
        if count > 0 then
          aux (count - 1) t
        else
          false
      | _ => false
  aux 0 chars


def String.isValidParentheses (s : String) : Bool :=
  List.isValidParentheses s.toList


def getAllSubstrings (s : String) : List String :=
  let chars := s.toList
  let n := chars.length
  (List.range n).bind fun i =>
    (List.range (n - i + 1)).map fun len =>
      String.mk (chars.drop i |>.take len)


def longestValidParentheses (s : String) : Nat :=
  if s.isEmpty then 0
  else
    let n := s.length
    let chars := s.toList
    -- dp[i] represents length of longest valid parentheses ending at position i
    let dp := Array.mkArray n 0
    let rec fill (i : Nat) (dp : Array Nat) : Array Nat :=
      if i >= n then dp
      else
        let char := chars.get! i
        if char = ')' && i > 0 then
          let prevChar := chars.get! (i - 1)
          let newDp := 
            if prevChar = '(' then
              -- Case: ...()
              let prevLen := if i >= 2 then dp.get! (i - 2) else 0
              dp.set! i (2 + prevLen)
            else if dp.get! (i - 1) > 0 then
              -- Case: ...))
              let matchPos := i - dp.get! (i - 1) - 1
              if matchPos >= 0 && chars.get! matchPos = '(' then
                let beforeMatch := if matchPos > 0 then dp.get! (matchPos - 1) else 0
                dp.set! i (dp.get! (i - 1) + 2 + beforeMatch)
              else dp
            else dp
          fill (i + 1) newDp
        else
          fill (i + 1) dp
    let finalDp := fill 0 dp
    finalDp.foldl max 0


def longestValidParenthesesImp (s : String) : Nat :=
  if s.isEmpty then 0
  else
    let chars := s.toList
    let n := chars.length
    let stack : List Nat := [-1]  -- Stack to store indices
    
    let rec process (i : Nat) (stack : List Nat) (maxLen : Nat) : Nat :=
      if i >= n then maxLen
      else
        let char := chars.get! i
        if char = '(' then
          process (i + 1) (i :: stack) maxLen
        else
          -- char = ')'
          let newStack := stack.tail!
          if newStack.isEmpty then
            process (i + 1) [i] maxLen
          else
            let len := i - newStack.head!
            process (i + 1) newStack (max maxLen len)
    
    process 0 stack 0


def Pre (s : String) : Prop := True


def empty_string_prop : Prop := longestValidParentheses "" = 0

  
def single_char_prop (c : Char) : Prop := longestValidParentheses c.toString = 0


def even_length_prop (s : String) : Prop := longestValidParentheses s % 2 = 0


def upper_bound_prop (s : String) : Prop := longestValidParentheses s ≤ s.length


def non_negative_prop (s : String) : Prop := longestValidParentheses s ≥ 0


def Post_prop (s : String) : Prop :=
  (empty_string_prop) ∧
  (∀ c, single_char_prop c) ∧
  (even_length_prop s) ∧
  (upper_bound_prop s) ∧
  (non_negative_prop s)



/-!
# Tests
-/

/-- expected: 2 -/
example : longestValidParentheses "(()" = 2 := by native_decide
#eval! longestValidParentheses "(()" -- expected: 2

/-- expected: 4 -/
example : longestValidParentheses ")()())" = 4 := by native_decide
#eval! longestValidParentheses ")()())" -- expected: 4

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : longestValidParentheses "" = 0 := by
  unfold longestValidParentheses
  rfl
#eval! longestValidParentheses "" -- expected: 0

/-- expected: 2 -/
example : longestValidParentheses "()" = 2 := by native_decide
#eval! longestValidParentheses "()" -- expected: 2

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: balanced parentheses -/
example : longestValidParentheses "(())" = 4 := by native_decide
#eval! longestValidParentheses "(())" -- expected: 4

/-- positive: consecutive pairs -/
example : longestValidParentheses "()()" = 4 := by native_decide
#eval! longestValidParentheses "()()" -- expected: 4

/-- negative: single character -/
example : longestValidParentheses "(" = 0 := by native_decide
#eval! longestValidParentheses "(" -- expected: 0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: balanced parentheses -/
example : longestValidParenthesesImp "(())" = 4 := by native_decide
#eval! longestValidParenthesesImp "(())" -- expected: 4

/-- negative: unbalanced -/
example : longestValidParenthesesImp "(((" = 0 := by native_decide
#eval! longestValidParenthesesImp "(((" -- expected: 0

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem longestValidParentheses_equivalence_thm (s : String) :
  longestValidParentheses s = longestValidParenthesesImp s := sorry




end ValidParentheses