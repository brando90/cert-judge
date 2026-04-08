import Lean
import Mathlib.Tactic

/--
Insert a number 'delimeter' between every two consecutive elements of input list `numbers`.
-/
def intersperse (numbers : List Int) (delimeter : Int) : List Int :=
  match numbers with
  | [] => []
  | [x] => [x]
  | x :: xs => x :: delimeter :: intersperse xs delimeter

/--
Specification for the intersperse function.
-/
def interspecSpec (numbers : List Int) (delimeter : Int) : List Int :=
  if numbers.isEmpty then
    []
  else
    let result := []
    let result := numbers.init.foldl (fun acc n => acc ++ [n, delimeter]) result
    result ++ [numbers.getLast (by
      intro h
      have : numbers.isEmpty = false := by assumption
      contradiction)]

/--
Precondition: Always true, no restrictions on inputs.
-/
def interspersePreCond (numbers : List Int) (delimeter : Int) : Prop :=
  True

/--
Postcondition: The output matches the specification.
-/
def interspersePostCond (numbers : List Int) (delimeter : Int) (result : List Int) : Prop :=
  result = interspecSpec numbers delimeter

/--
Correctness theorem for intersperse.
-/
theorem intersperse_correct (numbers : List Int) (delimeter : Int) :
  interspersePreCond numbers delimeter →
  interspersePostCond numbers delimeter (intersperse numbers delimeter) := by
  sorry

/--
Tests for the intersperse function.
-/
def tests : List (List Int × Int × List Int) := [
  ([], 7, []),
  ([5, 6, 3, 2], 8, [5, 8, 6, 8, 3, 8, 2]),
  ([2, 2, 2], 2, [2, 2, 2, 2, 2])
]

/--
Run the tests.
-/
def runTests : IO Unit := do
  for (input, delim, expected) in tests do
    let result := intersperse input delim
    if result != expected then
      throw (IO.userError s!"Test failed for input {input} and delimeter {delim}. Expected {expected}, got {result}")
    IO.println s!"Test passed for input {input} and delimeter {delim}"
  IO.println "All tests passed!"
