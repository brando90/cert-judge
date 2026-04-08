def filter_by_substring (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

/--
  `filter_by_substring` filters a list of strings to only include those that contain
  a given substring.
  
  Pre: None
  Post: The output list contains exactly those strings from the input list that contain
        the given substring.
-/
def filter_by_substring_spec (strings : List String) (substring : String) : List String :=
  strings.filter (fun x => x.contains substring)

theorem filter_by_substring_correct (strings : List String) (substring : String) :
  filter_by_substring strings substring = filter_by_substring_spec strings substring := by
  sorry

def main : IO Unit := do
  -- Test 1: Empty list
  let test1 := filter_by_substring [] "john"
  IO.println s!"Test 1: {test1}"
  assert! test1 == []

  -- Test 2: Filter by "xxx"
  let test2 := filter_by_substring ["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"] "xxx"
  IO.println s!"Test 2: {test2}"
  assert! test2 == ["xxx", "xxxAAA", "xxx"]

  -- Test 3: Filter by "xx"
  let test3 := filter_by_substring ["xxx", "asd", "aaaxxy", "john doe", "xxxAAA", "xxx"] "xx"
  IO.println s!"Test 3: {test3}"
  assert! test3 == ["xxx", "aaaxxy", "xxxAAA", "xxx"]

  -- Test 4: Filter by "run"
  let test4 := filter_by_substring ["grunt", "trumpet", "prune", "gruesome"] "run"
  IO.println s!"Test 4: {test4}"
  assert! test4 == ["grunt", "prune"]

  -- Test 5: Filter by "a"
  let test5 := filter_by_substring ["abc", "bacd", "cde", "array"] "a"
  IO.println s!"Test 5: {test5}"
  assert! test5 == ["abc", "bacd", "array"]

  IO.println "All tests passed!"
