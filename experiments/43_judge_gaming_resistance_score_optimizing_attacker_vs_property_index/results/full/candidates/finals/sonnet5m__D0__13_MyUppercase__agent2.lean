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

/-- Every Lean `String` satisfies the input precondition. -/
theorem preCondition_true (s : String) : preCondition s = true := rfl

/-- The implementation agrees with Lean's string uppercase operation. -/
theorem progCorrect (s : String) (h : preCondition s) :
  prog s = s.toUpper := by rfl

/-- The uppercase operation is stable when applied a second time. -/
theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

/-- Empty input remains empty. -/
theorem prog_empty : prog "" = "" := by
  native_decide

/-- Representative lowercase inputs are converted to uppercase. -/
theorem prog_lowercase_examples :
    prog "hello" = "HELLO" ∧
    prog "abc" = "ABC" ∧
    prog "good morning" = "GOOD MORNING" := by
  native_decide

/-- Uppercase letters and punctuation are preserved by the conversion. -/
theorem prog_mixed_example :
    prog "Hello, World!" = "HELLO, WORLD!" := by
  native_decide

/-- Digits and punctuation are unaffected while lowercase letters are converted. -/
theorem prog_nonletters_example :
    prog "123!?" = "123!?" ∧
    prog "123abc" = "123ABC" := by
  native_decide

/-- Strings containing only uppercase ASCII letters are unchanged. -/
theorem prog_already_upper :
    prog "LEAN 4!" = "LEAN 4!" := by
  native_decide

/-- Spaces and punctuation are retained while lowercase letters are converted. -/
theorem prog_spaces_and_punctuation :
    prog "a b-c!" = "A B-C!" := by
  native_decide

/-- Applying the operation to a concatenation is the same as applying it
to each part and concatenating the results. -/
theorem prog_append (a b : String) :
    prog (a ++ b) = prog a ++ prog b := by
  sorry

/-- A string is unchanged by the program exactly when it is a fixed point
of Lean's uppercase operation. -/
theorem prog_fixed_iff (s : String) :
    prog s = s ↔ s.toUpper = s := Iff.rfl

/-- Inputs already fixed by uppercase conversion are left unchanged. -/
theorem prog_fixed (s : String) (h : s.toUpper = s) :
    prog s = s := by
  simpa [prog] using h

/-- Every lowercase ASCII letter is converted in a representative sequence. -/
theorem prog_all_lowercase_letters :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

/-- Mixed ASCII letters, digits, whitespace, and punctuation are handled
together without changing the nonletters. -/
theorem prog_mixed_characters :
    prog "lean 4: abc-xyz! 09" = "LEAN 4: ABC-XYZ! 09" := by
  native_decide

/-- The result of the conversion is itself unchanged by uppercase conversion. -/
theorem prog_output_is_uppercase (s : String) :
    (prog s).toUpper = prog s := by
  sorry

/-- Inputs used to model the dynamically typed Python interface. -/
inductive TaskInput where
  | string (value : String)
  | none
  | integer (value : Int)
  deriving DecidableEq, Repr

/-- The Python precondition, expressed over string and non-string inputs. -/
def taskPrecondition : TaskInput → Bool
  | .string _ => true
  | .none => false
  | .integer _ => false

/-- The exception raised for an input that is not a string. -/
inductive TaskException where
  | valueError
  deriving DecidableEq, Repr

/-- A result-valued model of the Python program, including its precondition
failure behavior. -/
def checkedProg : TaskInput → Except TaskException String
  | .string s => .ok (prog s)
  | .none => .error .valueError
  | .integer _ => .error .valueError

/-- The modeled precondition accepts exactly the string inputs. -/
theorem taskPrecondition_iff (x : TaskInput) :
    taskPrecondition x = true ↔ ∃ s, x = .string s := by
  cases x <;> simp [taskPrecondition]

/-- A valid string input is processed by the same uppercase operation. -/
theorem checkedProg_string (s : String) :
    checkedProg (.string s) = .ok (prog s) := rfl

/-- `None` violates the precondition and produces a ValueError result. -/
theorem checkedProg_none :
    checkedProg .none = .error .valueError := rfl

/-- An integer violates the precondition and produces a ValueError result. -/
theorem checkedProg_integer (n : Int) :
    checkedProg (.integer n) = .error .valueError := rfl

/-- The checked program succeeds exactly on inputs satisfying its precondition. -/
theorem checkedProg_succeeds_iff (x : TaskInput) :
    (∃ s, checkedProg x = .ok s) ↔ taskPrecondition x = true := by
  cases x <;> simp [checkedProg, taskPrecondition]

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == "HELLO")

  -- Edge unit test
  assert! (prog "" == "")

  -- Mixed case and non-alphabetic characters
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123abc" == "123ABC")
  assert! (prog "123!?" == "123!?")
  assert! (prog "already UPPER" == "ALREADY UPPER")
  assert! (prog " " == " ")
  assert! (prog "abcdefghijklmnopqrstuvwxyz" == "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
  assert! (prog "lean 4: abc-xyz! 09" == "LEAN 4: ABC-XYZ! 09")

  IO.println "All tests passed."

end ToUpper
