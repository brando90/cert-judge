import Mathlib

open List
namespace MyProductList


def myProductList : List Nat → Nat
  | []      => 1
  | x :: xs => x * myProductList xs


def myProductListImp (xs : List Nat) : Nat := Id.run do
  let mut acc := 1
  for x in xs do
    acc := acc * x
  return acc



/-!
# Tests
-/

/-- expected: 24 -/
example : myProductList [2, 3, 4] = 24 := by native_decide
#eval myProductList [2, 3, 4] -- expected: 24

/-- expected: 5 -/
example : myProductList [5] = 5 := by native_decide
#eval myProductList [5] -- expected: 5

/-!
# Tests: Edge Cases
-/

/-- expected: 1 -/
example : myProductList [1, 1, 1] = 1 := by native_decide
#eval myProductList [1, 1, 1] -- expected: 1

/-- expected: 0 -/
example : myProductList [10, 0, 5] = 0 := by native_decide
#eval myProductList [10, 0, 5] -- expected: 0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: empty list -/
example : myProductList [] = 1 := by native_decide
#eval myProductList [] -- expected: 1

/-- positive: single element -/
example : myProductList [7] = 7 := by native_decide
#eval myProductList [7] -- expected: 7

/-- negative: product with zero is always zero -/
example : ¬ (myProductList [1, 0, 2] ≠ 0) := by native_decide
#eval (decide (myProductList [1, 0, 2] ≠ 0)) -- expected: false

/-- negative: empty list is not zero -/
example : ¬ (myProductList [] = 0) := by native_decide
#eval (decide (myProductList [] = 0)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: empty list -/
example : myProductListImp [] = 1 := by native_decide
#eval myProductListImp [] -- expected: 1

/-- negative: zero element makes product zero -/
example : ¬ (myProductListImp [10, 0, 5] ≠ 0) := by native_decide
#eval (decide (myProductListImp [10, 0, 5] ≠ 0)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem product_loop_aux (xs : List Nat) (acc : Nat) :
    Id.run (do
      let mut acc := acc
      for x in xs do
        acc := acc * x
      return acc) = acc * myProductList xs := by
  induction xs generalizing acc with
  | nil =>
      simp [myProductList]
  | cons x xs ih =>
      calc
        Id.run (do
          let mut acc := acc
          for x in x :: xs do
            acc := acc * x
          return acc) =
            Id.run (do
              let mut acc := acc * x
              for x in xs do
                acc := acc * x
              return acc) := by
              simp
        _ = acc * x * myProductList xs := by
              simpa [Nat.mul_assoc] using ih (acc * x)
        _ = acc * myProductList (x :: xs) := by
              simp [myProductList, Nat.mul_assoc]

theorem myProductList_equivalence_thm (xs : List Nat) :
  myProductList xs = myProductListImp xs := by
  unfold myProductListImp
  simpa [Nat.one_mul] using (product_loop_aux xs 1).symm




end MyProductList