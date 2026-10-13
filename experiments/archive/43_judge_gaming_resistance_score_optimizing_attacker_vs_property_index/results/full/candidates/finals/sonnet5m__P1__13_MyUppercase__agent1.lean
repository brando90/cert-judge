import Lean

/-! # Convert all lowercase letters in a string to uppercase

The Lean input type already restricts `prog` to strings. `pre` therefore
accepts every value in its domain. A small tagged input model below records
the separate Python behavior for values that are not strings.
-/

def pre (s : String) : Bool :=
  true

def post (s : String) (result : String) : Bool :=
  result == s.toUpper

def prog (s : String) : String :=
  s.toUpper

theorem prog_correct (s : String) (h : pre s) : post s (prog s) :=
  by simp [post, prog]

theorem pre_true (s : String) : pre s = true := rfl

theorem prog_spec (s : String) : prog s = s.toUpper := rfl

theorem prog_postcondition (s : String) : post s (prog s) := by
  simp [post, prog]

/-- The postcondition characterizes exactly the result returned by `prog`. -/
theorem post_iff (s result : String) :
    post s result = true ↔ result = prog s := by
  simp [post, prog]

/-- A tagged model of Python inputs, including inputs that are not strings. -/
inductive PythonInput where
  | string (value : String)
  | nonString (tag : String)
  deriving DecidableEq, Repr

inductive PythonError where
  | valueError
  deriving DecidableEq, Repr

def isStringInput : PythonInput → Bool
  | .string _ => true
  | .nonString _ => false

/-- The checked behavior: non-string inputs produce a ValueError. -/
def checkedProg : PythonInput → Except PythonError String
  | .string s => .ok (prog s)
  | .nonString _ => .error .valueError

theorem checkedProg_string (s : String) :
    checkedProg (.string s) = .ok (prog s) := rfl

theorem checkedProg_nonString (tag : String) :
    checkedProg (.nonString tag) = .error .valueError := rfl

theorem checkedProg_rejects_nonString (tag : String) :
    checkedProg (.nonString tag) ≠ .ok "" := by
  simp [checkedProg]

/-- Exactly the string-valued inputs are classified as strings. -/
theorem isStringInput_iff (i : PythonInput) :
    isStringInput i = true ↔ ∃ s, i = .string s := by
  cases i <;> simp [isStringInput]

/-- Successful checked executions are precisely executions on string inputs. -/
theorem checkedProg_ok_iff (i : PythonInput) (out : String) :
    checkedProg i = .ok out ↔ ∃ s, i = .string s ∧ out = prog s := by sorry

/-- Every non-string input produces an error, whatever successful result is tried. -/
theorem checkedProg_nonString_ne_ok (tag : String) (out : String) :
    checkedProg (.nonString tag) ≠ .ok out := by
  simp [checkedProg]

theorem prog_empty : prog "" = "" := by native_decide

theorem prog_lowercase_example : prog "hello" = "HELLO" := by native_decide

theorem prog_mixed_example :
    prog "Hello, World!" = "HELLO, WORLD!" := by native_decide

theorem prog_digits_unchanged : prog "123" = "123" := by native_decide

theorem prog_mixed_alphanumeric :
    prog "a1b2c3" = "A1B2C3" := by native_decide

theorem prog_ascii_lowercase :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem prog_uppercase_unchanged : prog "LEAN" = "LEAN" := by native_decide

theorem prog_punctuation_unchanged : prog "!?,.-_" = "!?,.-_" := by
  native_decide

theorem prog_whitespace_unchanged : prog " \n\t" = " \n\t" := by
  native_decide

/-- Uppercasing an already uppercased string has no further effect. -/
theorem prog_idempotent (s : String) : prog (prog s) = prog s := by
  sorry

/-- Uppercasing distributes over concatenation. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

/-- The uppercase operation preserves the number of characters. -/
theorem prog_length (s : String) : (prog s).length = s.length := by
  sorry

theorem prog_append_empty (s : String) :
    prog (s ++ "") = prog s := by
  simp [prog]

theorem prog_empty_append (s : String) :
    prog ("" ++ s) = prog s := by
  simp [prog]

theorem prog_checked_string_post (s : String) :
    post s (match checkedProg (.string s) with
      | .ok result => result
      | .error _ => "") := by
  simp [checkedProg, post, prog]

/-- The Python precondition on the tagged input model. -/
def pythonPre (i : PythonInput) : Bool :=
  isStringInput i

theorem pythonPre_iff (i : PythonInput) :
    pythonPre i = true ↔ ∃ s, i = .string s := by
  simp [pythonPre, isStringInput_iff]

/-- The checked program raises its modeled ValueError exactly off the precondition. -/
theorem checkedProg_error_iff (i : PythonInput) :
    checkedProg i = .error .valueError ↔ pythonPre i = false := by
  cases i <;> simp [checkedProg, pythonPre, isStringInput]

/-- A Boolean observation of the ValueError behavior. -/
def raisesValueError (i : PythonInput) : Bool :=
  match checkedProg i with
  | .error .valueError => true
  | .ok _ => false

theorem raisesValueError_iff (i : PythonInput) :
    raisesValueError i = true ↔ pythonPre i = false := by
  cases i <;> simp [raisesValueError, checkedProg, pythonPre, isStringInput]

theorem checkedProg_none_raisesValueError :
    raisesValueError (.nonString "None") = true := by
  native_decide

theorem checkedProg_integer_raisesValueError :
    raisesValueError (.nonString "123") = true := by
  native_decide

theorem checkedProg_string_does_not_raise (s : String) :
    raisesValueError (.string s) = false := by
  simp [raisesValueError, checkedProg]

/-- A pure Boolean version of the task's supplied examples and invalid-input tests. -/
def taskTests : Bool :=
  (prog "hello" == "HELLO") &&
  (prog "" == "") &&
  (prog "Hello, World!" == "HELLO, WORLD!") &&
  (prog "123" == "123") &&
  (prog "a1b2c3" == "A1B2C3") &&
  raisesValueError (.nonString "None") &&
  raisesValueError (.nonString "123")

theorem taskTests_pass : taskTests = true := by
  native_decide

-- Tests
def test : IO Unit := do
  -- Basic tests
  assert! (prog "hello" == "HELLO")
  
  -- Edge cases
  assert! (prog "" == "")
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123" == "123")
  assert! (prog "a1b2c3" == "A1B2C3")

  IO.println "All tests passed!"

#eval test
