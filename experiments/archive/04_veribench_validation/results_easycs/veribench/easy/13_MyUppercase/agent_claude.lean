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
