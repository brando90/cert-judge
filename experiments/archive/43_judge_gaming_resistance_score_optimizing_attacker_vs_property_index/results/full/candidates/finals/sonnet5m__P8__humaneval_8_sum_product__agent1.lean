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
Specification for sum_product:
- The first element of the result is the sum of all elements in the input list.
- The second element of the result is the product of all elements in the input list.
- For an empty list, the sum is 0 and the product is 1.
-/
def sum_product_spec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/-- The implementation satisfies the fold-based specification. -/
theorem sum_product_correct (numbers : List Int) :
    sum_product numbers = sum_product_spec numbers := by
  sorry

/-- The first component is the fold-based sum. -/
theorem sum_product_fst (numbers : List Int) :
    (sum_product numbers).1 = numbers.foldl (· + ·) 0 := by sorry

/-- The second component is the fold-based product. -/
theorem sum_product_snd (numbers : List Int) :
    (sum_product numbers).2 = numbers.foldl (· * ·) 1 := by sorry

/-- The empty-list behavior specified by the task. -/
theorem sum_product_empty : sum_product [] = (0, 1) := by sorry

/-- The result on a singleton list. -/
theorem sum_product_singleton (n : Int) : sum_product [n] = (n, n) := by sorry

/-- A two-element input sums and multiplies its two entries. -/
theorem sum_product_pair (a b : Int) :
    sum_product [a, b] = (a + b, a * b) := by sorry

/-- The concrete examples from the task. -/
theorem sum_product_examples :
    sum_product [1, 1, 1] = (3, 1) ∧
    sum_product [100, 0] = (100, 0) ∧
    sum_product [3, 5, 7] = (15, 105) ∧
    sum_product [10] = (10, 10) := by sorry

/--
Test cases for sum_product
-/
def test_sum_product : IO Unit := do
  assert! (sum_product [] = (0, 1))
  assert! (sum_product [1, 1, 1] = (3, 1))
  assert! (sum_product [100, 0] = (100, 0))
  assert! (sum_product [3, 5, 7] = (15, 105))
  assert! (sum_product [10] = (10, 10))
  IO.println "All tests passed!"

/--
Main function to run the tests
-/
def main : IO Unit :=
  test_sum_product
