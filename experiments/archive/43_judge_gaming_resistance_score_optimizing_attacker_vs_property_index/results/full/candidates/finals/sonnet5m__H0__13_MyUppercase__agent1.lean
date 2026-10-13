import Lean

/-! # Convert all lowercase letters in a string to uppercase

Edge cases:
- Empty string returns empty string.
- Non-alphabetic characters remain unchanged.
- The function raises ValueError if input is not a string.
-/

def pre (s : String) : Bool :=
  true

def post (s : String) (result : String) : Bool :=
  result == s.toUpper

def prog (s : String) : String :=
  s.toUpper

theorem prog_correct (s : String) (h : pre s) : post s (prog s) :=
  by simp [post, prog]

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

/-! A dynamically typed input model makes the non-string precondition and its
ValueError behavior explicit. A `PythonValue.string` is a string input; the
other constructors represent non-string inputs. -/

inductive PythonValue where
  | string (s : String)
  | none
  | integer (n : Int)
  deriving Repr, DecidableEq

inductive PythonError where
  | valueError
  deriving Repr, DecidableEq

def pythonPre (input : PythonValue) : Bool :=
  match input with
  | .string _ => true
  | _ => false

def guardedProg (input : PythonValue) : Except PythonError String :=
  match input with
  | .string s => .ok (prog s)
  | .none => .error .valueError
  | .integer _ => .error .valueError

def pythonPost (input : PythonValue) (result : Except PythonError String) : Bool :=
  match input, result with
  | .string s, .ok output => output == s.toUpper
  | .none, .error .valueError => true
  | .integer _, .error .valueError => true
  | _, _ => false

theorem pre_always_true (s : String) : pre s = true := rfl

theorem pythonPre_iff_string (input : PythonValue) :
    pythonPre input = true ↔ ∃ s, input = .string s := by
  cases input <;> simp [pythonPre]

theorem guardedProg_string (s : String) :
    guardedProg (.string s) = .ok (s.toUpper) := rfl

theorem guardedProg_none :
    guardedProg .none = .error .valueError := rfl

theorem guardedProg_integer (n : Int) :
    guardedProg (.integer n) = .error .valueError := rfl

theorem guardedProg_correct (input : PythonValue) :
    pythonPost input (guardedProg input) = true := by
  cases input <;> simp [pythonPost, guardedProg, prog]

theorem guardedProg_succeeds_iff_precondition (input : PythonValue) :
    (∃ output, guardedProg input = .ok output) ↔ pythonPre input = true := by
  cases input <;> simp [guardedProg, pythonPre]

theorem pythonPost_rejects_success_for_none (output : String) :
    pythonPost .none (.ok output) = false := rfl

theorem pythonPost_rejects_success_for_integer (n : Int) (output : String) :
    pythonPost (.integer n) (.ok output) = false := rfl
