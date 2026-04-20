import Mathlib

open List -- brings the `~` permutation notation into scope
namespace HasCloseElements


def hasCloseElements (numbers : List Float) (threshold : Float) : Bool :=
  match numbers with
  | []      => false
  | x :: xs =>
    if xs.any (fun y => Float.abs (x - y) < threshold) then
      true
    else
      hasCloseElements xs threshold


def hasCloseElementsImp (numbers : List Float) (threshold : Float) : Bool :=
  let rec checkPairs (i : Nat) (j : Nat) : Bool :=
    if i >= numbers.length then false
    else if j >= numbers.length then checkPairs (i + 1) (i + 2)
    else
      match numbers.get? i, numbers.get? j with
      | some x, some y => 
        if Float.abs (x - y) < threshold then true
        else checkPairs i (j + 1)
      | _, _ => false
  checkPairs 0 1



/-!
# Tests
-/

/-- expected: true -/
example : hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.3 = true := by native_decide
#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.3 -- expected: true

/-- expected: false -/
example : hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.05 = false := by native_decide
#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.05 -- expected: false

/-!
# Tests: Edge Cases
-/

/-- expected: false -/
example : hasCloseElements [] 0.1 = false := by native_decide
#eval hasCloseElements [] 0.1 -- expected: false

/-- expected: false -/
example : hasCloseElements [42.0] 0.01 = false := by native_decide
#eval hasCloseElements [42.0] 0.01 -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: close elements exist -/
example : hasCloseElements [1.0, 1.1] 0.2 = true := by native_decide
#eval hasCloseElements [1.0, 1.1] 0.2 -- expected: true

/-- positive: duplicate elements -/
example : hasCloseElements [2.0, 2.0] 0.1 = true := by native_decide
#eval hasCloseElements [2.0, 2.0] 0.1 -- expected: true

/-- negative: all elements far apart -/
example : ¬ (hasCloseElements [1.0, 3.0, 5.0] 1.0 = true) := by native_decide
#eval (decide (hasCloseElements [1.0, 3.0, 5.0] 1.0 = true)) -- expected: false

/-- negative: non-positive threshold -/
example : ¬ (hasCloseElements [1.0, 1.1] 0.0 = true) := by native_decide
#eval (decide (hasCloseElements [1.0, 1.1] 0.0 = true)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: close elements detected -/
example : hasCloseElementsImp [1.0, 1.05] 0.1 = true := by native_decide
#eval hasCloseElementsImp [1.0, 1.05] 0.1 -- expected: true

/-- negative: elements too far apart -/
example : ¬ (hasCloseElementsImp [1.0, 3.0, 5.0] 0.5 = true) := by native_decide
#eval (decide (hasCloseElementsImp [1.0, 3.0, 5.0] 0.5 = true)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem hasCloseElements_equivalence_thm (numbers : List Float) (threshold : Float) :
  hasCloseElements numbers threshold = hasCloseElementsImp numbers threshold := sorry




end HasCloseElements