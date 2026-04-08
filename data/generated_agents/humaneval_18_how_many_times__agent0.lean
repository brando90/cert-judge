/-
# File: humaneval_18_how_many_times.lean
# HumanEval problem HumanEval/18
-/

def how_many_times (string : String) (substring : String) : Nat :=
  let rec count (i : Nat) (acc : Nat) : Nat :=
    if i + substring.length > string.length then
      acc
    else if string.extract i (i + substring.length) == substring then
      count (i + 1) (acc + 1)
    else
      count (i + 1) acc
  count 0 0

/--
  Find how many times a given substring can be found in the original string. Count overlapping cases.
-/
def how_many_times_spec (string : String) (substring : String) : Nat :=
  let rec count (i : Nat) (acc : Nat) : Nat :=
    if i + substring.length > string.length then
      acc
    else if string.extract i (i + substring.length) == substring then
      count (i + 1) (acc + 1)
    else
      count (i + 1) acc
  count 0 0

theorem how_many_times_correct (string : String) (substring : String) :
  how_many_times string substring = how_many_times_spec string substring := by
  simp [how_many_times, how_many_times_spec]

def main : IO Unit := do
  -- Test cases
  assert! (how_many_times "" "x" == 0)
  assert! (how_many_times "xyxyxyx" "x" == 4)
  assert! (how_many_times "cacacacac" "cac" == 4)
  assert! (how_many_times "john doe" "john" == 1)
  
  -- Additional test cases from docstring
  assert! (how_many_times "" "a" == 0)
  assert! (how_many_times "aaa" "a" == 3)
  assert! (how_many_times "aaaa" "aa" == 3)
  
  IO.println "All tests passed!"
