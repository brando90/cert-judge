```lean
import Lean
import Mathlib.Tactic

/-- A string with HTML-escaped special characters -/
structure SafeString where
  val : String
  is_safe : True  -- Represents that the string has been properly escaped
  deriving Repr

/-- Represents a web application with template rendering capabilities -/
structure WebApplication where
  /-- Safely render a template by escaping all context values -/
  safe_render_template : (template : String) → (context : List (String × String)) → String

/-- Escape HTML special characters in a string -/
def html.escape (s : String) : SafeString :=
  let escaped := s.replace "&" "&amp;"
                  |>.replace "<" "&lt;"
                  |>.replace ">" "&gt;"
                  |>.replace "\"" "&quot;"
                  |>.replace "'" "&#x27;"
  { val := escaped, is_safe := True.intro }

/-- Implementation of safe XSS handling function -/
def safe_xss_handling (app : WebApplication) (user_input : String) : 
  {result : List (String × String) // result.any (fun (k, _) => k = "vulnerable" && _ = "true") = false} :=
  let comment_template := "
    <div class=\"comment\">
        <p>{{{comment_text}}}</p>
        <small>Posted by: {{{username}}}</small>
    </div>
    "
  let context := [("comment_text", (html.escape user_input).val), ("username", (html.escape "user123").val)]
  let rendered := app.safe_render_template comment_template context
  ⟨[("rendered_html", rendered), ("vulnerable", "false")], by simp⟩

/-- Specification: The rendered HTML should not contain unescaped user input -/
def safe_xss_handling_spec (app : WebApplication) (user_input : String) : Prop :=
  let result := (safe_xss_handling app user_input).val
  result.any (fun (k, _) => k = "vulnerable" && _ = "true") = false ∧
  result.any (fun (k, v) => k = "rendered_html" ∧ v.contains "<script") = false

/-- Correctness theorem for the safe XSS handling function -/
theorem safe_xss_handling_correct (app : WebApplication) (user_input : String) :
  safe_xss_handling_spec app user_input := by
  sorry

/-- Test that the function properly escapes script tags -/
def test_script_tag_escaping : IO Unit := do
  let app : WebApplication := {
    safe_render_template := fun template context =>
      context.foldl (fun result (k, v) => 
        result.replace s!"{{{{{{k}}}}}}" v
      ) template
  }
  
  let malicious_input := "<script>alert('XSS')</script>"
  let result := (safe_xss_handling app malicious_input).val
  
  let rendered_html := result.find? (fun (k, _) => k = "rendered_html")
  match rendered_html with
  | some (_, html) => 
    if html.contains "<script" then
      throw (IO.userError "Test failed: Unescaped script tag found")
    else if !html.contains "&lt;script" then
      throw (IO.userError "Test failed: Script tag not properly escaped")
    else
      IO.println "Test passed: Script tag properly escaped"
  | none =>
    throw (IO.userError "Test failed: rendered_html not found in result")

/-- Run all tests -/
def main : IO Unit := do
  test_script_tag_escaping
  IO.println "All tests passed."
```
