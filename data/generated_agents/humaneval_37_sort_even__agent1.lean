import Mathlib

namespace VeriBench.HumanEval37

/-- This function takes a list l and returns a list l' such that
    l' is identical to l in the odd indicies, while its values at the even indicies are equal
    to the values of the even indicies of l, but sorted. -/
def sortEven (l : List Int) : List Int :=
  let evens := l.enum.filterMap (fun (i, v) => if i % 2 = 0 then some v else none)
  let odds := l.enum.filterMap (fun (i, v) => if i % 2 = 1 then some v else none)
  let sortedEvens := evens.qsort (· ≤ ·)
  let zipped := sortedEvens.zip odds
  let result := zipped.foldl (fun acc (e, o) => acc ++ [e, o]) []
  if evens.length > odds.length then
    result ++ [sortedEvens.getLast (by sorry)]
  else
    result

/-- Test cases for sortEven -/
def test : IO Unit := do
  assert! (sortEven [1, 2, 3] == [1, 2, 3])
  assert! (sortEven [5, 6, 3, 4] == [3, 6, 5, 4])
  assert! (sortEven [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] == [-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123])
  assert! (sortEven [5, 8, -12, 4, 23, 2, 3, 11, 12, -10] == [-12, 8, 3, 4, 5, 2, 12, 11, 23, -10])
  IO.println "All tests passed!"

/-- Predicate that checks if a list has its even indices sorted -/
def hasEvenIndicesSorted (l : List Int) : Prop :=
  let evens := l.enum.filterMap (fun (i, v) => if i % 2 = 0 then some v else none)
  evens.sorted (· ≤ ·)

/-- Predicate that checks if two lists have the same values at odd indices -/
def sameOddIndices (l₁ l₂ : List Int) : Prop :=
  let odds₁ := l₁.enum.filterMap (fun (i, v) => if i % 2 = 1 then some v else none)
  let odds₂ := l₂.enum.filterMap (fun (i, v) => if i % 2 = 1 then some v else none)
  odds₁ = odds₂

/-- Predicate that checks if two lists have the same values at even indices (ignoring order) -/
def sameEvenIndicesMultiset (l₁ l₂ : List Int) : Prop :=
  let evens₁ := l₁.enum.filterMap (fun (i, v) => if i % 2 = 0 then some v else none)
  let evens₂ := l₂.enum.filterMap (fun (i, v) => if i % 2 = 0 then some v else none)
  evens₁.toMultiset = evens₂.toMultiset

/-- Correctness theorem for sortEven -/
theorem sortEven_correct (l : List Int) : 
  hasEvenIndicesSorted (sortEven l) ∧ 
  sameOddIndices (sortEven l) l ∧
  sameEvenIndicesMultiset (sortEven l) l := by
  sorry

end VeriBench.HumanEval37
