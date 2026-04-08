```lean
import Std

/--
  Return only positive numbers in the list.
-/
def getPositive (l : List Int) : List Int :=
  l.filter (· > 0)

/--
  Test function for `getPositive`.
-/
def test : IO Unit := do
  assert! (getPositive [-1, -2, 4, 5, 6] == [4, 5, 6])
  assert! (getPositive [5, 3, -5, 2, 3, 3, 9, 0, 123, 1, -10] == [5, 3, 2, 3, 3, 9, 123, 1])
  assert! (getPositive [-1, -2] == [])
  assert! (getPositive [] == [])
  IO.println "All tests passed!"

/--
  Specification for `getPositive`.
-/
def getPositiveSpec (l : List Int) (result : List Int) : Prop :=
  ∀ x, x ∈ result ↔ (x ∈ l ∧ x > 0)

/--
  Correctness theorem for `getPositive`.
-/
theorem getPositive_correct (l : List Int) : 
  getPositiveSpec l (getPositive l) := by
  unfold getPositiveSpec
  unfold getPositive
  intro x
  simp [List.filter_eq]
  sorry

#eval test
```
