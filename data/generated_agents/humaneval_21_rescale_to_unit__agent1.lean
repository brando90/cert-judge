import Mathlib.Tactic.Basic
import Mathlib.Tactic.Ring
import Mathlib.Data.Real.Basic

/--
Given list of numbers (of at least two elements), apply a linear transform to that list,
such that the smallest number will become 0 and the largest will become 1
-/
def rescaleToUnit (numbers : List Float) : List Float :=
  let minNumber := numbers.minimum?.getD 0
  let maxNumber := numbers.maximum?.getD 0
  numbers.map (fun x => (x - minNumber) / (maxNumber - minNumber))

/-- Tests for rescaleToUnit -/
def rescaleToUnitTests : List (List Float × List Float) := [
  ([2.0, 49.9], [0.0, 1.0]),
  ([100.0, 49.9], [1.0, 0.0]),
  ([1.0, 2.0, 3.0, 4.0, 5.0], [0.0, 0.25, 0.5, 0.75, 1.0]),
  ([2.0, 1.0, 5.0, 3.0, 4.0], [0.25, 0.0, 1.0, 0.5, 0.75]),
  ([12.0, 11.0, 15.0, 13.0, 14.0], [0.25, 0.0, 1.0, 0.5, 0.75])
]

/-- Run tests for rescaleToUnit -/
def testRescaleToUnit : IO Unit := do
  for (input, expected) in rescaleToUnitTests do
    let result := rescaleToUnit input
    if result == expected then
      IO.println s!"Test passed for {input}"
    else
      IO.println s!"Test failed for {input}. Expected {expected}, got {result}"

/-- Precondition: The list has at least two elements and the min and max are different -/
def rescaleToUnitPre (numbers : List Float) : Prop :=
  numbers.length ≥ 2 ∧
  numbers.maximum?.getD 0 ≠ numbers.minimum?.getD 0

/-- 
Postcondition: 
1. The result list has the same length as the input
2. The minimum value in the result is 0
3. The maximum value in the result is 1
-/
def rescaleToUnitPost (numbers : List Float) (result : List Float) : Prop :=
  result.length = numbers.length ∧
  result.minimum?.getD 0 = 0 ∧
  result.maximum?.getD 0 = 1

/-- Correctness theorem for rescaleToUnit -/
theorem rescaleToUnitCorrect (numbers : List Float) : 
  rescaleToUnitPre numbers → rescaleToUnitPost numbers (rescaleToUnit numbers) := by
  sorry
