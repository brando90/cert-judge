import Mathlib.Tactic

namespace VeriBench

/--
  Returns the parity (0 or 1) of the sum of all elements in a list of even integers.
  
  Precondition: All elements in the list are even integers.
  Postcondition: Returns 0 (as the sum of even numbers is always even).
-/
def evenSumParity (xs : List Int) : Int :=
  if xs.all (fun x => x % 2 = 0) then
    xs.sum % 2
  else
    panic! "Require list of even integers"

/-- Predicate that checks if all elements in the list are even integers. -/
def evenSumParity_pre (xs : List Int) : Prop :=
  xs.all (fun x => x % 2 = 0)

/-- Postcondition specifying that the result is the parity of the sum of the list. -/
def evenSumParity_post (xs : List Int) (result : Int) : Prop :=
  result = xs.sum % 2

theorem even_sum_of_all_even (xs : List Int) (h : xs.all (fun x => x % 2 = 0)) :
  xs.sum % 2 = 0 := by
  sorry

/-- Correctness theorem: evenSumParity satisfies its specification. -/
theorem evenSumParity_correct (xs : List Int) (h : evenSumParity_pre xs) :
  evenSumParity_post xs (evenSumParity xs) := by
  unfold evenSumParity evenSumParity_post
  simp [h]
  rfl

/-- Test cases for evenSumParity -/
def evenSumParity_test : IO Unit := do
  -- Basic test case
  let test1 := evenSumParity [2, 4, 6]
  IO.println s!"Test 1: {test1}"
  assert! test1 = 0

  -- Empty list test case
  let test2 := evenSumParity []
  IO.println s!"Test 2: {test2}"
  assert! test2 = 0

  -- The function will panic on invalid inputs, so we don't test those directly
  
  IO.println "All tests passed!"

end VeriBench
