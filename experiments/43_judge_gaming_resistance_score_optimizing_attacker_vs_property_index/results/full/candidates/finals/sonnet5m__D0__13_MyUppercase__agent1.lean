import Lean

/-! # Convert all lowercase letters in a string to uppercase

Lean's `String` type represents string inputs, so every value accepted by
`prog` satisfies the Python task's string precondition. The program's result
is the built-in uppercase conversion.
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
  rfl

theorem prog_eq_toUpper (s : String) : prog s = s.toUpper :=
  rfl

theorem prog_satisfies_post (s : String) : post s (prog s) = true := by
  simp [post, prog]

/-! A small dynamic-input model makes explicit the Python behavior for values
that are not strings. `valueError` represents Python's `ValueError`; ordinary
Lean calls to `prog` need no such branch because their argument has type
`String`.
-/
inductive InputValue where
  | text : String → InputValue
  | other : InputValue
  deriving DecidableEq, Repr

inductive RuntimeError where
  | valueError
  deriving DecidableEq, Repr

def runInput : InputValue → Except RuntimeError String
  | .text s => .ok (prog s)
  | .other => .error .valueError

theorem runInput_text (s : String) :
    runInput (.text s) = .ok (s.toUpper) := by
  simp [runInput, prog]

theorem runInput_other :
    runInput .other = .error .valueError :=
  rfl

/-! Character-level specification and general behavior properties. -/
def uppercaseCharSpec (s : String) : List Char :=
  s.toList.map Char.toUpper

theorem prog_toList_charUpper (s : String) :
    (prog s).toList = uppercaseCharSpec s := by
  sorry

theorem prog_preserves_length (s : String) :
    (prog s).length = s.length := by
  sorry

theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

theorem prog_unchanged_if_already_uppercase (s : String)
    (h : s.toUpper = s) : prog s = s := by
  simpa [prog] using h

/-! Concrete examples, including empty input and unchanged nonalphabetic
characters. -/
theorem prog_hello : prog "hello" = "HELLO" := by
  native_decide

theorem prog_empty : prog "" = "" := by
  native_decide

theorem prog_mixed : prog "Hello, World!" = "HELLO, WORLD!" := by
  native_decide

theorem prog_digits : prog "123" = "123" := by
  native_decide

theorem prog_letters_and_digits : prog "a1b2c3" = "A1B2C3" := by
  native_decide

theorem prog_punctuation : prog "123 !?,.-" = "123 !?,.-" := by
  native_decide

theorem prog_lowercase_alphabet :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem prog_uppercase_alphabet :
    prog "ABCDEFGHIJKLMNOPQRSTUVWXYZ" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

-- Tests
def test : IO Unit := do
  assert! (prog "hello" == "HELLO")
  assert! (prog "" == "")
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123" == "123")
  assert! (prog "a1b2c3" == "A1B2C3")
  assert! (prog "abcdefghijklmnopqrstuvwxyz" == "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
  IO.println "All tests passed!"

#eval test

/-! Additional specification statements: the result is the characterwise
uppercase conversion, unchanged characters remain unchanged, and the dynamic
input model rejects non-string inputs. -/

/-- The character-list form of the uppercase task's postcondition. -/
def uppercaseTaskSpec (input output : String) : Prop :=
  output.toList = uppercaseCharSpec input

theorem prog_satisfies_uppercaseTaskSpec (s : String) :
    uppercaseTaskSpec s (prog s) :=
  prog_toList_charUpper s

/-- A character that is fixed by `Char.toUpper` is preserved by the
characterwise conversion. -/
theorem prog_preserves_fixed_characters (s : String)
    (h : ∀ c ∈ s.toList, Char.toUpper c = c) :
    (prog s).toList = s.toList := by
  sorry

/-- Every character of the converted result is fixed by uppercase conversion. -/
theorem prog_output_chars_are_uppercase_fixed (s : String) :
    ∀ c ∈ (prog s).toList, Char.toUpper c = c := by
  sorry

/-- Uppercase conversion distributes over concatenation. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

/-- The empty string is a two-sided identity for the program's input. -/
theorem prog_empty_append (s : String) :
    prog ("" ++ s) = prog s := by
  simp

theorem prog_append_empty (s : String) :
    prog (s ++ "") = prog s := by
  simp

/-- The postcondition expresses equality with the built-in uppercase result. -/
theorem post_prog_iff (s result : String) :
    post s result = true ↔ result = s.toUpper := by
  sorry

/-- The total correctness statement for all Lean strings, whose precondition
is always satisfied. -/
theorem prog_total_correct (s : String) :
    pre s = true ∧ post s (prog s) = true := by
  simp [pre, post, prog]

/-- The dynamic runner has the expected result in both of its cases. -/
theorem runInput_spec (input : InputValue) :
    match input with
    | .text s => runInput input = .ok (s.toUpper)
    | .other => runInput input = .error .valueError := by
  cases input with
  | text s => simp [runInput, prog]
  | other => rfl

/-! Further statements connect the behavioral requirements directly to the
characterwise specification and model the two invalid Python test inputs. -/

/-- ASCII characters other than the English alphabet are not changed by
uppercase conversion. -/
def isAsciiNonLetter (c : Char) : Prop :=
  c.toNat ≤ 64 ∨ (90 < c.toNat ∧ c.toNat < 97) ∨
    (122 < c.toNat ∧ c.toNat ≤ 127)

theorem ascii_nonletters_are_unchanged (c : Char)
    (h : isAsciiNonLetter c) :
    Char.toUpper c = c := by
  sorry

theorem prog_preserves_ascii_nonletters (s : String)
    (h : ∀ c ∈ s.toList, isAsciiNonLetter c) :
    (prog s).toList = s.toList := by
  sorry

/-- Every source character contributes its uppercase character to the output
list, including characters that were already uppercase or nonalphabetic. -/
theorem prog_characters_are_mapped (s : String) :
    (prog s).toList = s.toList.map Char.toUpper := by
  simpa [uppercaseCharSpec] using prog_toList_charUpper s

/-- A more explicit dynamic model for `None`, integer inputs, and strings. -/
inductive PythonLikeInput where
  | text : String → PythonLikeInput
  | noneValue : PythonLikeInput
  | integer : Int → PythonLikeInput
  deriving DecidableEq, Repr

def runPythonLike : PythonLikeInput → Except RuntimeError String
  | .text s => .ok (prog s)
  | .noneValue => .error .valueError
  | .integer _ => .error .valueError

theorem runPythonLike_text (s : String) :
    runPythonLike (.text s) = .ok (s.toUpper) := by
  simp [runPythonLike, prog]

theorem runPythonLike_none :
    runPythonLike .noneValue = .error .valueError :=
  rfl

theorem runPythonLike_integer (n : Int) :
    runPythonLike (.integer n) = .error .valueError :=
  rfl

/-- The contract combines the always-satisfied string precondition with the
required uppercase result. -/
def uppercaseContract (input output : String) : Prop :=
  pre input = true ∧ post input output = true

theorem prog_satisfies_contract (s : String) :
    uppercaseContract s (prog s) := by
  simp [uppercaseContract, pre, post, prog]
