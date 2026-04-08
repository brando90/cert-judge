import Std.Data.List.Basic

/-- Triple each integer in the input list.

Edge cases:
- Empty list returns empty list.
- Non-integer elements are invalid and raise ValueError. -/
def tripleAll (lst : List Int) : List Int :=
  lst.map (· * 3)

/-- Precondition for tripleAll -/
def tripleAllPre (lst : List Int) : Prop := True

/-- Postcondition for tripleAll -/
def tripleAllPost (lst : List Int) (result : List Int) : Prop :=
  result = lst.map (· * 3)

/-- Correctness theorem for tripleAll -/
theorem tripleAll_correct (lst : List Int) (h : tripleAllPre lst) :
  tripleAllPost lst (tripleAll lst) := by
  unfold tripleAllPost
  unfold tripleAll
  simp
  sorry

/-- Test cases for tripleAll -/
def tripleAll_test : IO Unit := do
  -- Basic test
  let test1 := tripleAll [1, 2, 3]
  IO.println test1
  assert! test1 = [3, 6, 9]
  
  -- Edge case: empty list
  let test2 := tripleAll []
  IO.println test2
  assert! test2 = []
  
  -- Negative numbers
  let test3 := tripleAll [-1, 0, 4]
  IO.println test3
  assert! test3 = [-3, 0, 12]
  
  IO.println "All tests passed!"

#eval tripleAll_test
