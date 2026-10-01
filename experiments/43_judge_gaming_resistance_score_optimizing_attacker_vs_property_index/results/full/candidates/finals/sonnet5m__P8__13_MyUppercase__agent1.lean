import Lean

/-! # Convert all lowercase letters in a string to uppercase

Empty strings remain empty, and characters not changed by uppercasing are
preserved. Lean's `String` type represents only string inputs; a small
`Except`-based model below also records the Python `ValueError` behavior for
non-string inputs.
-/

def pre (s : String) : Bool :=
  true

def post (s : String) (result : String) : Bool :=
  result == s.toUpper

def prog (s : String) : String :=
  s.toUpper

theorem prog_correct (s : String) (h : pre s) : post s (prog s) :=
  by simp [post, prog]

theorem pre_holds_for_every_string (s : String) : pre s = true :=
  by simp [pre]

theorem post_iff_uppercase (s result : String) :
    post s result = true ↔ result = s.toUpper := by
  simp [post]

theorem prog_eq_toUpper (s : String) : prog s = s.toUpper :=
  rfl

theorem prog_empty : prog "" = "" := by sorry

theorem prog_hello : prog "hello" = "HELLO" := by sorry

theorem prog_mixed_case :
    prog "Hello, World!" = "HELLO, WORLD!" := by sorry

theorem prog_nonalphabetic_unchanged :
    prog "123 !?" = "123 !?" := by sorry

theorem prog_mixed_alphanumeric :
    prog "a1b2c3" = "A1B2C3" := by sorry

theorem prog_uppercase_is_fixed (s : String) (h : s.toUpper = s) :
    prog s = s := by
  simpa [prog] using h

theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

/-- Inputs used to model the dynamically typed Python interface. -/
inductive PythonInput where
  | string (value : String)
  | integer (value : Int)
  | none
  deriving DecidableEq, Repr

/-- The exception category raised by the Python program on an invalid input. -/
inductive PythonError where
  | valueError
  deriving DecidableEq, Repr

/-- A typed model of the Python wrapper: strings succeed, other inputs fail. -/
def runPython (input : PythonInput) : Except PythonError String :=
  match input with
  | .string s => .ok (prog s)
  | .integer _ => .error .valueError
  | .none => .error .valueError

theorem runPython_string (s : String) :
    runPython (.string s) = .ok (prog s) :=
  rfl

theorem runPython_integer_raises (n : Int) :
    runPython (.integer n) = .error .valueError :=
  rfl

theorem runPython_none_raises :
    runPython .none = .error .valueError :=
  rfl

theorem runPython_rejects_nonstrings (input : PythonInput)
    (h : ∀ s, input ≠ .string s) :
    runPython input = .error .valueError := by
  cases input with
  | string s => exact False.elim (h s rfl)
  | integer n => rfl
  | none => rfl

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
