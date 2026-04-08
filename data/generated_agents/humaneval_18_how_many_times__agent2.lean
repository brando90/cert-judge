/-
# File: humaneval_18_how_many_times.lean
# HumanEval problem HumanEval/18
-/

def howManyTimes (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    if string.isEmpty then 0 else string.length + 1
  else
    let mut times := 0
    for i in [0:string.length - substring.length + 1] do
      if string.extract i (i + substring.length) == substring then
        times := times + 1
    times

/-- Find how many times a given substring can be found in the original string. Count overlapping cases. -/
def spec (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    if string.isEmpty then 0 else string.length + 1
  else
    let mut times := 0
    for i in [0:string.length - substring.length + 1] do
      if string.extract i (i + substring.length) == substring then
        times := times + 1
    times

theorem howManyTimes_spec (string : String) (substring : String) : 
  howManyTimes string substring = spec string substring := by
  sorry

def main : IO Unit := do
  let test1 := howManyTimes "" "x" == 0
  let test2 := howManyTimes "xyxyxyx" "x" == 4
  let test3 := howManyTimes "cacacacac" "cac" == 4
  let test4 := howManyTimes "john doe" "john" == 1
  let test5 := howManyTimes "" "a" == 0
  let test6 := howManyTimes "aaa" "a" == 3
  let test7 := howManyTimes "aaaa" "aa" == 3
  
  if test1 && test2 && test3 && test4 && test5 && test6 && test7 then
    IO.println "All tests passed!"
  else
    IO.println "Some tests failed!"
