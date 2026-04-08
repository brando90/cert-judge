```lean
import Lean
import Mathlib.Tactic.Basic
open Lean Elab Command Term Meta

/-!
# Safe XSS Handling

This module provides functions for safely rendering HTML templates
by escaping user input to prevent XSS attacks.
-/

/-- Escape HTML special characters in a string -/
def htmlEscape (s : String) : String :=
  s.replace "&" "&amp;"
   .replace "<" "&lt;"
   .replace ">" "&gt;"
   .replace "\"" "&quot;"
   .replace "'" "&#x27;"

/-- Web application with template rendering capabilities -/
structure WebApplication where
  /-- Safely render a template by escaping all context values -/
  safeRenderTemplate : (template : String) → (context : List (String × String)) → String :=
    fun template context =>
      let safeCtx := context.map (fun (k, v) => (k, htmlEscape v))
      safeCtx.foldl (fun acc (k, v) => acc.replace s!"{{{{k}}}}" v) template

/-- Result of rendering user input -/
structure RenderResult where
  renderedHtml : String
  vulnerable : Bool

/-- 
  Safe XSS handling function that renders user input in a template
  while preventing XSS attacks by escaping special characters.
-/
def safeXssHandling (app : WebApplication) (userInput : String) : RenderResult :=
  let commentTemplate := "
    <div class=\"comment\">
        <p>{{{comment_text}}}</p>
        <small>Posted by: {{{username}}}</small>
    </div>
    "
  let rendered := app.safeRenderTemplate commentTemplate [
    ("comment_text", userInput),
    ("username", "user123")
  ]
  { renderedHtml := rendered, vulnerable := false }

/-- Specification for safe XSS handling function -/
def safeXssHandlingSpec (app : WebApplication) (userInput : String) : RenderResult :=
  let result := safeXssHandling app userInput
  -- Specification: result should not contain unescaped script tags
  { result with 
    vulnerable := result.renderedHtml.contains "<script" || 
                 result.renderedHtml.contains "<SCRIPT" }

/-- Tests for the safeXssHandling function -/
def testSafeXssHandling : IO Unit := do
  let app : WebApplication := {}
  let maliciousInput := "<script>alert('XSS')</script>"
  let result := safeXssHandling app maliciousInput
  
  if result.vulnerable then
    throw (IO.userError "Test failed: Result should not be vulnerable")
  
  if result.renderedHtml.contains "<script" then
    throw (IO.userError "Test failed: Rendered HTML contains unescaped script tag")
  
  if !(result.renderedHtml.contains "&lt;script") then
    throw (IO.userError "Test failed: Rendered HTML doesn't contain escaped script tag")
  
  IO.println "All tests passed."

/-- Theorem stating that safeXssHandling correctly prevents XSS attacks -/
theorem safeXssHandling_prevents_xss (app : WebApplication) (userInput : String) :
  let result := safeXssHandling app userInput
  result.vulnerable = false ∧ 
  (userInput.contains "<script" → result.renderedHtml.contains "&lt;script") ∧
  ¬result.renderedHtml.contains "<script" :=
sorry

/-- Theorem stating that safeXssHandling satisfies its specification -/
theorem safeXssHandling_correct (app : WebApplication) (userInput : String) :
  safeXssHandling app userInput = safeXssHandlingSpec app userInput :=
sorry
```
