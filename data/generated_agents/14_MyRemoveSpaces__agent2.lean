import Std.Data.String.Basic

namespace RemoveSpaces

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.replace " " ""

theorem prog_spec (s : String) : pre s → prog s = s.replace " " "" :=
  fun _ => rfl

/--
Remove all space characters from a string.

Edge cases:
- Empty string returns empty string.
- String with only spaces returns empty string.
-/
def removeSpaces (s : String) : String :=
  prog s

/-- Unit tests for removeSpaces -/
def tests : IO Unit := do
  -- Basic test
  assert! (removeSpaces "hello world" = "helloworld")
  
  -- Edge cases
  assert! (removeSpaces "" = "")
  assert! (removeSpaces "   " = "")
  
  -- Additional tests
  assert! (removeSpaces "no spaces" = "nospaces")
  assert! (removeSpaces " leading space" = "leadingspace")
  assert! (removeSpaces "trailing space " = "trailingspace")
  assert! (removeSpaces " spaces everywhere " = "spaceseverywhere")
  
  IO.println "All tests passed!"

end RemoveSpaces
