```lean
import Mathlib.Data.List.Basic
import Mathlib.Data.List.Sort
import Mathlib.Data.Finset.Basic

/-- 
  `unique` returns sorted unique elements in a list.
  
  Example:
  ```
  unique [5, 3, 5, 2, 3, 3, 9, 0, 123] = [0, 2, 3, 5, 9, 123]
  ```
-/
def unique (l : List Int) : List Int :=
  (l.toFinset.toList.mergeSort (· ≤ ·))

/-- Predicate stating that a list contains no duplicates -/
def NoDuplicates (l : List Int) : Prop :=
  ∀ x, l.count x ≤ 1

/-- Predicate stating that a list is sorted in ascending order -/
def Sorted (l : List Int) : Prop :=
  ∀ i j, i < j → j < l.length → l[i]! ≤ l[j]!

/-- Predicate stating that two lists contain the same elements with the same multiplicities -/
def SameElements (l₁ l₂ : List Int) : Prop :=
  ∀ x, l₁.count x = l₂.count x

/-- Specification for the `unique` function -/
def UniqueSpec (l input : List Int) : Prop :=
  NoDuplicates l ∧ Sorted l ∧ SameElements l (input.dedup)

theorem unique_correct (l : List Int) : UniqueSpec (unique l) l := by
  sorry

/-- Test cases for the `unique` function -/
def uniqueTests : List (List Int × List Int) := [
  ([5, 3, 5, 2, 3, 3, 9, 0, 123], [0, 2, 3, 5, 9, 123])
]

/-- Run the test cases -/
def runUniqueTests : List Bool :=
  uniqueTests.map (fun (input, expected) => unique input = expected)

/-- All tests should pass -/
theorem uniqueTestsPass : runUniqueTests.all id = true := by
  simp [runUniqueTests, uniqueTests]
  decide
```
