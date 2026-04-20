import Mathlib

namespace RollingMax


def rollingMax (numbers : List Int) : List Int :=
  match numbers with
  | [] => []
  | x :: xs =>
    let rec aux (remaining : List Int) (currentMax : Int) (acc : List Int) : List Int :=
      match remaining with
      | [] => acc.reverse
      | y :: ys =>
        let newMax := max currentMax y
        aux ys newMax (newMax :: acc)
    aux xs x [x]


def rollingMaxImp (numbers : List Int) : List Int :=
  let rec go (lst : List Int) (maxSoFar : Option Int) (result : List Int) : List Int :=
    match lst with
    | [] => result.reverse
    | x :: xs =>
      match maxSoFar with
      | none => go xs (some x) [x]
      | some m =>
        let newMax := max m x
        go xs (some newMax) (newMax :: result)
  match numbers with
  | [] => []
  | _ => go numbers none []

-- Helper lemmas for proofs

/-!
# Tests
-/

/-- expected: [] -/
example : rollingMax [] = [] := by native_decide
#eval rollingMax []

/-- expected: [1] -/
example : rollingMax [1] = [1] := by native_decide
#eval rollingMax [1]

/-!
# Tests: Edge Cases
-/

/-- expected: [1, 2, 3, 4] -/
example : rollingMax [1, 2, 3, 4] = [1, 2, 3, 4] := by native_decide
#eval rollingMax [1, 2, 3, 4]

/-- expected: [4, 4, 4, 4] -/
example : rollingMax [4, 3, 2, 1] = [4, 4, 4, 4] := by native_decide
#eval rollingMax [4, 3, 2, 1]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: mixed sequence -/
example : rollingMax [3, 2, 3, 100, 3] = [3, 3, 3, 100, 100] := by native_decide
#eval rollingMax [3, 2, 3, 100, 3] -- expected: [3, 3, 3, 100, 100]

/-- positive: negative numbers -/
example : rollingMax [-1, -2, -3, -4] = [-1, -1, -1, -1] := by native_decide
#eval rollingMax [-1, -2, -3, -4] -- expected: [-1, -1, -1, -1]

/-- negative: length doesn't decrease -/
example : ¬ ((rollingMax [1, 2, 3]).length < [1, 2, 3].length) := by native_decide
#eval (decide ((rollingMax [1, 2, 3]).length < [1, 2, 3].length)) -- expected: false

/-- negative: rolling max doesn't decrease -/
example : ¬ (rollingMax [1, 5, 3] = [1, 5, 1]) := by native_decide
#eval (decide (rollingMax [1, 5, 3] = [1, 5, 1])) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: constant values -/
example : rollingMaxImp [0, 0, 0, 0] = [0, 0, 0, 0] := by native_decide
#eval rollingMaxImp [0, 0, 0, 0] -- expected: [0, 0, 0, 0]

/-- negative: doesn't decrease -/
example : ¬ (rollingMaxImp [5, 1, 3] = [5, 1, 3]) := by native_decide
#eval (decide (rollingMaxImp [5, 1, 3] = [5, 1, 3])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem rollingMax_equivalence_thm (numbers : List Int) :
  rollingMax numbers = rollingMaxImp numbers := sorry




end RollingMax