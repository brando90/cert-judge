```lean
import Lean
import Std.Data.List.Basic

namespace HumanEval30

/--
Return only positive numbers in the list.
-/
def getPositive (l : List Int) : List Int :=
  l.filter (λ e => e > 0)

/-- The function returns only positive numbers from the input list. -/
theorem getPositive_spec (l : List Int) :
  getPositive l = l.filter (λ e => e > 0) := by
  rfl

/-- Tests for getPositive function -/
def getPositiveTests : IO Unit := do
  let test1 := getPositive [-1, -2, 4, 5, 6]
  IO.println s!"Test 1: {test1}"
  assert! test1 == [4, 5, 6]

  let test2 := getPositive [5, 3, -5, 2, 3, 3, 9, 0, 123, 1, -10]
  IO.println s!"Test 2: {test2}"
  assert! test2 == [5, 3, 2, 3, 3, 9, 123, 1]

  let test3 := getPositive [-1, -2]
  IO.println s!"Test 3: {test3}"
  assert! test3 == []

  let test4 := getPositive []
  IO.println s!"Test 4: {test4}"
  assert! test4 == []

  IO.println "All tests passed!"

/-- Correctness theorems for getPositive -/

theorem getPositive_preserves_positivity (l : List Int) :
  ∀ x ∈ getPositive l, x > 0 := by
  intro x h
  have h' := List.mem_filter.mp h
  exact h'.2
  
theorem getPositive_preserves_membership (l : List Int) :
  ∀ x, x ∈ getPositive l ↔ x ∈ l ∧ x > 0 := by
  intro x
  exact List.mem_filter

theorem getPositive_empty (l : List Int) :
  (∀ x ∈ l, x ≤ 0) → getPositive l = [] := by
  intro h
  simp [getPositive]
  apply List.filter_eq_nil.mpr
  intro x hx
  apply not_lt.mpr
  exact h x hx

end HumanEval30
```
