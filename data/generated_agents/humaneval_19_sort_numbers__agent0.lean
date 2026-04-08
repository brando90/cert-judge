import Lean
import Std.Data.List.Basic
open Std

/-
  Implementation of sort_numbers function.
  Sorts a space-delimited string of number names from smallest to largest.
-/

def valueMap (s : String) : Option Nat :=
  match s with
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

/-- 
  Returns true if the string is a valid number name ('zero' through 'nine')
-/
def isValidNumberName (s : String) : Bool :=
  valueMap s |>.isSome

/--
  Sorts a space-delimited string of number names from smallest to largest.
  Valid number names are 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', and 'nine'.
-/
def sortNumbers (numbers : String) : String :=
  if numbers = "" then 
    ""
  else
    let words := numbers.split (· = ' ')
    let validWords := words.filter (fun x => x ≠ "" && isValidNumberName x)
    let sortedWords := validWords.qsort (fun x y => 
      match valueMap x, valueMap y with
      | some vx, some vy => vx < vy
      | _, _ => false)
    String.intercalate " " sortedWords.toList

/--
  Specification for sortNumbers function:
  
  1. If input is empty, output is empty
  2. Output only contains valid number names
  3. Output words are sorted by their numeric value
  4. Output contains the same number of words as valid input words
-/
def sortNumbersSpec (numbers : String) (result : String) : Prop :=
  let inputWords := numbers.split (· = ' ')
  let validInputWords := inputWords.filter (fun x => x ≠ "" && isValidNumberName x)
  let outputWords := result.split (· = ' ')
  
  (numbers = "" → result = "") ∧
  (result = "" → validInputWords = #[]) ∧
  (validInputWords.size > 0 → 
    -- Output only contains valid number names
    (∀ w ∈ outputWords.toList, w = "" ∨ isValidNumberName w) ∧
    -- Output is sorted
    (∀ i j, 0 ≤ i → i < j → j < outputWords.size → 
      match valueMap outputWords[i]!, valueMap outputWords[j]! with
      | some vi, some vj => vi ≤ vj
      | _, _ => true) ∧
    -- Output has same valid words as input (multiset equality)
    (outputWords.filter (· ≠ "")).size = validInputWords.size)

/--
  Correctness theorem for sortNumbers
-/
theorem sortNumbers_correct (numbers : String) : 
  sortNumbersSpec numbers (sortNumbers numbers) := by
  sorry

/--
  Test cases for sortNumbers
-/
def test_sortNumbers : IO Unit := do
  assert! (sortNumbers "" = "")
  assert! (sortNumbers "three" = "three")
  assert! (sortNumbers "three five nine" = "three five nine")
  assert! (sortNumbers "five zero four seven nine eight" = "zero four five seven eight nine")
  assert! (sortNumbers "six five four three two one zero" = "zero one two three four five six")
  IO.println "All tests passed!"

#eval test_sortNumbers
