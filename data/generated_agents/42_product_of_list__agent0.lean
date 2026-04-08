import Std.Data.List.Basic

namespace ProductOfList

/--
  Return the product of all elements in a non-empty list.
-/
def product_of_list (xs : List Int) : Int :=
  match xs with
  | [] => panic! "Require non-empty List[Int]"
  | _ => xs.foldl (· * ·) 1

/-- Precondition: Input must be a non-empty list of integers -/
def pre (xs : List Int) : Prop :=
  xs ≠ []

/-- Postcondition: Result is the product of all elements in the list -/
def post (xs : List Int) (result : Int) : Prop :=
  result = xs.foldl (· * ·) 1

/-- Implementation satisfies specification -/
theorem product_of_list_correct (xs : List Int) (h : pre xs) : post xs (product_of_list xs) := by
  sorry

/-- Test cases for product_of_list -/
def test : IO Unit := do
  -- Basic case
  assert! (product_of_list [2, 3, 4] == 24)
  -- Single element case
  assert! (product_of_list [5] == 5)
  -- Multiple elements with same value
  assert! (product_of_list [1, 1, 1] == 1)
  -- Negative numbers
  assert! (product_of_list [2, -3, 4] == -24)
  -- Mixed positive and negative
  assert! (product_of_list [-2, -3] == 6)
  -- Try to trigger the panic (uncomment to test)
  -- let _ := product_of_list []
  IO.println "All tests passed!"

#eval test

end ProductOfList
