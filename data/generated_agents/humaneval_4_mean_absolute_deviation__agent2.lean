import Mathlib.Data.List.Basic
import Mathlib.Tactic.Ring

/--
For a given list of input numbers, calculate Mean Absolute Deviation
around the mean of this dataset.
Mean Absolute Deviation is the average absolute difference between each
element and a centerpoint (mean in this case):
MAD = average | x - x_mean |

Implementation:
- Calculate the mean of the list
- For each element, calculate the absolute difference from the mean
- Return the average of these differences
-/
def mean_absolute_deviation (numbers : List Float) : Float :=
  if numbers.length = 0 then
    0
  else
    let mean := numbers.sum / numbers.length
    let deviations := numbers.map (fun x => abs (x - mean))
    deviations.sum / numbers.length

/-- The mean of a list is the sum divided by the length -/
def mean (numbers : List Float) : Float :=
  if numbers.length = 0 then 0 else numbers.sum / numbers.length

/-- Specification of mean_absolute_deviation using the mean function -/
def mean_absolute_deviation_spec (numbers : List Float) : Float :=
  if numbers.length = 0 then
    0
  else
    let m := mean numbers
    (numbers.map (fun x => abs (x - m))).sum / numbers.length

/-- Precondition: The list should not be empty -/
def mean_absolute_deviation_pre (numbers : List Float) : Prop :=
  numbers.length > 0

/-- Postcondition: The result should be non-negative -/
def mean_absolute_deviation_post (numbers : List Float) (result : Float) : Prop :=
  result ≥ 0

/-- The implementation satisfies the specification -/
theorem mean_absolute_deviation_correct (numbers : List Float) :
  mean_absolute_deviation numbers = mean_absolute_deviation_spec numbers := by
  sorry

/-- The implementation satisfies the postcondition when the precondition is met -/
theorem mean_absolute_deviation_pre_post (numbers : List Float) :
  mean_absolute_deviation_pre numbers → mean_absolute_deviation_post numbers (mean_absolute_deviation numbers) := by
  sorry

/-- Test cases -/
def test_mean_absolute_deviation : Bool :=
  let test1 := abs (mean_absolute_deviation [1.0, 2.0, 3.0] - 2.0/3.0) < 1e-6
  let test2 := abs (mean_absolute_deviation [1.0, 2.0, 3.0, 4.0] - 1.0) < 1e-6
  let test3 := abs (mean_absolute_deviation [1.0, 2.0, 3.0, 4.0, 5.0] - 6.0/5.0) < 1e-6
  test1 && test2 && test3

#eval test_mean_absolute_deviation -- Should return true
