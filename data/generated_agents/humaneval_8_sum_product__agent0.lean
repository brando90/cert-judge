import Std.Data.List.Basic

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

/--
Precondition: None
Postcondition: Returns a tuple (sum, product) where sum is the sum of all elements
and product is the product of all elements. For empty lists, sum = 0 and product = 1.
-/
theorem sumProductCorrect (numbers : List Int) : 
  sumProduct numbers = (sum numbers, product numbers) := by
  sorry

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
