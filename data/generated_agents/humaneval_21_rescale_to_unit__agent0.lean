import Lean.Data.HashMap
import Std.Data.List.Basic
import Std.Data.Array.Basic

/-!
# rescale_to_unit

Given list of numbers (of at least two elements), apply a linear transform to that list,
such that the smallest number will become 0 and the largest will become 1
-/

def rescale_to_unit (numbers : List Float) : List Float :=
  let min_number := numbers.minimum?.getD 0.0
  let max_number := numbers.maximum?.getD 0.0
  numbers.map (fun x => (x - min_number) / (max_number - min_number))

/-- Test cases for `rescale_to_unit` -/
def test : IO Unit := do
  let t1 := rescale_to_unit [2.0, 49.9]
  IO.println s!"Test 1: {t1}"
  assert! t1 == [0.0, 1.0]

  let t2 := rescale_to_unit [100.0, 49.9]
  IO.println s!"Test 2: {t2}"
  assert! t2 == [1.0, 0.0]

  let t3 := rescale_to_unit [1.0, 2.0, 3.0, 4.0, 5.0]
  IO.println s!"Test 3: {t3}"
  assert! t3 == [0.0, 0.25, 0.5, 0.75, 1.0]

  let t4 := rescale_to_unit [2.0, 1.0, 5.0, 3.0, 4.0]
  IO.println s!"Test 4: {t4}"
  assert! t4 == [0.25, 0.0, 1.0, 0.5, 0.75]

  let t5 := rescale_to_unit [12.0, 11.0, 15.0, 13.0, 14.0]
  IO.println s!"Test 5: {t5}"
  assert! t5 == [0.25, 0.0, 1.0, 0.5, 0.75]

  IO.println "All tests passed!"

/--
Precondition for `rescale_to_unit`:
- The input list must have at least two elements
- The maximum and minimum values must be different
-/
def rescale_to_unit.pre (numbers : List Float) : Prop :=
  numbers.length ≥ 2 ∧ 
  numbers.maximum?.getD 0.0 ≠ numbers.minimum?.getD 0.0

/--
Postcondition for `rescale_to_unit`:
- The output list has the same length as the input list
- The minimum value in the output list is 0.0
- The maximum value in the output list is 1.0
- The relative ordering of elements is preserved
-/
def rescale_to_unit.post (numbers : List Float) (result : List Float) : Prop :=
  result.length = numbers.length ∧
  result.minimum?.getD 0.0 = 0.0 ∧
  result.maximum?.getD 0.0 = 1.0 ∧
  (∀ i j, i < numbers.length → j < numbers.length → 
    numbers.get? i = some (numbers.get? j).get → result.get? i = result.get? j)

/--
Correctness theorem for `rescale_to_unit`:
If the precondition holds, then the postcondition holds for the result.
-/
theorem rescale_to_unit.correct (numbers : List Float) :
  rescale_to_unit.pre numbers → rescale_to_unit.post numbers (rescale_to_unit numbers) :=
sorry

#eval test
