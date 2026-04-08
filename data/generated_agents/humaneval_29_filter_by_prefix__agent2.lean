import Lean
import Std

namespace VeriBench.HumanEval.Problem29

/-- Filter an input list of strings only for ones that start with a given prefix. -/
def filter_by_prefix (strings : List String) (prefix : String) : List String :=
  strings.filter (String.isPrefixOf prefix)

/-- Tests for filter_by_prefix -/
def filter_by_prefix_tests : IO Unit := do
  assert $ filter_by_prefix [] "john" == []
  assert $ filter_by_prefix ["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"] "xxx" == ["xxx", "xxxAAA", "xxx"]
  assert $ filter_by_prefix [] "a" == []
  assert $ filter_by_prefix ["abc", "bcd", "cde", "array"] "a" == ["abc", "array"]
  IO.println "All tests passed!"

/-- Precondition for filter_by_prefix -/
def filter_by_prefix_pre (_strings : List String) (_prefix : String) : Prop :=
  True

/-- Postcondition for filter_by_prefix -/
def filter_by_prefix_post (strings : List String) (prefix : String) (result : List String) : Prop :=
  ∀ s, s ∈ result ↔ (s ∈ strings ∧ String.isPrefixOf prefix s)

/-- Correctness theorem for filter_by_prefix -/
theorem filter_by_prefix_correct (strings : List String) (prefix : String)
    (h_pre : filter_by_prefix_pre strings prefix) :
    filter_by_prefix_post strings prefix (filter_by_prefix strings prefix) := by
  intro s
  simp [filter_by_prefix, List.filter_eq]
  sorry

end VeriBench.HumanEval.Problem29
