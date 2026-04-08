import Std.Data.List.Basic

/--
Find how many times a given substring can be found in the original string. Count overlapping cases.
-/
def howManyTimes (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    0
  else if substring.length > string.length then
    0
  else
    let rec countOccurrences (startPos : Nat) (acc : Nat) : Nat :=
      if startPos + substring.length > string.length then
        acc
      else if string.extract startPos (startPos + substring.length) == substring then
        countOccurrences (startPos + 1) (acc + 1)
      else
        countOccurrences (startPos + 1) acc
    
    countOccurrences 0 0

/-- Specification: howManyTimes counts the number of occurrences of substring in string, including overlapping occurrences. -/
def howManyTimesSpec (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    0
  else
    (List.range (string.length - substring.length + 1)).foldl
      (fun count i => if string.extract i (i + substring.length) == substring then count + 1 else count)
      0

/-- Precondition: substring is not empty. -/
def howManyTimesPre (string : String) (substring : String) : Prop :=
  true

/-- Postcondition: the result is the number of occurrences of substring in string. -/
def howManyTimesPost (string : String) (substring : String) (result : Nat) : Prop :=
  result = howManyTimesSpec string substring

theorem howManyTimes_correct (string : String) (substring : String) :
  howManyTimesPre string substring →
  howManyTimesPost string substring (howManyTimes string substring) :=
  sorry

/-- Test cases for howManyTimes -/
def howManyTimes_test : IO Unit := do
  assert! (howManyTimes "" "x" = 0)
  assert! (howManyTimes "xyxyxyx" "x" = 4)
  assert! (howManyTimes "cacacacac" "cac" = 4)
  assert! (howManyTimes "john doe" "john" = 1)
  assert! (howManyTimes "aaa" "a" = 3)
  assert! (howManyTimes "aaaa" "aa" = 3)
  IO.println "All tests passed!"
