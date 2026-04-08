/-
File: humaneval_42_incr_list.lean
-/

def incr_list (l : List Int) : List Int :=
  l.map (λ e => e + 1)

/-- Return list with elements incremented by 1. -/
def incr_list_spec (l : List Int) : List Int :=
  l.map (λ e => e + 1)

/-- Correctness theorem for incr_list -/
theorem incr_list_correct (l : List Int) : incr_list l = incr_list_spec l := by
  simp [incr_list, incr_list_spec]

/-! Tests -/
def test_incr_list : IO Unit := do
  assert! (incr_list [] == [])
  assert! (incr_list [3, 2, 1] == [4, 3, 2])
  assert! (incr_list [5, 2, 5, 2, 3, 3, 9, 0, 123] == [6, 3, 6, 3, 4, 4, 10, 1, 124])
  IO.println "All tests passed!"

/-! Main -/
def main : IO Unit :=
  test_incr_list
