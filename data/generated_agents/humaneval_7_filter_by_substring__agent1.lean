import Lean.Data.HashMap
import Mathlib.Tactic
import Mathlib.Data.List.Basic

namespace VeriBench

/-- 
  `filter_by_substring` filters an input list of strings only for ones that contain given substring.
-/
def filter_by_substring (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

/-- Specification for `filter_by_substring`. -/
def filter_by_substring_spec (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

/-- Tests for `filter_by_substring`. -/
def filter_by_substring_tests : List (List String × String × List String) := [
  ([], "john", []),
  (["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"], "xxx", ["xxx", "xxxAAA", "xxx"]),
  (["xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"], "xx", ["xxx", "aaaxxy", "xxxAAA", "xxx"]),
  (["grunt", "trumpet", "prune", "gruesome"], "run", ["grunt", "prune"])
]

theorem filter_by_substring_correct (strings : List String) (substring : String) :
  filter_by_substring strings substring = filter_by_substring_spec strings substring := by
  rfl

/-- Run the tests. -/
def run_filter_by_substring_tests : IO Unit := do
  for (input1, input2, expected) in filter_by_substring_tests do
    let result := filter_by_substring input1 input2
    if result != expected then
      throw (IO.userError s!"Test failed: filter_by_substring {input1} {input2} = {result}, but expected {expected}")
    else
      IO.println s!"Test passed: filter_by_substring {input1} {input2} = {expected}"

#eval run_filter_by_substring_tests

end VeriBench
