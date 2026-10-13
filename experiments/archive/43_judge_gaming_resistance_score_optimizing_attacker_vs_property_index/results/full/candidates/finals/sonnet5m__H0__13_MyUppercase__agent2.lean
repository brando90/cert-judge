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

/-- The output specification for uppercasing a string. -/
def postCondition (input output : String) : Prop :=
  output = input.toUpper

/-- Every Lean `String` satisfies the input precondition. -/
theorem preCondition_true (s : String) : preCondition s = true := by
  rfl

/-- The program satisfies the output specification for every string input. -/
theorem prog_satisfies_postCondition (s : String) :
    postCondition s (prog s) := by
  rfl

theorem progCorrect (s : String) (h : preCondition s) :
    prog s = s.toUpper := by
  rfl

theorem prog_empty : prog "" = "" := by
  native_decide

theorem prog_lowercase : prog "hello" = "HELLO" := by
  native_decide

theorem prog_mixed_case :
    prog "Hello, World!" = "HELLO, WORLD!" := by
  native_decide

theorem prog_digits_and_lowercase :
    prog "123abc" = "123ABC" := by
  native_decide

theorem prog_nonalphabetic_unchanged :
    prog "123 !?" = "123 !?" := by
  native_decide

theorem prog_full_ascii_lowercase :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem prog_uppercase_unchanged :
    prog "LEAN 4!" = "LEAN 4!" := by
  native_decide

theorem prog_idempotent (s : String) : prog (prog s) = prog s := by
  sorry

/-- Uppercasing changes characters in place, so the string length is preserved. -/
theorem prog_preserves_length (s : String) :
    (prog s).length = s.length := by
  sorry

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == "HELLO")

  -- Edge unit test
  assert! (prog "" == "")

  -- Mixed case and non-alphabetic characters
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123abc" == "123ABC")
  assert! (prog "123 !?" == "123 !?")

  IO.println "All tests passed."

end ToUpper
