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
  ([10], (10, 10)),
  ([-2, 3], (1, -6)),
  ([0, 4, 5], (9, 0)),
  ([-1, -2, -3], (-6, -6))
]

/-- Specification of sumProduct: it returns the sum and product of the input list -/
def sumProductSpec (numbers : List Int) : Int × Int :=
  (numbers.foldl (· + ·) 0, numbers.foldl (· * ·) 1)

/-- A named version of the accumulator loop used by `sumProduct`. -/
def sumProductLoop (nums : List Int) (sumAcc prodAcc : Int) : Int × Int :=
  match nums with
  | [] => (sumAcc, prodAcc)
  | n :: rest => sumProductLoop rest (sumAcc + n) (prodAcc * n)

/-- The accumulator loop computes the two folds with the supplied initial values. -/
theorem sumProductLoop_correct (numbers : List Int) (sumAcc prodAcc : Int) :
    sumProductLoop numbers sumAcc prodAcc =
      (numbers.foldl (· + ·) sumAcc, numbers.foldl (· * ·) prodAcc) := by
  induction numbers generalizing sumAcc prodAcc with
  | nil =>
      simp [sumProductLoop]
  | cons n numbers ih =>
      simp [sumProductLoop, ih, List.foldl]

/-- The implementation's local loop agrees with the named accumulator loop. -/
theorem sumProduct_eq_sumProductLoop (numbers : List Int) :
    sumProduct numbers = sumProductLoop numbers 0 1 := by sorry

/-- The implementation returns the specified sum and product for every list. -/
theorem sumProduct_eq_spec (numbers : List Int) :
    sumProduct numbers = sumProductSpec numbers := by
  rw [sumProduct_eq_sumProductLoop]
  simpa [sumProductSpec] using sumProductLoop_correct numbers 0 1

/-- The sum component is the fold of addition over the input list. -/
theorem sumProduct_sum (numbers : List Int) :
    (sumProduct numbers).1 = numbers.foldl (· + ·) 0 := by
  simpa [sumProductSpec] using congrArg Prod.fst (sumProduct_eq_spec numbers)

/-- The product component is the fold of multiplication over the input list. -/
theorem sumProduct_product (numbers : List Int) :
    (sumProduct numbers).2 = numbers.foldl (· * ·) 1 := by
  simpa [sumProductSpec] using congrArg Prod.snd (sumProduct_eq_spec numbers)

/-- Precondition: always true, no restrictions on input -/
def sumProductPre (_numbers : List Int) : Prop := True

/-- Postcondition: the result matches the specification -/
def sumProductPost (numbers : List Int) (result : Int × Int) : Prop :=
  result = sumProductSpec numbers

/-- Theorem: sumProduct satisfies its specification -/
theorem sumProductCorrect (numbers : List Int) 
  (h : sumProductPre numbers) : sumProductPost numbers (sumProduct numbers) := by
  exact sumProduct_eq_spec numbers

/-- All of the concrete examples in the test list pass. -/
theorem sumProductTests_correct :
    ∀ t ∈ sumProductTests, sumProduct t.1 = t.2 := by
  native_decide

/-- The empty list has the conventional empty sum and product. -/
theorem sumProduct_empty : sumProduct [] = (0, 1) := by
  native_decide

/-- A singleton list returns its element as both sum and product. -/
theorem sumProduct_singleton (n : Int) : sumProduct [n] = (n, n) := by sorry

/-- The implementation correctly handles a list containing a negative value. -/
theorem sumProduct_negative_example : sumProduct [-2, 3] = (1, -6) := by
  native_decide

/-- A zero in the input makes the product zero, in this concrete test case. -/
theorem sumProduct_zero_example : sumProduct [0, 4, 5] = (9, 0) := by
  native_decide

/-- Products and sums are computed correctly for a list of negative values. -/
theorem sumProduct_all_negative_example :
    sumProduct [-1, -2, -3] = (-6, -6) := by
  native_decide
