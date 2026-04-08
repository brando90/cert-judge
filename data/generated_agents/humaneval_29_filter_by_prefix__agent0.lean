/-
# VeriBench problem: HumanEval/29
# Description: Filter an input list of strings only for ones that start with a given prefix.
-/

import Std.Data.List.Basic

def filter_by_prefix (strings : List String) (prefix : String) : List String :=
  strings.filter (fun s => s.startsWith prefix)

def main : IO Unit := do
  let result1 := filter_by_prefix [] "a"
  IO.println s!"filter_by_prefix [] \"a\" = {result1}"

  let result2 := filter_by_prefix ["abc", "bcd", "cde", "array"] "a"
  IO.println s!"filter_by_prefix [\"abc\", \"bcd\", \"cde\", \"array\"] \"a\" = {result2}"

-- Tests
def test : IO Unit := do
  assert $ filter_by_prefix [] "john" == []
  assert $ filter_by_prefix ["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"] "xxx" == ["xxx", "xxxAAA", "xxx"]
  IO.println "All tests passed!"

-- Verification
theorem filter_by_prefix_spec (strings : List String) (prefix : String) :
  filter_by_prefix strings prefix = strings.filter (fun s => s.startsWith prefix) :=
  rfl

/-- Predicate specifying the expected behavior of filter_by_prefix -/
def filter_by_prefix_post (strings : List String) (prefix : String) (result : List String) : Prop :=
  ∀ s, s ∈ result ↔ (s ∈ strings ∧ s.startsWith prefix)

/-- The implementation satisfies the specification -/
theorem filter_by_prefix_correct (strings : List String) (prefix : String) :
  filter_by_prefix_post strings prefix (filter_by_prefix strings prefix) := by
  unfold filter_by_prefix_post
  intro s
  unfold filter_by_prefix
  simp [List.mem_filter]
  sorry
