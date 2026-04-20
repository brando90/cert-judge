import Mathlib

namespace SortThird


def insertionSort (l : List Int) : List Int :=
  let rec insert (x : Int) (sorted : List Int) : List Int :=
    match sorted with
    | [] => [x]
    | h :: t => if x ≤ h then x :: h :: t else h :: insert x t
  let rec sort (l : List Int) : List Int :=
    match l with
    | [] => []
    | h :: t => insert h (sort t)
  sort l


def sortThird (l : List Int) : List Int :=
  -- Get indices divisible by 3
  let thirdIndices := (List.range l.length).filter (fun i => i % 3 = 0)
  -- Extract values at those indices
  let thirdValues := thirdIndices.map (fun i => l.get! i)
  -- Sort those values
  let sortedValues := insertionSort thirdValues
  -- Create result by updating original list
  let rec updateAtIndices (original : List Int) (indices : List Nat) (values : List Int) : List Int :=
    match indices, values with
    | [], _ => original
    | _, [] => original  
    | i :: is, v :: vs => updateAtIndices (original.set i v) is vs
  updateAtIndices l thirdIndices sortedValues

-- Helper lemmas for insertion sort

/-!
# Tests
-/

example : sortThird [1, 2, 3] = [1, 2, 3] := by native_decide
#eval sortThird [1, 2, 3] -- expected: [1, 2, 3]

example : sortThird [5, 6, 3, 4, 8, 9, 2] = [2, 6, 3, 4, 8, 9, 5] := by native_decide
#eval sortThird [5, 6, 3, 4, 8, 9, 2] -- expected: [2, 6, 3, 4, 8, 9, 5]

/-!
# Tests: Edge Cases
-/

example : sortThird [] = [] := by native_decide
#eval sortThird [] -- expected: []

example : sortThird [1] = [1] := by native_decide
#eval sortThird [1] -- expected: [1]

/-!
# Positive / Negative Test-Suite
-/

/-- positive: from Python test suite -/
example : sortThird [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] = [1, 3, -5, 2, -3, 3, 5, 0, 123, 9, -10] := by native_decide
#eval sortThird [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] -- expected: [1, 3, -5, 2, -3, 3, 5, 0, 123, 9, -10]

/-- positive: from Python test suite -/
example : sortThird [5, 8, -12, 4, 23, 2, 3, 11, 12, -10] = [-10, 8, -12, 3, 23, 2, 4, 11, 12, 5] := by native_decide
#eval sortThird [5, 8, -12, 4, 23, 2, 3, 11, 12, -10] -- expected: [-10, 8, -12, 3, 23, 2, 4, 11, 12, 5]

/-- positive: sortThird [5, 6, 3, 4, 8, 9, 2, 1] -/
example : sortThird [5, 6, 3, 4, 8, 9, 2, 1] = [2, 6, 3, 4, 8, 9, 5, 1] := by native_decide
#eval sortThird [5, 6, 3, 4, 8, 9, 2, 1] -- expected: [2, 6, 3, 4, 8, 9, 5, 1]

/-- negative: non-third indices are not changed -/
example : ¬ (sortThird [5, 6, 3, 4, 8, 9, 2] = [5, 6, 3, 4, 8, 9, 2]) := by native_decide

/-!
# Tests: Properties
-/

/-- Length is preserved -/
example : (sortThird [5, 6, 3, 4, 8, 9, 2]).length = [5, 6, 3, 4, 8, 9, 2].length := by native_decide
#eval (sortThird [5, 6, 3, 4, 8, 9, 2]).length -- expected: 7

/-- Idempotent: applying sortThird twice gives same result -/
example : sortThird (sortThird [5, 6, 3, 4, 8, 9, 2]) = sortThird [5, 6, 3, 4, 8, 9, 2] := by native_decide



end SortThird
