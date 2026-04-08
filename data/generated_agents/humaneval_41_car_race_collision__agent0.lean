```lean
/- VeriBench problem: car_race_collision -/

def carRaceCollision (n : Int) : Int :=
  n * n

theorem carRaceCollision_spec (n : Int) (h : n ≥ 0) : carRaceCollision n = n * n := by
  unfold carRaceCollision
  rfl

/-- Test cases for carRaceCollision -/
def carRaceCollision_tests : List (Int × Int) :=
  [(2, 4), (3, 9), (4, 16), (8, 64), (10, 100)]

/-- Run all test cases -/
def runCarRaceCollisionTests : IO Unit := do
  for (input, expected) in carRaceCollision_tests do
    let result := carRaceCollision input
    if result != expected then
      throw (IO.userError s!"Test failed: carRaceCollision {input} = {result}, but expected {expected}")

/-- Verify all test cases -/
theorem carRaceCollision_tests_correct : ∀ (test : Int × Int), test ∈ carRaceCollision_tests →
  carRaceCollision test.1 = test.2 := by
  intro test h
  cases test with
  | mk input expected =>
    simp at h
    have input_nonneg : input ≥ 0 := by
      cases h <;> (try simp; try omega)
    rw [carRaceCollision_spec input input_nonneg]
    cases h <;> simp

#eval runCarRaceCollisionTests
```
