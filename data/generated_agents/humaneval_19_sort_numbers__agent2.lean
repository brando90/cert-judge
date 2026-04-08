import Lean
import Std

/-- A mapping from number words to their integer values. -/
def valueMap (word : String) : Option Nat :=
  match word with
  | "zero" => some 0
  | "one" => some 1
  | "two" => some 2
  | "three" => some 3
  | "four" => some 4
  | "five" => some 5
  | "six" => some 6
  | "seven" => some 7
  | "eight" => some 8
  | "nine" => some 9
  | _ => none

/-- Check if a word is a valid number word. -/
def isValidNumberWord (word : String) : Bool :=
  match valueMap word with
  | some _ => true
  | none => false

/-- Input is a space-delimited string of numberals from 'zero' to 'nine'.
    Valid choices are 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight' and 'nine'.
    Return the string with numbers sorted from smallest to largest -/
def sortNumbers (numbers : String) : String :=
  let words := numbers.split (· == ' ')
  let validWords := words.filter (fun word => word != "" && isValidNumberWord word)
  let sortedWords := validWords.qsort (fun x y => 
    match valueMap x, valueMap y with
    | some vx, some vy => vx < vy
    | _, _ => false)
  String.intercalate " " sortedWords.toList

/-- Precondition: All words in the input string must be valid number words or empty strings. -/
def sortNumbers.pre (numbers : String) : Prop :=
  numbers.split (· == ' ').all (fun word => word == "" || isValidNumberWord word)

/-- Postcondition: The output is a space-delimited string of number words sorted by their numerical values. -/
def sortNumbers.post (numbers : String) (result : String) : Prop :=
  let inputWords := numbers.split (· == ' ')
  let validInputWords := inputWords.filter (fun word => word != "" && isValidNumberWord word)
  let outputWords := result.split (· == ' ')
  
  -- If input is empty or has only empty words, output should be empty
  (validInputWords.isEmpty → result = "") ∧
  
  -- Output words should be sorted by numerical value
  (¬validInputWords.isEmpty → 
    outputWords.size = validInputWords.size ∧
    outputWords.all isValidNumberWord ∧
    List.isSorted (outputWords.map (fun w => Option.get! (valueMap w))).toList (· ≤ ·))

/-- Correctness theorem: sortNumbers satisfies its specification. -/
theorem sortNumbers_correct (numbers : String) : 
  sortNumbers.pre numbers → sortNumbers.post numbers (sortNumbers numbers) := by
  sorry

/-- Tests for the sortNumbers function -/
def testSortNumbers : IO Unit := do
  IO.println s!"Test 1: {sortNumbers ""}"
  assert! (sortNumbers "" = "")
  
  IO.println s!"Test 2: {sortNumbers "three"}"
  assert! (sortNumbers "three" = "three")
  
  IO.println s!"Test 3: {sortNumbers "three five nine"}"
  assert! (sortNumbers "three five nine" = "three five nine")
  
  IO.println s!"Test 4: {sortNumbers "five zero four seven nine eight"}"
  assert! (sortNumbers "five zero four seven nine eight" = "zero four five seven eight nine")
  
  IO.println s!"Test 5: {sortNumbers "six five four three two one zero"}"
  assert! (sortNumbers "six five four three two one zero" = "zero one two three four five six")
  
  IO.println "All tests passed!"

#eval testSortNumbers
