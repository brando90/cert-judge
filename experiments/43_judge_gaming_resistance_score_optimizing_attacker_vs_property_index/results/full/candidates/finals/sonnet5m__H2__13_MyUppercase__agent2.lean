import VeriBench

namespace ToUpper

def preCondition (s : String) : Bool := true

/-- Convert all lowercase letters in a string to uppercase.

Edge cases:
- Empty string returns empty string.
- Non-alphabetic characters remain unchanged.
-/
def prog (s : String) : String :=
  s.toUpper

/-- The required output for a string input is its uppercase form. -/
def postCondition (input output : String) : Prop :=
  output = input.toUpper

theorem preConditionAlways (s : String) : preCondition s = true := by
  rfl

theorem progSatisfiesPostCondition (s : String) :
    postCondition s (prog s) := by
  rfl

theorem progCorrect (s : String) (h : preCondition s) :
    postCondition s (prog s) := by
  rfl

theorem prog_eq_toUpper (s : String) :
    prog s = s.toUpper := by
  rfl

theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

theorem prog_empty :
    prog "" = "" := by sorry

theorem prog_hello :
    prog "hello" = "HELLO" := by sorry

theorem prog_mixed_case :
    prog "Hello, World!" = "HELLO, WORLD!" := by sorry

theorem prog_digits_and_letters :
    prog "123abc" = "123ABC" := by sorry

theorem prog_non_alphabetic_unchanged :
    prog "123!?" = "123!?" := by sorry

/-- Uppercasing distributes over concatenation. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

/-- A string is unchanged by the program exactly when it is already uppercase. -/
theorem prog_fixedPoint_iff (s : String) :
    prog s = s ↔ s.toUpper = s := by
  rfl

/-- The program's output is itself a fixed point of uppercasing. -/
theorem prog_output_fixedPoint (s : String) :
    prog (prog s) = prog s := by
  exact prog_idempotent s

/-- Equal inputs always have equal outputs. -/
theorem prog_congruent {s t : String} (h : s = t) :
    prog s = prog t := by
  cases h
  rfl

/-- For inputs in the Lean `String` domain, the precondition is always satisfied.
    Non-string Python inputs are modeled separately below. -/
inductive PythonInput where
  | string (value : String)
  | nonString
  deriving DecidableEq, Repr

inductive PythonValueError where
  | requireString
  deriving DecidableEq, Repr

def pythonPreCondition : PythonInput → Bool
  | .string _ => true
  | .nonString => false

/-- A typed model of the wrapper behavior, including its non-string error path. -/
def checkedProg : PythonInput → Except PythonValueError String
  | .string s => .ok (prog s)
  | .nonString => .error .requireString

theorem pythonPreCondition_string (s : String) :
    pythonPreCondition (.string s) = true := by
  rfl

theorem pythonPreCondition_nonString :
    pythonPreCondition .nonString = false := by
  rfl

theorem checkedProg_string (s : String) :
    checkedProg (.string s) = .ok (s.toUpper) := by
  rfl

theorem checkedProg_nonString :
    checkedProg .nonString = .error .requireString := by
  rfl

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == "HELLO")

  -- Edge unit test
  assert! (prog "" == "")

  -- Mixed case and non-alphabetic characters
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123abc" == "123ABC")

  IO.println "All tests passed."

end ToUpper
