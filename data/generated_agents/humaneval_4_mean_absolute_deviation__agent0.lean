import Mathlib.Data.Real.Basic
import Std.Data.List.Basic

namespace VeriBench.HumanEval.MeanAbsoluteDeviation

/-- For a given list of input numbers, calculate Mean Absolute Deviation
around the mean of this dataset.
Mean Absolute Deviation is the average absolute difference between each
element and a centerpoint (mean in this case):
MAD = average | x - x_mean | -/
def meanAbsoluteDeviation (numbers : List Float) : Float :=
  if numbers.isEmpty then
    0
  else
    let mean := numbers.sum / numbers.length
    (numbers.map (fun x => Float.abs (x - mean))).sum / numbers.length

/-- Mean of a list of floats -/
def mean (numbers : List Float) : Float :=
  if numbers.isEmpty then 0 else numbers.sum / numbers.length

/-- Precondition: The list is non-empty -/
def pre (numbers : List Float) : Prop :=
  ¬numbers.isEmpty

/-- Postcondition: The result is the mean absolute deviation -/
def post (numbers : List Float) (result : Float) : Prop :=
  pre numbers →
  result = (numbers.map (fun x => Float.abs (x - mean numbers))).sum / numbers.length

/-- Correctness theorem: meanAbsoluteDeviation satisfies its specification -/
theorem meanAbsoluteDeviation_correct (numbers : List Float) :
  post numbers (meanAbsoluteDeviation numbers) := by
  sorry

/-- Tests -/
def test : IO Unit := do
  let test1 := meanAbsoluteDeviation [1.0, 2.0, 3.0]
  let test2 := meanAbsoluteDeviation [1.0, 2.0, 3.0, 4.0]
  let test3 := meanAbsoluteDeviation [1.0, 2.0, 3.0, 4.0, 5.0]
  
  if Float.abs (test1 - 2.0/3.0) < 1e-6 then
    IO.println "Test 1 passed"
  else
    IO.println s!"Test 1 failed: expected {2.0/3.0}, got {test1}"
  
  if Float.abs (test2 - 1.0) < 1e-6 then
    IO.println "Test 2 passed"
  else
    IO.println s!"Test 2 failed: expected {1.0}, got {test2}"
  
  if Float.abs (test3 - 6.0/5.0) < 1e-6 then
    IO.println "Test 3 passed"
  else
    IO.println s!"Test 3 failed: expected {6.0/5.0}, got {test3}"

end VeriBench.HumanEval.MeanAbsoluteDeviation
