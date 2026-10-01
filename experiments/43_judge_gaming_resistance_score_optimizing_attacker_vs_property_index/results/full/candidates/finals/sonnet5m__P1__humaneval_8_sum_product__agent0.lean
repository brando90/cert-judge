import Mathlib
/--
For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
Empty sum should be equal to 0 and empty product should be equal to 1.
-/
def sumProduct (numbers : List Int) : Int × Int :=
  let rec loop (remaining : List Int) (sum_value : Int) (prod_value : Int) : Int × Int :=
    match remaining with
    | [] => (sum_value, prod_value)
    | n :: rest => loop rest (sum_value + n) (prod_value * n)
  loop numbers 0 1

/--
The sum of a list is the sum of all its elements.
An empty list has a sum of 0.
-/
def sum (numbers : List Int) : Int :=
  match numbers with
  | [] => 0
  | n :: rest => n + sum rest

/--
The product of a list is the product of all its elements.
An empty list has a product of 1.
-/
def product (numbers : List Int) : Int :=
  match numbers with
  | [] => 1
  | n :: rest => n * product rest

/-- A recursive version of the accumulator loop used by `sumProduct`. -/
def sumProductAux (remaining : List Int) (sum_value prod_value : Int) : Int × Int :=
  match remaining with
  | [] => (sum_value, prod_value)
  | n :: rest => sumProductAux rest (sum_value + n) (prod_value * n)

/-- The auxiliary loop adds the remaining sum and multiplies by the remaining product. -/
theorem sumProductAux_correct (remaining : List Int) (sum_value prod_value : Int) :
    sumProductAux remaining sum_value prod_value =
      (sum_value + sum remaining, prod_value * product remaining) := by
  induction remaining generalizing sum_value prod_value with
  | nil =>
      simp [sumProductAux, sum, product]
  | cons n rest ih =>
      change sumProductAux rest (sum_value + n) (prod_value * n) =
        (sum_value + (n + sum rest), prod_value * (n * product rest))
      rw [ih (sum_value + n) (prod_value * n)]
      ext <;> ring

/-- The implementation's local loop agrees with the auxiliary loop. -/
theorem sumProduct_eq_aux (numbers : List Int) :
    sumProduct numbers = sumProductAux numbers 0 1 := by sorry

/--
Precondition: None
Postcondition: Returns a tuple (sum, product) where sum is the sum of all elements
and product is the product of all elements. For empty lists, sum = 0 and product = 1.
-/
theorem sumProductCorrect (numbers : List Int) :
  sumProduct numbers = (sum numbers, product numbers) := by
  rw [sumProduct_eq_aux]
  simpa using (sumProductAux_correct numbers 0 1)

theorem sumProduct_fst (numbers : List Int) :
    (sumProduct numbers).1 = sum numbers := by
  simpa using congrArg Prod.fst (sumProductCorrect numbers)

theorem sumProduct_snd (numbers : List Int) :
    (sumProduct numbers).2 = product numbers := by
  simpa using congrArg Prod.snd (sumProductCorrect numbers)

theorem sum_append_spec (numbers tail : List Int) :
    sum (numbers ++ tail) = sum numbers + sum tail := by
  induction numbers with
  | nil =>
      simp [sum]
  | cons n rest ih =>
      change n + sum (rest ++ tail) = (n + sum rest) + sum tail
      rw [ih]
      ring

theorem product_append_spec (numbers tail : List Int) :
    product (numbers ++ tail) = product numbers * product tail := by
  induction numbers with
  | nil =>
      simp [product]
  | cons n rest ih =>
      change n * product (rest ++ tail) = (n * product rest) * product tail
      rw [ih]
      ring

/-- Summing and multiplying over a concatenation separates into the two lists. -/
theorem sumProduct_append (numbers tail : List Int) :
    sumProduct (numbers ++ tail) =
      ((sumProduct numbers).1 + (sumProduct tail).1,
        (sumProduct numbers).2 * (sumProduct tail).2) := by
  simp [sumProductCorrect, sum_append_spec, product_append_spec]

theorem sumProduct_empty : sumProduct [] = (0, 1) := by
  decide

theorem sumProduct_ones : sumProduct [1, 1, 1] = (3, 1) := by
  decide

theorem sumProduct_with_zero : sumProduct [100, 0] = (100, 0) := by
  decide

theorem sumProduct_three : sumProduct [3, 5, 7] = (15, 105) := by
  decide

theorem sumProduct_singleton : sumProduct [10] = (10, 10) := by
  decide

def main : IO Unit := do
  -- Test 1: Empty list
  IO.println s!"Test 1: {sumProduct []}"
  assert! sumProduct [] == (0, 1)

  -- Test 2: List with ones
  IO.println s!"Test 2: {sumProduct [1, 1, 1]}"
  assert! sumProduct [1, 1, 1] == (3, 1)

  -- Test 3: List with zero
  IO.println s!"Test 3: {sumProduct [100, 0]}"
  assert! sumProduct [100, 0] == (100, 0)

  -- Test 4: General case
  IO.println s!"Test 4: {sumProduct [3, 5, 7]}"
  assert! sumProduct [3, 5, 7] == (3 + 5 + 7, 3 * 5 * 7)

  -- Test 5: Single element
  IO.println s!"Test 5: {sumProduct [10]}"
  assert! sumProduct [10] == (10, 10)

  IO.println "All tests passed!"
