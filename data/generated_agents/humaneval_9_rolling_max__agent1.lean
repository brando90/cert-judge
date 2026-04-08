import VeriBench.Common
import VeriBench.List

namespace HumanEval9

/--
From a given list of integers, generate a list of rolling maximum element found until given moment
in the sequence.
-/
def rolling_max (numbers : List Int) : List Int :=
  let rec aux (running_max : Option Int) (result : List Int) (remaining : List Int) : List Int :=
    match remaining with
    | [] => result.reverse
    | n :: rest =>
      let new_max := match running_max with
        | none => n
        | some m => max m n
      aux (some new_max) (new_max :: result) rest
  aux none [] numbers

/-- The rolling max of an empty list is an empty list. -/
theorem rolling_max_nil : rolling_max [] = [] := by
  simp [rolling_max]
  sorry

/-- The rolling max of a singleton list is the singleton list itself. -/
theorem rolling_max_singleton (n : Int) : rolling_max [n] = [n] := by
  simp [rolling_max]
  sorry

/-- The rolling max is always the same length as the input list. -/
theorem rolling_max_length (numbers : List Int) : 
  (rolling_max numbers).length = numbers.length := by
  sorry

/-- Every element in the rolling max list is greater than or equal to the corresponding element in the input list. -/
theorem rolling_max_ge (numbers : List Int) (i : Nat) (h : i < numbers.length) :
  (rolling_max numbers).get ⟨i, by rw [rolling_max_length]; exact h⟩ ≥ numbers.get ⟨i, h⟩ := by
  sorry

/-- The rolling max list is monotonically non-decreasing. -/
theorem rolling_max_monotonic (numbers : List Int) (i j : Nat) 
  (hi : i < numbers.length) (hj : j < numbers.length) (hij : i ≤ j) :
  (rolling_max numbers).get ⟨i, by rw [rolling_max_length]; exact hi⟩ ≤ 
  (rolling_max numbers).get ⟨j, by rw [rolling_max_length]; exact hj⟩ := by
  sorry

/-- Specification: rolling_max returns a list where each element is the maximum of all elements up to that point. -/
theorem rolling_max_spec (numbers : List Int) (i : Nat) (h : i < numbers.length) :
  (rolling_max numbers).get ⟨i, by rw [rolling_max_length]; exact h⟩ = 
  List.foldl (init := numbers.get ⟨0, numbers.length_pos_of_mem h⟩) 
    (fun acc x => max acc x) 
    (numbers.take (i + 1)) := by
  sorry

/-- Tests for rolling_max -/
def test_rolling_max : IO Unit := do
  IO.println "Testing rolling_max..."
  assert $ rolling_max [] == []
  assert $ rolling_max [1, 2, 3, 4] == [1, 2, 3, 4]
  assert $ rolling_max [4, 3, 2, 1] == [4, 4, 4, 4]
  assert $ rolling_max [3, 2, 3, 100, 3] == [3, 3, 3, 100, 100]
  assert $ rolling_max [1, 2, 3, 2, 3, 4, 2] == [1, 2, 3, 3, 3, 4, 4]
  IO.println "All tests passed!"

end HumanEval9
