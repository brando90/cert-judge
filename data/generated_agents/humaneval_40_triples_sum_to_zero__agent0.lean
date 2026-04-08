import Mathlib.Data.List.Basic
import Mathlib.Tactic

namespace VeriBench

/-- 
  `triples_sum_to_zero` takes a list of integers as an input.
  It returns true if there are three distinct elements in the list that
  sum to zero, and false otherwise.
-/
def triples_sum_to_zero (l : List Int) : Bool :=
  let n := l.length
  List.range n |> List.any fun i =>
    List.range (n - (i + 1)) |> List.any fun j' =>
      let j := j' + (i + 1)
      List.range (n - (j + 1)) |> List.any fun k' =>
        let k := k' + (j + 1)
        l[i]! + l[j]! + l[k]! = 0

/-- Specification for `triples_sum_to_zero` -/
def triples_sum_to_zero_spec (l : List Int) : Bool :=
  ∃ i j k, i < l.length ∧ j < l.length ∧ k < l.length ∧ 
           i ≠ j ∧ i ≠ k ∧ j ≠ k ∧
           l[i]! + l[j]! + l[k]! = 0

/-- Tests for `triples_sum_to_zero` -/
def triples_sum_to_zero_tests : List (List Int × Bool) := [
  ([1, 3, 5, 0], false),
  ([1, 3, 5, -1], false),
  ([1, 3, -2, 1], true),
  ([1, 2, 3, 7], false),
  ([1, 2, 5, 7], false),
  ([2, 4, -5, 3, 9, 7], true),
  ([1], false),
  ([1, 3, 5, -100], false),
  ([100, 3, 5, -100], false)
]

/-- Run the tests for `triples_sum_to_zero` -/
theorem triples_sum_to_zero_test : triples_sum_to_zero_tests.all (fun (input, expected) => 
  triples_sum_to_zero input = expected) := by
  simp [triples_sum_to_zero_tests]
  decide

/-- 
  Correctness theorem: `triples_sum_to_zero` satisfies its specification
-/
theorem triples_sum_to_zero_correct (l : List Int) : 
  triples_sum_to_zero l = triples_sum_to_zero_spec l := by
  sorry

end VeriBench
