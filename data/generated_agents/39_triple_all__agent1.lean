import Std.Data.List.Basic

/--
Triple each integer in the input list.
-/
def tripleAll (lst : List Int) : List Int :=
  lst.map (fun x => x * 3)

/-- Specification for tripleAll -/
def tripleAll_spec (lst : List Int) (result : List Int) : Prop :=
  result = lst.map (fun x => x * 3)

theorem tripleAll_correct (lst : List Int) : tripleAll_spec lst (tripleAll lst) := by
  unfold tripleAll_spec
  unfold tripleAll
  simp
  sorry

/-- Tests for tripleAll -/
def tripleAll_test : IO Unit := do
  -- Basic test
  assert! (tripleAll [1, 2, 3] == [3, 6, 9])
  
  -- Empty list test
  assert! (tripleAll [] == [])
  
  -- Negative numbers
  assert! (tripleAll [-1, 0, 4] == [-3, 0, 12])
  
  IO.println "All tests passed!"

#eval tripleAll_test
