import Lean
import Std.Data.List
import Std.Data.HashMap

namespace HumanEval19

def valueMap : Std.HashMap String Nat :=
  Std.HashMap.ofList [
    ("zero", 0),
    ("one", 1),
    ("two", 2),
    ("three", 3),
    ("four", 4),
    ("five", 5),
    ("six", 6),
    ("seven", 7),
    ("eight", 8),
    ("nine", 9)
  ]

/-- 
  Input is a space-delimited string of numberals from 'zero' to 'nine'.
  Valid choices are 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight' and 'nine'.
  Return the string with numbers sorted from smallest to largest
-/
def sortNumbers (numbers: String) : String :=
  if numbers = "" then
    ""
  else
    let words := numbers.split (· = ' ')
    let nonEmptyWords := words.filter (fun x => x ≠ "")
    let sortedWords := nonEmptyWords.qsort (fun x y => 
      match valueMap.find? x, valueMap.find? y with
      | some vx, some vy => vx ≤ vy
      | _, _ => false
    )
    String.intercalate " " sortedWords.toList

/-- Every word in the input is a valid number word -/
def validInput (s: String) : Prop :=
  if s = "" then
    True
  else
    let words := s.split (· = ' ')
    let nonEmptyWords := words.filter (fun x => x ≠ "")
    nonEmptyWords.all (fun w => valueMap.contains w)

/-- The output is a space-separated string of the same words sorted by their numeric values -/
def validOutput (input: String) (output: String) : Prop :=
  if input = "" then
    output = ""
  else
    let inputWords := (input.split (· = ' ')).filter (fun x => x ≠ "")
    let outputWords := (output.split (· = ' ')).filter (fun x => x ≠ "")
    
    -- Same set of words
    (inputWords.toList.toFinset = outputWords.toList.toFinset) ∧
    
    -- Words are sorted by numeric value
    outputWords.toList.isPairwiseLE (fun x y =>
      match valueMap.find? x, valueMap.find? y with
      | some vx, some vy => vx ≤ vy
      | _, _ => false
    )

theorem sortNumbers_correct (s: String) (h: validInput s) : 
  validOutput s (sortNumbers s) := by
  sorry

#eval sortNumbers ""
#eval sortNumbers "three"
#eval sortNumbers "three five nine"
#eval sortNumbers "five zero four seven nine eight"
#eval sortNumbers "six five four three two one zero"

def test : IO Unit := do
  IO.println "Running tests..."
  assert (sortNumbers "" = "")
  assert (sortNumbers "three" = "three")
  assert (sortNumbers "three five nine" = "three five nine")
  assert (sortNumbers "five zero four seven nine eight" = "zero four five seven eight nine")
  assert (sortNumbers "six five four three two one zero" = "zero one two three four five six")
  IO.println "All tests passed!"

end HumanEval19
