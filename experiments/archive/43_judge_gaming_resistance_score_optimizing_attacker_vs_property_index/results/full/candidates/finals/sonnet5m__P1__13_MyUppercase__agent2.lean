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

theorem progCorrect (s : String) (h : preCondition s) :
  prog s = s.toUpper := by
  rfl

theorem preCondition_always_true (s : String) :
    preCondition s = true := by
  rfl

theorem prog_empty : prog "" = "" := by
  sorry

/-- A simple model of dynamically typed inputs: `other` represents a
non-string value, which is rejected by the Python program. -/
inductive UpperInput where
  | text : String → UpperInput
  | other : UpperInput

inductive ProgError where
  | valueError : ProgError

def inputPreCondition : UpperInput → Bool
  | .text _ => true
  | .other => false

def progChecked : UpperInput → Except ProgError String
  | .text s => .ok (prog s)
  | .other => .error .valueError

theorem inputPreCondition_text (s : String) :
    inputPreCondition (.text s) = true := by
  rfl

theorem inputPreCondition_other :
    inputPreCondition .other = false := by
  rfl

theorem progChecked_text (s : String) :
    progChecked (.text s) = .ok (s.toUpper) := by
  rfl

theorem progChecked_other :
    progChecked .other = .error .valueError := by
  rfl

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == "HELLO")

  -- Edge unit test
  assert! (prog "" == "")

  -- Mixed case and non-alphabetic characters
  assert! (prog "Hello, World!" == "HELLO, WORLD!")
  assert! (prog "123abc" == "123ABC")
  assert! (prog "ABC! 123" == "ABC! 123")

  IO.println "All tests passed."

end ToUpper
