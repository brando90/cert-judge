import Std.Data.List.Basic
import Mathlib.Data.List.Sort

namespace HumanEval33

def sortThird (l : List Int) : List Int :=
  let indices := List.range l.length
  let pairs := List.zip indices l
  let sortedThirdIndices := pairs
    |> List.filter (fun (i, _) => i % 3 == 0)
    |> List.map (fun (_, v) => v)
    |> List.sort
  
  let thirdIndicesIter := sortedThirdIndices.enum
  
  indices.foldl (init := []) fun acc i => 
    if i % 3 == 0 then
      let idx := i / 3
      let value := (thirdIndicesIter.get! idx).2
      acc ++ [value]
    else
      acc ++ [l.get! i]

def testSortThird : IO Unit := do
  let test1 := sortThird [1, 2, 3]
  IO.println s!"Test 1: {test1}"
  assert! test1 == [1, 2, 3]
  
  let test2 := sortThird [5, 6, 3, 4, 8, 9, 2]
  IO.println s!"Test 2: {test2}"
  assert! test2 == [2, 6, 3, 4, 8, 9, 5]
  
  let test3 := sortThird [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10]
  IO.println s!"Test 3: {test3}"
  assert! test3 == [-10, 3, -5, 2, -3, 3, 5, 0, 123, 1, 9]
  
  let test4 := sortThird [5, 8, -12, 4, 23, 2, 3, 11, 12, -10]
  IO.println s!"Test 4: {test4}"
  assert! test4 == [-12, 8, 3, 4, 23, 2, 5, 11, 12, -10]
  
  let test5 := sortThird [5, 8, 3, 4, 6, 9, 2]
  IO.println s!"Test 5: {test5}"
  assert! test5 == [2, 8, 3, 4, 6, 9, 5]
  
  let test6 := sortThird [5, 6, 9, 4, 8, 3, 2]
  IO.println s!"Test 6: {test6}"
  assert! test6 == [2, 6, 9, 4, 8, 3, 5]
  
  let test7 := sortThird [5, 6, 3, 4, 8, 9, 2, 1]
  IO.println s!"Test 7: {test7}"
  assert! test7 == [2, 6, 3, 4, 8, 9, 5, 1]
  
  IO.println "All tests passed!"

/-- 
  sortThird takes a list l and returns a list l' such that
  l' is identical to l in the indices that are not divisible by three, while its values at the indices that are divisible by three are equal
  to the values of the corresponding indices of l, but sorted.
-/
def sortThirdSpec (l : List Int) : List Int :=
  let thirdIndices := List.range l.length |> List.filter (fun i => i % 3 == 0)
  let thirdValues := thirdIndices.map (fun i => l.get! i)
  let sortedThirdValues := List.sort thirdValues
  
  List.range l.length |> List.map fun i =>
    if i % 3 == 0 then
      let idx := i / 3
      sortedThirdValues.get! idx
    else
      l.get! i

theorem sortThird_correct (l : List Int) : sortThird l = sortThirdSpec l := by
  sorry

end HumanEval33
