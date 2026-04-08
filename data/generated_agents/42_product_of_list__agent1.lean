import Mathlib.Tactic
import Mathlib.Data.List.Basic

namespace ProductOfList

/--
  Product of all elements in a non-empty list of integers.
  
  Edge cases:
  - Single-element list returns that element.
  - Empty list is invalid.
-/
def productOfList (xs : List Int) : Int :=
  match xs with
  | [] => panic! "Require non-empty List[Int]"
  | _ => xs.foldl (· * ·) 1

/-- Precondition: the list must be non-empty. -/
def pre (xs : List Int) : Prop := xs ≠ []

/-- Postcondition: the result is the product of all elements in the list. -/
def post (xs : List Int) (result : Int) : Prop :=
  result = xs.foldl (· * ·) 1

/-- Test cases for `productOfList` -/
def tests : List (List Int × Int) := [
  ([2, 3, 4], 24),
  ([5], 5),
  ([1, 1, 1], 1)
]

/-- Run all test cases -/
def runTests : Bool :=
  tests.all (fun (input, expected) => productOfList input = expected)

#eval runTests -- Should return true

/-- Correctness theorem: if precondition holds, then postcondition holds for the result. -/
theorem productOfList_correct (xs : List Int) (h : pre xs) : post xs (productOfList xs) := by
  unfold pre at h
  unfold post
  unfold productOfList
  cases xs with
  | nil => contradiction
  | cons head tail => rfl
  sorry

end ProductOfList
