import Lean
import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic

namespace HumanEval20

/--
  From a supplied list of numbers (of length at least two) select and return two that are the closest to each
  other and return them in order (smaller number, larger number).
-/
def find_closest_elements (numbers : List Float) : Float × Float :=
  let rec helper (idx : Nat) (closest_pair : Float × Float) (distance : Float) : Float × Float :=
    if h : idx < numbers.length then
      let elem := numbers.get ⟨idx, h⟩
      let rec inner_helper (idx2 : Nat) (cp : Float × Float) (d : Float) : Float × Float :=
        if h2 : idx2 < numbers.length then
          let elem2 := numbers.get ⟨idx2, h2⟩
          if idx != idx2 then
            let new_distance := Float.abs (elem - elem2)
            if new_distance < d then
              inner_helper (idx2 + 1) (min elem elem2, max elem elem2) new_distance
            else
              inner_helper (idx2 + 1) cp d
          else
            inner_helper (idx2 + 1) cp d
        else
          cp
      let (new_pair, new_distance) := 
        match idx with
        | 0 => 
            let e1 := numbers.get ⟨0, by simp [h]⟩
            let e2 := numbers.get ⟨1, by {
              have : 1 < numbers.length := by {
                simp
                exact Nat.le_trans (Nat.le_of_lt (Nat.zero_lt_succ 1)) (Nat.le_of_lt h)
              }
              exact this
            }⟩
            ((min e1 e2, max e1 e2), Float.abs (e1 - e2))
        | _ => (closest_pair, distance)
      let result := inner_helper 0 new_pair new_distance
      helper (idx + 1) result new_distance
    else
      closest_pair
  
  let first := numbers.get! 0
  let second := numbers.get! 1
  helper 0 (min first second, max first second) (Float.abs (first - second))

/-- Predicate stating that a list has at least two elements -/
def hasAtLeastTwo (l : List α) : Prop :=
  l.length ≥ 2

/-- Predicate stating that a pair (a, b) has a ≤ b -/
def orderedPair (p : Float × Float) : Prop :=
  p.1 ≤ p.2

/--
  The find_closest_elements function returns a pair of elements from the input list
  that have the minimum distance between them, and the pair is ordered.
-/
theorem find_closest_elements_spec (numbers : List Float) (h : hasAtLeastTwo numbers) :
  let result := find_closest_elements numbers
  orderedPair result ∧
  (∃ i j, i < numbers.length ∧ j < numbers.length ∧ i ≠ j ∧
    result.1 = numbers[i] ∧ result.2 = numbers[j]) ∧
  (∀ i j, i < numbers.length → j < numbers.length → i ≠ j →
    Float.abs (numbers[i] - numbers[j]) ≥ Float.abs (result.1 - result.2)) := sorry

/-- Test cases for find_closest_elements -/
def tests : List (List Float × (Float × Float)) := [
  ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], (3.9, 4.0)),
  ([1.0, 2.0, 5.9, 4.0, 5.0], (5.0, 5.9)),
  ([1.0, 2.0, 3.0, 4.0, 5.0, 2.2], (2.0, 2.2)),
  ([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], (2.0, 2.0)),
  ([1.1, 2.2, 3.1, 4.1, 5.1], (2.2, 3.1))
]

/-- Run the test cases -/
def runTests : List Bool :=
  tests.map (fun (test : List Float × (Float × Float)) =>
    find_closest_elements test.1 == test.2)

/-- All tests should pass -/
theorem all_tests_pass : runTests.all id = true := by native_decide

end HumanEval20
