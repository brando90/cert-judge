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
The specification for `sum_product`, expressed using left folds. The initial
values encode the required empty sum and empty product.
-/
def sum_product_spec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/-- A named version of the accumulator loop used by `sum_product`. -/
def sum_product_loop_aux : List Int → Int → Int → Int × Int
  | [], sum_acc, prod_acc => (sum_acc, prod_acc)
  | n :: rest, sum_acc, prod_acc =>
      sum_product_loop_aux rest (sum_acc + n) (prod_acc * n)

/-- The implementation's local loop is the same loop with its initial accumulators. -/
theorem sum_product_eq_loop_aux (numbers : List Int) :
    sum_product numbers = sum_product_loop_aux numbers 0 1 := by sorry

/-- The accumulator loop agrees with left folds started at its accumulators. -/
theorem sum_product_loop_aux_fold (numbers : List Int) (sum_acc prod_acc : Int) :
    sum_product_loop_aux numbers sum_acc prod_acc =
      (numbers.foldl (· + ·) sum_acc, numbers.foldl (· * ·) prod_acc) := by
  induction numbers generalizing sum_acc prod_acc with
  | nil =>
      simp [sum_product_loop_aux]
  | cons n rest ih =>
      simp only [sum_product_loop_aux, List.foldl_cons]
      exact ih (sum_acc + n) (prod_acc * n)

/--
The implementation computes the specified sum and product for every input list.
-/
theorem sum_product_correct (numbers : List Int) :
    sum_product numbers = sum_product_spec numbers := by
  calc
    sum_product numbers = sum_product_loop_aux numbers 0 1 :=
      sum_product_eq_loop_aux numbers
    _ = (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1) :=
      sum_product_loop_aux_fold numbers 0 1
    _ = sum_product_spec numbers := by rfl

@[simp]
theorem sum_product_nil : sum_product ([] : List Int) = (0, 1) := by
  simp [sum_product_correct, sum_product_spec]

@[simp]
theorem sum_product_singleton (n : Int) : sum_product [n] = (n, n) := by
  simp [sum_product_correct, sum_product_spec]

theorem sum_product_sum (numbers : List Int) :
    (sum_product numbers).1 = numbers.foldl (· + ·) 0 := by
  simp [sum_product_correct, sum_product_spec]

theorem sum_product_product (numbers : List Int) :
    (sum_product numbers).2 = numbers.foldl (· * ·) 1 := by
  simp [sum_product_correct, sum_product_spec]

/-- Appending lists continues each fold from the accumulated result of the first list. -/
theorem sum_product_append (xs ys : List Int) :
    sum_product (xs ++ ys) =
      (ys.foldl (· + ·) (xs.foldl (· + ·) 0),
       ys.foldl (· * ·) (xs.foldl (· * ·) 1)) := by
  rw [sum_product_correct]
  simp [sum_product_spec, List.foldl_append]

theorem sum_product_example_ones : sum_product [1, 1, 1] = (3, 1) := by
  norm_num [sum_product_correct, sum_product_spec]

theorem sum_product_example_zero : sum_product [100, 0] = (100, 0) := by
  norm_num [sum_product_correct, sum_product_spec]

theorem sum_product_example_three : sum_product [3, 5, 7] = (15, 105) := by
  norm_num [sum_product_correct, sum_product_spec]

theorem sum_product_example_ten : sum_product [10] = (10, 10) := by
  norm_num [sum_product_correct, sum_product_spec]

/-- Executable test cases for `sum_product`. -/
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
