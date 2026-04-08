```lean
import Std.Data.List.Basic

def max_element (l: List Int): Int :=
  match l with
  | [] => 0 -- Default value for empty list
  | x :: xs =>
    let rec loop (current_max: Int) (remaining: List Int): Int :=
      match remaining with
      | [] => current_max
      | y :: ys => 
        if y > current_max then
          loop y ys
        else
          loop current_max ys
    loop x xs

/-- max_element returns the maximum element in a non-empty list. -/
def max_element_spec (l: List Int): Int :=
  match l with
  | [] => 0 -- Default value for empty list
  | x :: xs => xs.foldl (fun acc e => if e > acc then e else acc) x

/-- Tests for max_element function -/
def max_element_tests : List (List Int × Int) := [
  ([1, 2, 3], 3),
  ([5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10], 124)
]

theorem max_element_correct (l: List Int) : 
  max_element l = max_element_spec l := by
  sorry

/-- Verify that max_element passes all tests -/
example : List.all max_element_tests (fun (input, expected) => max_element input = expected) = true := by
  simp [max_element_tests, List.all]
  constructor
  · rfl
  · constructor
    · rfl
    · constructor
```
