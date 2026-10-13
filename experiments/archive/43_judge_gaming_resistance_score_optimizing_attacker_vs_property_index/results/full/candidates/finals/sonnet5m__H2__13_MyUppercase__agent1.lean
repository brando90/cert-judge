import Lean

/-! # Convert all lowercase letters in a string to uppercase

Lean strings model the string-valued inputs accepted by the source function.
The tagged input model below also records the source function's ValueError
behavior for values that are not strings.
-/

def pre (s : String) : Bool :=
  true

def post (s : String) (result : String) : Bool :=
  result == s.toUpper

def prog (s : String) : String :=
  s.toUpper

theorem prog_correct (s : String) (h : pre s) : post s (prog s) :=
  by simp [post, prog]

theorem pre_always_true (s : String) : pre s = true :=
  rfl

theorem prog_returns_uppercase (s : String) :
    prog s = s.toUpper :=
  rfl

theorem prog_satisfies_post (s : String) : post s (prog s) = true :=
  by simp [post, prog]

theorem post_iff_uppercase (s result : String) :
    post s result = true ↔ result = s.toUpper :=
  by simp [post]

theorem prog_preserves_already_uppercase (s : String)
    (h : s.toUpper = s) : prog s = s :=
  by simpa [prog] using h

theorem prog_idempotent (s : String) : prog (prog s) = prog s := by
  sorry

theorem prog_empty : prog "" = "" := by sorry

theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

theorem prog_fixed_point (s : String) :
    prog s = s ↔ s.toUpper = s := by
  rfl

/-! A small tagged model of the dynamically typed source interface. -/
inductive PythonInput where
  | text (value : String)
  | nonString (description : String)
  deriving Repr, DecidableEq

inductive PythonOutcome where
  | returned (value : String)
  | valueError
  deriving Repr, DecidableEq

def pythonModel (input : PythonInput) : PythonOutcome :=
  match input with
  | .text value => .returned (prog value)
  | .nonString _ => .valueError

def pythonPre (input : PythonInput) : Bool :=
  match input with
  | .text _ => true
  | .nonString _ => false

def pythonPost (input : PythonInput) (outcome : PythonOutcome) : Prop :=
  match input with
  | .text value => outcome = .returned (value.toUpper)
  | .nonString _ => outcome = .valueError

theorem pythonModel_returns_uppercase (s : String) :
    pythonModel (.text s) = .returned (s.toUpper) :=
  rfl

theorem pythonModel_rejects_nonString (description : String) :
    pythonModel (.nonString description) = .valueError :=
  rfl

theorem pythonModel_correct (input : PythonInput) :
    pythonPost input (pythonModel input) := by
  cases input <;> rfl

theorem pythonPre_iff_isText (input : PythonInput) :
    pythonPre input = true ↔ ∃ s, input = .text s := by
  cases input with
  | text s => simp [pythonPre]
  | nonString description => simp [pythonPre]

theorem pythonModel_nonString_violates_pre (description : String) :
    pythonPre (.nonString description) = false :=
  rfl

-- Tests
def test : IO Unit := do
  -- Basic and empty-string cases
  assert! (prog "hello" == "HELLO")
  assert! (prog "" == "")

  -- Lowercase letters are converted, while punctuation and digits remain.
  assert! (prog "abcdefghijklmnopqrstuvwxyz" == "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123" == "123")
  assert! (prog "a1b2c3" == "A1B2C3")
  assert! (prog "ABC!? 42" == "ABC!? 42")

  -- Non-string inputs are represented by the ValueError outcome.
  assert! (pythonModel (.nonString "None") == .valueError)
  assert! (pythonModel (.nonString "123") == .valueError)

  IO.println "All tests passed!"

#eval test
