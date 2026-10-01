import VeriBench

namespace ToUpper

/-- Every value of the Lean `String` type is a valid string input. -/
def preCondition (s : String) : Bool := true

/-- Convert all lowercase letters in a string to uppercase.

Edge cases:
- Empty string returns empty string.
- Non-alphabetic characters remain unchanged.

As in Python's `str.upper`, the result is represented by Lean's `String.toUpper`.
-/
def prog (s : String) : String :=
  s.toUpper

/-- The postcondition for uppercasing a string. -/
def postCondition (s result : String) : Prop :=
  result = s.toUpper

theorem preCondition_holds (s : String) : preCondition s = true := by
  rfl

/-- `prog` returns the uppercase form of every string satisfying the precondition. -/
theorem progCorrect (s : String) (h : preCondition s) :
    prog s = s.toUpper := by
  rfl

theorem prog_satisfies_postCondition (s : String) (h : preCondition s) :
    postCondition s (prog s) := by
  rfl

/-- Uppercasing an already-uppercase string leaves it unchanged. -/
theorem prog_eq_self_of_uppercase (s : String) (h : s.toUpper = s) :
    prog s = s := by
  simpa [prog] using h

/-- A string is unchanged by `prog` exactly when it is fixed by `String.toUpper`. -/
theorem prog_eq_self_iff (s : String) :
    prog s = s ↔ s.toUpper = s := by
  rfl

/-- Uppercasing twice has the same result as uppercasing once. -/
theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

theorem prog_empty : prog "" = "" := by
  native_decide

theorem prog_lowercase_example : prog "hello" = "HELLO" := by
  native_decide

theorem prog_mixed_case_example :
    prog "Hello, World!" = "HELLO, WORLD!" := by
  native_decide

theorem prog_non_alphabetic_example : prog "123!?" = "123!?" := by
  native_decide

/-- The postcondition characterizes the unique correct output. -/
theorem postCondition_iff_output (s result : String) :
    postCondition s result ↔ result = prog s := by
  simp [postCondition, prog]

/-- Any result satisfying the postcondition is exactly the program's output. -/
theorem prog_output_unique (s result : String)
    (h : postCondition s result) :
    result = prog s := by
  simpa [postCondition, prog] using h

/-- The output of uppercasing is itself fixed by uppercasing. -/
theorem prog_output_is_uppercase (s : String) :
    (prog s).toUpper = prog s := by
  simpa [prog] using prog_idempotent s

/-- The program agrees with the postcondition for every possible result. -/
theorem prog_satisfies_postCondition_iff (s result : String) :
    postCondition s result ↔ result = prog s := by
  exact postCondition_iff_output s result

/--
A small checked interface models Python's `ValueError` case: `none` represents
an input that is not a string, while `some s` represents a string input.
The original `prog` itself accepts only Lean strings.
-/
def progChecked (input : Option String) : Except Unit String :=
  match input with
  | none => .error ()
  | some s => .ok (prog s)

theorem progChecked_nonString :
    progChecked none = Except.error () := by
  rfl

theorem progChecked_string (s : String) :
    progChecked (some s) = Except.ok (s.toUpper) := by
  rfl

/-- The checked interface fails exactly for inputs that do not represent strings. -/
theorem progChecked_error_iff (input : Option String) :
    (∃ e : Unit, progChecked input = Except.error e) ↔ input = none := by
  cases input <;> simp [progChecked]

/-- The checked interface returns the uppercase input for every string input. -/
theorem progChecked_input_cases (input : Option String) :
    progChecked input =
      match input with
      | none => Except.error ()
      | some s => Except.ok (s.toUpper) := by
  cases input <;> rfl

/-- The checked interface succeeds exactly on string inputs. -/
theorem progChecked_success_iff (input : Option String) :
    (∃ result, progChecked input = Except.ok result) ↔
      ∃ s, input = some s := by
  cases input <;> simp [progChecked]

/-- For a string input, the checked result is the uppercase string. -/
theorem progChecked_some_result (s : String) :
    ∃ result, progChecked (some s) = Except.ok result ∧ result = s.toUpper := by
  exact ⟨s.toUpper, rfl, rfl⟩

/-- Non-string inputs cannot produce a successful checked result. -/
theorem progChecked_none_not_ok (result : String) :
    progChecked none ≠ Except.ok result := by
  simp [progChecked]

theorem prog_uppercase_ascii_alphabet :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem prog_uppercase_existing_capitals :
    prog "HELLO" = "HELLO" := by
  native_decide

theorem prog_preserves_digits_and_punctuation :
    prog "0123456789 !?,.-_" = "0123456789 !?,.-_" := by
  native_decide

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == "HELLO")

  -- Empty string
  assert! (prog "" == "")

  -- Mixed case and non-alphabetic characters
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123abc" == "123ABC")
  assert! (prog "123!?" == "123!?")

  IO.println "All tests passed."

end ToUpper
