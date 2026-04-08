import Std.Tactic.Basic

/--
Return list with elements incremented by 1.
-/
def incr_list (l : List Int) : List Int :=
  l.map (λ e => e + 1)

/-- Tests for incr_list -/
def incr_list_tests : List (List Int × List Int) := [
  ([], []),
  ([3, 2, 1], [4, 3, 2]),
  ([5, 2, 5, 2, 3, 3, 9, 0, 123], [6, 3, 6, 3, 4, 4, 10, 1, 124])
]

/-- Run the tests for incr_list -/
#eval incr_list_tests.all (λ (input, expected) => incr_list input == expected)

/-- Specification for incr_list -/
def incr_list_spec (l : List Int) : List Int :=
  l.map (λ e => e + 1)

/-- Precondition for incr_list -/
def incr_list_pre (_l : List Int) : Prop := True

/-- Postcondition for incr_list -/
def incr_list_post (l : List Int) (result : List Int) : Prop :=
  result = incr_list_spec l

/-- Correctness theorem for incr_list -/
theorem incr_list_correct (l : List Int) :
  incr_list_pre l → incr_list_post l (incr_list l) := by
  intro _
  unfold incr_list_post
  unfold incr_list_spec
  unfold incr_list
  simp
  sorry
