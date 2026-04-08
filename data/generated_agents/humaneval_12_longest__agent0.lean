/-
File: humaneval_12_longest.lean
-/

def longest (strings : List String) : Option String :=
  if strings.isEmpty then
    none
  else
    let maxlen := strings.foldl (fun acc s => max acc s.length) 0
    strings.find? (fun s => s.length == maxlen)

/-- longest returns the longest string from a list, or none if the list is empty.
    If there are multiple strings of the same length, it returns the first one. -/
theorem longest_spec (strings : List String) :
  longest strings =
    if strings.isEmpty then
      none
    else
      let maxlen := strings.foldl (fun acc s => max acc s.length) 0
      strings.find? (fun s => s.length == maxlen) :=
by sorry

/-- Tests for longest function -/
def longest_tests : IO Unit := do
  assert $ longest [] == none
  assert $ longest ["x", "y", "z"] == some "x"
  assert $ longest ["x", "yyy", "zzzz", "www", "kkkk", "abc"] == some "zzzz"
  IO.println "All tests passed!"

/-- Proof that longest returns none on empty list -/
theorem longest_empty : longest [] = none :=
by sorry

/-- Proof that longest returns the first string with maximum length -/
theorem longest_first_max (strings : List String) (h : strings ≠ []) :
  longest strings = strings.find? (fun s => s.length = strings.foldl (fun acc s => max acc s.length) 0) :=
by sorry

#eval longest_tests
