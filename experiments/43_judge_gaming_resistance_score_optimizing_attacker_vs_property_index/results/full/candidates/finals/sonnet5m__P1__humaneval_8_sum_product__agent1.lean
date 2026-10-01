import Mathlib
/-
This file implements a function that calculates the sum and product of a list of integers.
-/

import Mathlib.Tactic

/--
`sum_product` computes the sum and product of a list of integers.
Empty sum should be equal to 0 and empty product should be equal to 1.
-/
def sum_product (numbers : List Int) : Int × Int :=
  let sum_value := 0
  let prod_value := 1

  let rec loop (lst : List Int) (sum_acc : Int) (prod_acc : Int) : Int × Int :=
    match lst with
    | [] => (sum_acc, prod_acc)
    | n :: rest => loop rest (sum_acc + n) (prod_acc * n)

  loop numbers sum_value prod_value

/--
Specification for `sum_product`, expressed using left folds.
-/
def sum_product_spec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/-- A global version of the accumulator loop used to prove its fold characterization. -/
def sum_product_loop (lst : List Int) (sum_acc prod_acc : Int) : Int × Int :=
  match lst with
  | [] => (sum_acc, prod_acc)
  | n :: rest => sum_product_loop rest (sum_acc + n) (prod_acc * n)

/-- The accumulator loop is equivalent to folding from its current accumulators. -/
theorem sum_product_loop_eq_foldl (numbers : List Int) (sum_acc prod_acc : Int) :
    sum_product_loop numbers sum_acc prod_acc =
      (numbers.foldl (· + ·) sum_acc, numbers.foldl (· * ·) prod_acc) := by
  induction numbers generalizing sum_acc prod_acc with
  | nil => simp [sum_product_loop]
  | cons n rest ih => simp [sum_product_loop, ih]

/-- The implementation's local accumulator loop agrees with the global loop. -/
theorem sum_product_eq_loop (numbers : List Int) :
    sum_product numbers = sum_product_loop numbers 0 1 := by
  sorry

/-- The implementation satisfies its fold-based specification. -/
theorem sum_product_correct (numbers : List Int) :
    sum_product numbers = sum_product_spec numbers := by
  rw [sum_product_eq_loop, sum_product_loop_eq_foldl]
  rfl

theorem sum_product_fst (numbers : List Int) :
    (sum_product numbers).1 = numbers.foldl (· + ·) 0 := by
  rw [sum_product_correct]
  rfl

theorem sum_product_snd (numbers : List Int) :
    (sum_product numbers).2 = numbers.foldl (· * ·) 1 := by
  rw [sum_product_correct]
  rfl

/-- The result agrees with the usual list sum and product. -/
theorem sum_product_sum_prod (numbers : List Int) :
    sum_product numbers = (numbers.sum, numbers.prod) := by
  sorry

/-- Processing a list with a leading element adds and multiplies that element
with the results for the remaining list. -/
theorem sum_product_cons (n : Int) (numbers : List Int) :
    sum_product (n :: numbers) =
      (n + (sum_product numbers).1, n * (sum_product numbers).2) := by
  sorry

/-- The sum and product results combine across list concatenation. -/
theorem sum_product_append (left right : List Int) :
    sum_product (left ++ right) =
      ((sum_product left).1 + (sum_product right).1,
       (sum_product left).2 * (sum_product right).2) := by
  sorry

/-- Permuting the input does not change its sum or product. -/
theorem sum_product_perm {left right : List Int} (h : left.Perm right) :
    sum_product left = sum_product right := by
  sorry

/-- The empty list has sum zero and product one. -/
theorem sum_product_empty : sum_product [] = (0, 1) := by
  native_decide

/-- Concrete examples from the task's test function. -/
theorem sum_product_examples :
    sum_product [] = (0, 1) ∧
    sum_product [1, 1, 1] = (3, 1) ∧
    sum_product [100, 0] = (100, 0) ∧
    sum_product [3, 5, 7] = (15, 105) ∧
    sum_product [10] = (10, 10) := by
  native_decide

/-- Additional examples covering negative values and a zero product. -/
theorem sum_product_additional_examples :
    sum_product [-2, 4] = (2, -8) ∧
    sum_product [-2, 0, 4] = (2, 0) ∧
    sum_product [0] = (0, 0) := by
  native_decide

/-- Test cases for `sum_product`. -/
def test_sum_product : IO Unit := do
  assert! (sum_product [] = (0, 1))
  assert! (sum_product [1, 1, 1] = (3, 1))
  assert! (sum_product [100, 0] = (100, 0))
  assert! (sum_product [3, 5, 7] = (15, 105))
  assert! (sum_product [10] = (10, 10))
  IO.println "All tests passed!"

/-- Main function to run the tests. -/
def main : IO Unit :=
  test_sum_product
