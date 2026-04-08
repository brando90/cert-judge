```lean
def below_threshold (l : List Int) (t : Int) : Bool :=
  l.all (· < t)

theorem below_threshold_correct (l : List Int) (t : Int) :
  below_threshold l t = true ↔ ∀ e ∈ l, e < t := by
  simp [below_threshold, List.all_eq_true]
  sorry

def test_below_threshold : IO Unit := do
  assert! (below_threshold [1, 2, 4, 10] 100 = true)
  assert! (below_threshold [1, 20, 4, 10] 5 = false)
  assert! (below_threshold [1, 20, 4, 10] 21 = true)
  assert! (below_threshold [1, 20, 4, 10] 22 = true)
  assert! (below_threshold [1, 8, 4, 10] 11 = true)
  assert! (below_threshold [1, 8, 4, 10] 10 = false)
  IO.println "All tests passed!"

#eval test_below_threshold
```
