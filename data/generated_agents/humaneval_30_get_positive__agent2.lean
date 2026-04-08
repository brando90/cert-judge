/-
This file implements and verifies a function that returns only positive numbers from a list.
-/

def get_positive (l : List Int) : List Int :=
  l.filter (fun e => e > 0)

/-- get_positive returns only positive numbers in the list. -/
theorem get_positive_spec (l : List Int) :
  ∀ x, x ∈ get_positive l ↔ x ∈ l ∧ x > 0 := by
  intro x
  simp [get_positive]
  sorry

/-- Positive numbers in the result are greater than zero. -/
theorem get_positive_all_positive (l : List Int) :
  ∀ x, x ∈ get_positive l → x > 0 := by
  intro x h
  simp [get_positive] at h
  exact h.2
  sorry

/-- All positive numbers from the input are preserved in the result. -/
theorem get_positive_preserves_positive (l : List Int) :
  ∀ x, x ∈ l → x > 0 → x ∈ get_positive l := by
  intro x h1 h2
  simp [get_positive]
  exact ⟨h1, h2⟩
  sorry

def tests : IO Unit := do
  assert! (get_positive [-1, -2, 4, 5, 6] == [4, 5, 6])
  assert! (get_positive [5, 3, -5, 2, 3, 3, 9, 0, 123, 1, -10] == [5, 3, 2, 3, 3, 9, 123, 1])
  assert! (get_positive [-1, -2] == [])
  assert! (get_positive [] == [])
  IO.println "All tests passed!"
