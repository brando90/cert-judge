import Std

/--
  Return sorted unique elements in a list.
-/
def unique (l : List Int) : List Int :=
  (l.eraseDups.toArray.qsort (·<·)).toList

/--
  Specification: unique should return a sorted list of unique elements from the input list.
-/
def uniqueSpec (l : List Int) (result : List Int) : Prop :=
  -- Result contains exactly the unique elements from l (in any order)
  (∀ x, x ∈ result ↔ x ∈ l) ∧
  -- Result is sorted
  (∀ i j, i < j → i < result.length → j < result.length → result[i]! ≤ result[j]!) ∧
  -- Result has no duplicates
  (∀ i j, i ≠ j → i < result.length → j < result.length → result[i]! ≠ result[j]!)

theorem unique_correct (l : List Int) : uniqueSpec l (unique l) := by
  sorry

def main : IO Unit := do
  let test1 := unique [5, 3, 5, 2, 3, 3, 9, 0, 123]
  IO.println s!"Test 1: {test1}"
  assert! test1 = [0, 2, 3, 5, 9, 123]
  IO.println "All tests passed!"
