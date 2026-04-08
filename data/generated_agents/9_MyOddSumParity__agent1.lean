import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/--
Returns the parity (0 or 1) of the sum of all elements in a list of odd integers.
-/
def oddSumParity (xs : List Int) : Int :=
  match xs with
  | [] => panic! "Require non-empty list of odd integers (got empty list)"
  | _ => (xs.sum % 2)

/--
Predicate that checks if a list is a non-empty list of odd integers.
-/
def isNonEmptyListOfOdd (xs : List Int) : Prop :=
  xs ≠ [] ∧ ∀ x ∈ xs, x % 2 = 1

/--
Precondition: The input must be a non-empty list of odd integers.
-/
def oddSumParity_pre (xs : List Int) : Prop :=
  isNonEmptyListOfOdd xs

/--
Postcondition: The result is either 0 or 1, representing the parity of the sum.
-/
def oddSumParity_post (xs : List Int) (result : Int) : Prop :=
  result = 0 ∨ result = 1

theorem odd_sum_parity_theorem (xs : List Int) (h : oddSumParity_pre xs) :
  oddSumParity_post xs (oddSumParity xs) := by
  sorry

/-- Unit tests for oddSumParity function -/
def oddSumParity_test : IO Unit := do
  -- Basic test
  assert! (oddSumParity [1, 3, 5] = 1)
  
  -- Edge case: single odd number
  assert! (oddSumParity [1] = 1)
  
  -- Even count of odd numbers
  assert! (oddSumParity [1, 3] = 0)
  
  -- More tests
  assert! (oddSumParity [5, 7, 9, 11] = 0)
  assert! (oddSumParity [3, 5, 7] = 1)
  
  IO.println "All oddSumParity tests passed!"

/-- Main function to run tests -/
def main : IO Unit :=
  oddSumParity_test
