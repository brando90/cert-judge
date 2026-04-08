import Std.Data.List.Basic

namespace HumanEval33

/-- 
This function takes a list l and returns a list l' such that
l' is identical to l in the indicies that are not divisible by three, while its values at the indicies that are divisible by three are equal
to the values of the corresponding indicies of l, but sorted.
-/
def sortThird (l : List Int) : List Int :=
  let indices := List.range l.length
  let sortedEveryThird := l.filterWithIndex (fun i _ => i % 3 == 0) |>.sort
  
  let rec buildResult (remaining : List Int) (everyThird : List Int) (i : Nat) (acc : List Int) : List Int :=
    match remaining with
    | [] => acc.reverse
    | x :: xs =>
      if i % 3 == 0 then
        match everyThird with
        | [] => acc.reverse ++ remaining -- Should not happen if inputs are valid
        | y :: ys => buildResult xs ys (i+1) (y :: acc)
      else
        buildResult xs everyThird (i+1) (x :: acc)
  
  buildResult l sortedEveryThird 0 []

/-- Specification: sortThird returns a list where elements at indices divisible by 3 are sorted -/
def spec (l : List Int) : List Int :=
  let everyThird := l.filterWithIndex (fun i _ => i % 3 == 0) |>.sort
  let rec replace (l : List Int) (replacements : List Int) (i : Nat) : List Int :=
    match l with
    | [] => []
    | x :: xs =>
      if i % 3 == 0 then
        match replacements with
        | [] => x :: replace xs [] (i+1) -- Should not happen if inputs are valid
        | y :: ys => y :: replace xs ys (i+1)
      else
        x :: replace xs replacements (i+1)
  replace l everyThird 0

/-- Precondition: Always true -/
def pre (_l : List Int) : Prop := True

/-- Postcondition: sortThird returns a list with the same length as the input -/
def post (l : List Int) (result : List Int) : Prop :=
  l.length = result.length ∧
  (∀ i, i < l.length → i % 3 ≠ 0 → l.get? i = result.get? i) ∧
  (List.filterWithIndex (fun i _ => i % 3 == 0) result |>.sort = List.filterWithIndex (fun i _ => i % 3 == 0) result)

theorem sortThird_correct (l : List Int) (h : pre l) : post l (sortThird l) := sorry

/-- Tests for sortThird function -/
def tests : IO Unit := do
  let test1 := sortThird [1, 2, 3] = [1, 2, 3]
  let test2 := sortThird [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] = [-10, 3, -5, 2, -3, 3, 5, 0, 123, 1, 9]
  let test3 := sortThird [5, 8, -12, 4, 23, 2, 3, 11, 12, -10] = [-12, 8, 5, 4, 23, 2, 3, 11, 12, -10]
  let test4 := sortThird [5, 6, 3, 4, 8, 9, 2] = [2, 6, 3, 4, 8, 9, 5]
  let test5 := sortThird [5, 8, 3, 4, 6, 9, 2] = [2, 8, 3, 4, 6, 9, 5]
  let test6 := sortThird [5, 6, 9, 4, 8, 3, 2] = [2, 6, 9, 4, 8, 3, 5]
  let test7 := sortThird [5, 6, 3, 4, 8, 9, 2, 1] = [2, 6, 3, 4, 8, 9, 5, 1]
  
  IO.println s!"Test 1: {test1}"
  IO.println s!"Test 2: {test2}"
  IO.println s!"Test 3: {test3}"
  IO.println s!"Test 4: {test4}"
  IO.println s!"Test 5: {test5}"
  IO.println s!"Test 6: {test6}"
  IO.println s!"Test 7: {test7}"
  
  if test1 && test2 && test3 && test4 && test5 && test6 && test7 then
    IO.println "All tests passed!"
  else
    throw (IO.userError "Some tests failed!")

end HumanEval33
