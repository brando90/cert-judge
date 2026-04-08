import VeriBench.Common

namespace HumanEval12

/--
Out of list of strings, return the longest one. Return the first one in case of multiple
strings of the same length. Return None in case the input list is empty.
-/
def longest (strings : List String) : Option String :=
  if strings.isEmpty then
    none
  else
    let maxlen := strings.map String.length |>.maximum?.get!
    strings.find? (fun s => s.length = maxlen)

/-- Specification for `longest` -/
def longestSpec (strings : List String) : Option String :=
  if strings.isEmpty then
    none
  else
    let maxlen := strings.map String.length |>.maximum?.get!
    strings.find? (fun s => s.length = maxlen)

/-- Precondition for `longest` -/
def longestPre (strings : List String) : Prop := True

/-- Postcondition for `longest` -/
def longestPost (strings : List String) (result : Option String) : Prop :=
  result = longestSpec strings

/-- Correctness theorem for `longest` -/
theorem longest_correct (strings : List String) (h : longestPre strings) :
  longestPost strings (longest strings) := by
  simp [longestPost, longestSpec, longest]
  sorry

/-- Tests for `longest` -/
def tests : List (List String × Option String) := [
  ([], none),
  (["x", "y", "z"], "x"),
  (["x", "yyy", "zzzz", "www", "kkkk", "abc"], "zzzz"),
  (["a", "b", "c"], "a"),
  (["a", "bb", "ccc"], "ccc")
]

/-- Run the tests -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := longest input
    if result != expected then
      throw (IO.userError s!"Test failed: longest {input} = {result}, expected {expected}")
  IO.println "All tests passed!"

end HumanEval12
