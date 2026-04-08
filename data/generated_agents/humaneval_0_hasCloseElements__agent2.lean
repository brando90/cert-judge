import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic

/--
Check if in given list of numbers, are any two numbers closer to each other
than given threshold.
-/
def hasCloseElements (numbers : List Float) (threshold : Float) : Bool :=
  let rec check (idx : Nat) (numbers : List Float) : Bool :=
    match numbers with
    | [] => false
    | elem :: rest =>
      let rec checkAgainst (idx2 : Nat) (others : List Float) : Bool :=
        match others with
        | [] => check (idx + 1) rest
        | elem2 :: rest2 =>
          if idx != idx2 then
            let distance := Float.abs (elem - elem2)
            if distance < threshold then
              true
            else
              checkAgainst (idx2 + 1) rest2
          else
            checkAgainst (idx2 + 1) rest2
      checkAgainst 0 numbers
  check 0 numbers

/--
Specification: Returns true if and only if there exist two distinct indices i and j
such that |numbers[i] - numbers[j]| < threshold.
-/
def hasCloseElementsSpec (numbers : List Float) (threshold : Float) : Bool :=
  ∃ i j, i < numbers.length ∧ j < numbers.length ∧ i ≠ j ∧ 
         Float.abs (numbers.get! i - numbers.get! j) < threshold

/--
Test cases for the hasCloseElements function.
-/
def hasCloseElementsTests : List (List Float × Float × Bool) := [
  -- Original tests
  ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3, true),
  ([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05, false),
  ([1.0, 2.0, 5.9, 4.0, 5.0], 0.95, true),
  ([1.0, 2.0, 5.9, 4.0, 5.0], 0.8, false),
  ([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1, true),
  ([1.1, 2.2, 3.1, 4.1, 5.1], 1.0, true),
  ([1.1, 2.2, 3.1, 4.1, 5.1], 0.5, false),
  
  -- Edge cases
  ([], 0.1, false),
  ([1.5], 0.1, false),
  ([3.14, 3.14], 0.1, true),
  ([3.14, 3.14], 0.0, false),
  ([100.0, 200.0], 999.9, true),
  ([1.0, 1.00000001], 0.00001, true),
  ([1.0, 1.0002], 0.00001, false)
]

/--
Run all the test cases and check that the function returns the expected results.
-/
def runHasCloseElementsTests : IO Unit :=
  let results := hasCloseElementsTests.map (fun (test : List Float × Float × Bool) =>
    let (numbers, threshold, expected) := test
    let actual := hasCloseElements numbers threshold
    (actual == expected, numbers, threshold, expected, actual))
  
  let failures := results.filter (fun (r, _, _, _, _) => !r)
  
  if failures.isEmpty then
    IO.println "All tests passed!"
  else
    for (_, numbers, threshold, expected, actual) in failures do
      IO.println s!"Test failed: hasCloseElements {numbers} {threshold} returned {actual}, expected {expected}"

/--
The implementation satisfies the specification.
-/
theorem hasCloseElements_correct (numbers : List Float) (threshold : Float) :
  hasCloseElements numbers threshold = hasCloseElementsSpec numbers threshold := by
  sorry

/--
Main entry point to run the tests.
-/
def main : IO Unit :=
  runHasCloseElementsTests
