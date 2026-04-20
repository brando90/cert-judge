import Mathlib

namespace MyReverse


def myReverse : List Nat → List Nat
  | [] => []
  | x :: xs => myReverse xs ++ [x]


def myReverseImp (xs : List Nat) : List Nat := Id.run do
  let mut result : List Nat := []
  for x in xs do
    result := x :: result
  return result

/-!
# Property Theorems
-/



/-!
# Tests
-/

/-- expected: [4, 3, 2, 1] -/
example : myReverse [1, 2, 3, 4] = [4, 3, 2, 1] := by native_decide
#eval myReverse [1, 2, 3, 4] -- expected: [4, 3, 2, 1]

/-!
# Tests: Edge Cases
-/

/-- expected: [] -/
example : myReverse [] = [] := by native_decide
#eval myReverse [] -- expected: []

/-- expected: [5] -/
example : myReverse [5] = [5] := by native_decide
#eval myReverse [5] -- expected: [5]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: reverses pairs correctly -/
example : myReverse [1, 2] = [2, 1] := by native_decide
#eval myReverse [1, 2] -- expected: [2, 1]

/-- positive: handles longer lists -/
example : myReverse [1, 2, 3, 4, 5] = [5, 4, 3, 2, 1] := by native_decide
#eval myReverse [1, 2, 3, 4, 5] -- expected: [5, 4, 3, 2, 1]

/-- negative: reverse of non-empty should not be empty -/
example : ¬ (myReverse [1, 2] = []) := by native_decide
#eval (decide (myReverse [1, 2] = [])) -- expected: false

/-- negative: reverse should change order (for length > 1) -/
example : ¬ (myReverse [1, 2, 3] = [1, 2, 3]) := by native_decide
#eval (decide (myReverse [1, 2, 3] = [1, 2, 3])) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: maintains reverse computation -/
example : myReverseImp [1, 2] = [2, 1] := by native_decide
#eval myReverseImp [1, 2] -- expected: [2, 1]

/-- negative: reverse of non-empty should not be empty -/
example : ¬ (myReverseImp [1, 2] = []) := by native_decide
#eval (decide (myReverseImp [1, 2] = [])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem myReverseImp_aux (xs acc : List Nat) :
    Id.run (do
      let mut result : List Nat := acc
      for x in xs do
        result := x :: result
      return result) = myReverse xs ++ acc := by
  induction xs generalizing acc with
  | nil =>
      simp [myReverse]
  | cons x xs ih =>
      calc
        Id.run (do
          let mut result : List Nat := acc
          for x in x :: xs do
            result := x :: result
          return result) =
            Id.run (do
              let mut result : List Nat := x :: acc
              for x in xs do
                result := x :: result
              return result) := by
                simp
        _ = myReverse xs ++ (x :: acc) := ih (x :: acc)
        _ = myReverse (x :: xs) ++ acc := by
              simp [myReverse, List.append_assoc]

theorem myReverse_equivalence_thm (xs : List Nat) :
  myReverse xs = myReverseImp xs := by
  unfold myReverseImp
  simpa using (myReverseImp_aux xs []).symm




end MyReverse