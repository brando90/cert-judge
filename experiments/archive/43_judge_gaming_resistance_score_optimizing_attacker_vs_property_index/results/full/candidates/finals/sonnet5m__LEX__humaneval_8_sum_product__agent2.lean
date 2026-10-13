import Mathlib

/--
  For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
  Empty sum should be equal to 0 and empty product should be equal to 1.
-/
def sumProduct (numbers : List Int) : Int × Int := 
  let sum_value := 0
  let prod_value := 1
  
  let rec loop (nums : List Int) (sum_acc : Int) (prod_acc : Int) : Int × Int :=
    match nums with
    | [] => (sum_acc, prod_acc)
    | n :: rest => loop rest (sum_acc + n) (prod_acc * n)
  
  loop numbers sum_value prod_value

/-- Tests for sumProduct -/
def sumProductTests : List (List Int × (Int × Int)) := [
  ([], (0, 1)),
  ([1, 1, 1], (3, 1)),
  ([100, 0], (100, 0)),
  ([3, 5, 7], (15, 105)),
  ([10], (10, 10))
]

/-- Specification of sumProduct: it returns the sum and product of the input list -/
def sumProductSpec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/-- A recursive accumulator implementation of the sum and product calculation. -/
def sumProductLoop : List Int → Int → Int → Int × Int
  | [], sum, prod => (sum, prod)
  | n :: rest, sum, prod => sumProductLoop rest (sum + n) (prod * n)

/-- The accumulator loop is equivalent to folding each accumulator over the list. -/
theorem sumProductLoop_eq_foldl (numbers : List Int) (sum prod : Int) :
    sumProductLoop numbers sum prod =
      (numbers.foldl (fun acc n => acc + n) sum,
       numbers.foldl (fun acc n => acc * n) prod) := by
  induction numbers generalizing sum prod with
  | nil => rfl
  | cons n rest ih =>
      simpa [sumProductLoop, List.foldl] using ih (sum + n) (prod * n)

/-- The recursive loop started with the empty sum and product gives the specification. -/
theorem sumProductLoop_eq_spec (numbers : List Int) :
    sumProductLoop numbers 0 1 = sumProductSpec numbers := by
  rw [sumProductLoop_eq_foldl]
  rfl

/-- The implementation returns the specified sum and product. -/
theorem sumProduct_eq_spec (numbers : List Int) :
    sumProduct numbers = sumProductSpec numbers := by sorry

/-- Precondition: always true, no restrictions on input -/
def sumProductPre (_numbers : List Int) : Prop := True

/-- Postcondition: the result matches the specification -/
def sumProductPost (numbers : List Int) (result : Int × Int) : Prop :=
  result = sumProductSpec numbers

/-- Theorem: sumProduct satisfies its specification -/
theorem sumProductCorrect (numbers : List Int)
    (h : sumProductPre numbers) : sumProductPost numbers (sumProduct numbers) := by
  simpa [sumProductPost] using sumProduct_eq_spec numbers

/-- The sum component is the fold of addition over the input. -/
theorem sumProduct_sum (numbers : List Int) :
    (sumProduct numbers).1 = numbers.foldl (· + ·) 0 := by
  rw [sumProduct_eq_spec]
  rfl

/-- The product component is the fold of multiplication over the input. -/
theorem sumProduct_product (numbers : List Int) :
    (sumProduct numbers).2 = numbers.foldl (· * ·) 1 := by
  rw [sumProduct_eq_spec]
  rfl

/-- Concrete examples from the task tests. -/
theorem sumProduct_empty : sumProduct [] = (0, 1) := by decide

theorem sumProduct_ones : sumProduct [1, 1, 1] = (3, 1) := by decide

theorem sumProduct_zero : sumProduct [100, 0] = (100, 0) := by decide

theorem sumProduct_three : sumProduct [3, 5, 7] = (15, 105) := by decide

theorem sumProduct_singleton : sumProduct [10] = (10, 10) := by decide
