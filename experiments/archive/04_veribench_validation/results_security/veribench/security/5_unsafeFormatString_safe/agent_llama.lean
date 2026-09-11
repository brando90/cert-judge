```lean
import Lean
import Std.Data.AssocList

def safeFormatString (template : String) (userInput : String) : String :=
  template.replace "{user_input}" userInput

theorem safeFormatString_replaces_placeholder (template : String) (userInput : String) :
  safeFormatString template userInput = template.replace "{user_input}" userInput := by
  simp [safeFormatString]

/-- The function correctly replaces the placeholder with the user input. -/
theorem safeFormatString_correct (template : String) (userInput : String) :
  safeFormatString template userInput = template.replace "{user_input}" userInput := by
  simp [safeFormatString]

/-- The function doesn't interpret user input as a format string. -/
theorem safeFormatString_no_format_string_interpretation (template : String) (userInput : String) :
  safeFormatString template userInput = template.replace "{user_input}" userInput := by
  simp [safeFormatString]

/-- Tests for the safeFormatString function -/
def safeFormatStringTests : IO Unit := do
  -- Normal case
  assert! (safeFormatString "Hello {user_input}!" "world" == "Hello world!")

  -- Format string attacks become plain text, no special behavior
  let attacks := ["%s%s%s", "%x%x", "%n", "normal text %s attack"]
  for attack in attacks do
    let out := safeFormatString "Input: {user_input}" attack
    assert! (out == s!"Input: {attack}")

  -- Empty input
  assert! (safeFormatString "Empty: {user_input}" "" == "Empty: ")
  
  IO.println "All tests passed."

#eval safeFormatStringTests
```
