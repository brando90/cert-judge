import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic

/-- For a given list of input numbers, calculate Mean Absolute Deviation
around the mean of this dataset.
Mean Absolute Deviation is the average absolute difference between each
element and a centerpoint (mean in this case):
MAD = average | x - x_mean | -/
def meanAbsoluteDeviation (numbers : List Float) : Float :=
  let mean := numbers.sum / numbers.length
  (numbers.map (fun x => Float.abs (x - mean))).sum / numbers.length

/-- Tests for the meanAbsoluteDeviation function -/
def meanAbsoluteDeviation_test : IO Unit := do
  let test1 := Float.abs (meanAbsoluteDeviation [1.0, 2.0, 3.0] - 2.0/3.0) < 1e-6
  let test2 := Float.abs (meanAbsoluteDeviation [1.0, 2.0, 3.0, 4.0] - 1.0) < 1e-6
  let test3 := Float.abs (meanAbsoluteDeviation [1.0, 2.0, 3.0, 4.0, 5.0] - 6.0/5.0) < 1e-6
  
  if test1 && test2 && test3 then
    IO.println "All tests passed!"
  else
    IO.println "Tests failed!"

/-- Precondition for meanAbsoluteDeviation: the list must not be empty -/
def meanAbsoluteDeviation_pre (numbers : List Float) : Prop :=
  numbers.length > 0

/-- Postcondition for meanAbsoluteDeviation: the result is non-negative -/
def meanAbsoluteDeviation_post (numbers : List Float) (result : Float) : Prop :=
  result ≥ 0

/-- Theorem stating that meanAbsoluteDeviation satisfies its pre and post conditions -/
theorem meanAbsoluteDeviation_correct (numbers : List Float) :
  meanAbsoluteDeviation_pre numbers → meanAbsoluteDeviation_post numbers (meanAbsoluteDeviation numbers) :=
  fun h => sorry

/-- Run the tests -/
def main : IO Unit :=
  meanAbsoluteDeviation_test
