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
  simp [prog]
  sorry

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
