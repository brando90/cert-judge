import Std.Data.List.Basic

/--
  This function takes a list l and returns a list l' such that
  l' is identical to l in the odd indicies, while its values at the even indicies are equal
  to the values of the even indicies of l, but sorted.
-/
def sortEven (l : List Int) : List Int :=
  let evens := l.enum.filter (fun (i, _) => i % 2 == 0) |>.map Prod.snd
  let odds := l.enum.filter (fun (i, _) => i % 2 == 1) |>.map Prod.snd
  let sortedEvens := evens.sort
  
  let zipped := sortedEvens.zip odds
  let combined := zipped.map (fun (e, o) => [e, o]) |>.join
  
  if evens.length > odds.length then
    combined ++ [sortedEvens.getLast (evens.getLast! default)]
  else
    combined

/--
  Predicate stating that a list is sorted.
-/
def isSorted (l : List Int) : Prop :=
  ∀ i j, i < j → j < l.length → l[i]! ≤ l[j]!

/--
  Predicate stating that two lists have the same elements at odd indices.
-/
def sameOddIndices (l l' : List Int) : Prop :=
  ∀ i, i < l.length → i % 2 == 1 → i < l'.length → l[i]! = l'[i]!

/--
  Predicate stating that the even indices of a list contain the same elements as another list, but sorted.
-/
def sortedEvenIndices (l l' : List Int) : Prop :=
  let evens := l.enum.filter (fun (i, _) => i % 2 == 0) |>.map Prod.snd
  let evens' := l'.enum.filter (fun (i, _) => i % 2 == 0) |>.map Prod.snd
  evens.toFinset = evens'.toFinset ∧ isSorted evens'

/--
  Specification for the sortEven function.
-/
def sortEvenSpec (l l' : List Int) : Prop :=
  sameOddIndices l l' ∧ sortedEvenIndices l l' ∧ l.length = l'.length

theorem sortEven_correct (l : List Int) : sortEvenSpec l (sortEven l) := sorry

/-- Test cases for the sortEven function. -/
def sortEvenTests : List (List Int × List Int) := [
  ([1, 2, 3], [1, 2, 3]),
  ([5, 6, 3, 4], [3, 6, 5, 4]),
  ([5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10], [-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123]),
  ([5, 8, -12, 4, 23, 2, 3, 11, 12, -10], [-12, 8, 3, 4, 5, 2, 12, 11, 23, -10])
]

/-- Run the test cases. -/
def runSortEvenTests : List Bool :=
  sortEvenTests.map (fun (input, expected) => sortEven input == expected)

/-- Check that all tests pass. -/
example : runSortEvenTests.all id = true := by native_decide
