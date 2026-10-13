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

/-- The same accumulator-based computation, exposed for proving the specification. -/
def sum_product_loop (lst : List Int) (sum_acc prod_acc : Int) : Int × Int :=
  match lst with
  | [] => (sum_acc, prod_acc)
  | n :: rest => sum_product_loop rest (sum_acc + n) (prod_acc * n)

/-- The local loop in `sum_product` agrees with the exposed accumulator loop. -/
theorem sum_product_eq_loop (numbers : List Int) :
    sum_product numbers = sum_product_loop numbers 0 1 := by sorry

/--
The accumulator-based computation agrees with the two corresponding folds.
-/
theorem sum_product_loop_fold (numbers : List Int) (sum_acc prod_acc : Int) :
    sum_product_loop numbers sum_acc prod_acc =
      (numbers.foldl (fun acc n => acc + n) sum_acc,
       numbers.foldl (fun acc n => acc * n) prod_acc) := by
  induction numbers generalizing sum_acc prod_acc with
  | nil =>
      rfl
  | cons n rest ih =>
      simp only [sum_product_loop, List.foldl]
      exact ih (sum_acc + n) (prod_acc * n)

/--
Specification for sum_product: 
- The first element of the result is the sum of all elements in the input list.
- The second element is the product of all elements in the input list.
- For an empty list, the sum is 0 and the product is 1.
-/
def sum_product_spec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/--
Theorem stating that the implementation satisfies the specification.
-/
theorem sum_product_correct (numbers : List Int) : 
  sum_product numbers = sum_product_spec numbers := by
  unfold sum_product_spec
  calc
    sum_product numbers = sum_product_loop numbers 0 1 :=
      sum_product_eq_loop numbers
    _ = (numbers.foldl (fun acc n => acc + n) 0,
         numbers.foldl (fun acc n => acc * n) 1) :=
      sum_product_loop_fold numbers 0 1

/-- The sum component is the sum fold over the input list. -/
theorem sum_product_fst (numbers : List Int) :
    (sum_product numbers).1 = numbers.foldl (· + ·) 0 := by
  rw [sum_product_correct]
  rfl

/-- The product component is the product fold over the input list. -/
theorem sum_product_snd (numbers : List Int) :
    (sum_product numbers).2 = numbers.foldl (· * ·) 1 := by
  rw [sum_product_correct]
  rfl

/-- The empty list has sum zero and product one. -/
theorem sum_product_empty : sum_product [] = (0, 1) := by
  simp [sum_product_correct, sum_product_spec]

/-- The result on a singleton list is that integer in both components. -/
theorem sum_product_singleton (n : Int) :
    sum_product [n] = (n, n) := by
  simp [sum_product_correct, sum_product_spec, List.foldl]

/-- A cons cell initializes each fold with the head element. -/
theorem sum_product_cons (n : Int) (numbers : List Int) :
    sum_product (n :: numbers) =
      (numbers.foldl (fun acc x => acc + x) n,
       numbers.foldl (fun acc x => acc * x) n) := by
  simp [sum_product_correct, sum_product_spec, List.foldl]

/-- The result agrees with the standard list sum and product. -/
theorem sum_product_eq_sum_prod (numbers : List Int) :
    sum_product numbers = (numbers.sum, numbers.prod) := by
  sorry

/-- Sums and products of concatenated lists combine componentwise. -/
theorem sum_product_append (xs ys : List Int) :
    sum_product (xs ++ ys) =
      ((sum_product xs).1 + (sum_product ys).1,
       (sum_product xs).2 * (sum_product ys).2) := by
  sorry

/-- Reversing a list does not change its sum or product. -/
theorem sum_product_reverse (numbers : List Int) :
    sum_product numbers = sum_product numbers.reverse := by
  sorry

/-- Permuting a list does not change its sum or product. -/
theorem sum_product_perm (xs ys : List Int) (h : xs.Perm ys) :
    sum_product xs = sum_product ys := by
  sorry

/-- A list containing zero has product zero. -/
theorem sum_product_product_eq_zero_of_mem (numbers : List Int)
    (h : 0 ∈ numbers) :
    (sum_product numbers).2 = 0 := by
  sorry

/-- The product is zero exactly when the list contains zero. -/
theorem sum_product_product_eq_zero_iff (numbers : List Int) :
    (sum_product numbers).2 = 0 ↔ 0 ∈ numbers := by
  sorry

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
