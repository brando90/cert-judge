import VeriBench

namespace EvenNumbers

/-- Returns a new list containing only the even numbers from the input list. -/
def evenNumbers (xs : List Int) : List Int :=
  xs.filter (fun x => x % 2 == 0)

/-- Precondition: Input is a list of integers. -/
def pre (xs : List Int) : Prop := True

/-- Postcondition: Output is a list of even integers from the input list. -/
def post (xs : List Int) (result : List Int) : Prop :=
  result = xs.filter (fun x => x % 2 == 0)

theorem evenNumbers_correct (xs : List Int) (h : pre xs) :
  post xs (evenNumbers xs) := by
  unfold post
  unfold evenNumbers
  rfl
  sorry

/-- Test cases for evenNumbers function -/
def test : IO Unit := do
  let test1 := evenNumbers [1, 2, 3, 4, 5, 6]
  IO.println s!"Test 1: {test1}"
  assert! test1 == [2, 4, 6]
  
  let test2 := evenNumbers []
  IO.println s!"Test 2: {test2}"
  assert! test2 == []
  
  let test3 := evenNumbers [1, 3, 5]
  IO.println s!"Test 3: {test3}"
  assert! test3 == []
  
  IO.println "All tests passed!"

end EvenNumbers
