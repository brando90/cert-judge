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

/-- Precondition: always true, no restrictions on input -/
def sumProductPre (_numbers : List Int) : Prop := True

/-- Postcondition: the result matches the specification -/
def sumProductPost (numbers : List Int) (result : Int × Int) : Prop :=
  result = sumProductSpec numbers

/-- Theorem: sumProduct satisfies its specification -/
theorem sumProductCorrect (numbers : List Int) 
  (h : sumProductPre numbers) : sumProductPost numbers (sumProduct numbers) := by sorry

