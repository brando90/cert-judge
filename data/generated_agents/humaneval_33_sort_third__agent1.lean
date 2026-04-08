import Std

namespace HumanEval33SortThird

/--
This function takes a list l and returns a list l' such that
l' is identical to l in the indices that are not divisible by three, while its values at the indices that are divisible by three are equal
to the values of the corresponding indices of l, but sorted.
-/
def sortThird (l : List Int) : List Int :=
  let indices := List.range l.length |>.filter (fun i => i % 3 == 0)
  let values := indices.map (fun i => l.get! i)
  let sortedValues := values.sort
  let result := l.toArray
  let _ := indices.zip sortedValues |>.foldl (fun acc (i, v) => 
    acc.set! i v) result
  result.toList

/-- Specification of sortThird -/
def sortThirdSpec (l : List Int) : List Int :=
  let indices := List.range l.length |>.filter (fun i => i % 3 == 0)
  let values := indices.map (fun i => l.get! i)
  let sortedValues := values.sort
  let result := l.toArray
  let _ := indices.zip sortedValues |>.foldl (fun acc (i, v) => 
    acc.set! i v) result
  result.toList

theorem sortThird_correct (l : List Int) : sortThird l = sortThirdSpec l := by
  sorry

/-- Test cases -/
def test : IO Unit := do
  assert! (sortThird [1, 2, 3] == [1, 2, 3])
  assert! (sortThird [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] == 
           [-10, 3, -5, 2, -3, 3, 5, 0, 123, 1, 9])
  assert! (sortThird [5, 8, -12, 4, 23, 2, 3, 11, 12, -10] == 
           [-12, 8, 5, 4, 23, 2, 3, 11, 12, -10])
  assert! (sortThird [5, 6, 3, 4, 8, 9, 2] == [2, 6, 3, 4, 8, 9, 5])
  assert! (sortThird [5, 8, 3, 4, 6, 9, 2] == [2, 8, 3, 4, 6, 9, 5])
  assert! (sortThird [5, 6, 9, 4, 8, 3, 2] == [2, 6, 9, 4, 8, 3, 5])
  assert! (sortThird [5, 6, 3, 4, 8, 9, 2, 1] == [2, 6, 3, 4, 8, 9, 5, 1])
  IO.println "All tests passed!"

end HumanEval33SortThird
