import VeriBench

namespace FilterBySubstring

/-- Filter an input list of strings only for ones that contain given substring -/
def filter_by_substring (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

/-- Tests for filter_by_substring -/
def test : IO Unit := do
  assert $ filter_by_substring [] "john" == []
  assert $ filter_by_substring ["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"] "xxx" == ["xxx", "xxxAAA", "xxx"]
  assert $ filter_by_substring ["xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"] "xx" == ["xxx", "aaaxxy", "xxxAAA", "xxx"]
  assert $ filter_by_substring ["grunt", "trumpet", "prune", "gruesome"] "run" == ["grunt", "prune"]
  IO.println "All tests passed!"

/-- Specification for filter_by_substring -/
def filter_by_substring_spec (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

/-- Proof that filter_by_substring satisfies its specification -/
theorem filter_by_substring_correct (strings : List String) (substring : String) :
  filter_by_substring strings substring = filter_by_substring_spec strings substring := by
  simp [filter_by_substring, filter_by_substring_spec]

end FilterBySubstring
