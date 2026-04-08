```lean
import Lean.Data.Parsec
import Std.Data.String.Basic

namespace VeriBench.RemoveDigits

def pre (s : String) : Bool := true

def post (s : String) (result : String) : Bool :=
  ∀ c, c ∈ result.data → !c.isDigit

def removeDigits (s : String) : String :=
  s.foldl (fun acc c => if c.isDigit then acc else acc.push c) ""

theorem removeDigits_spec (s : String) : post s (removeDigits s) := by
  sorry

/-- Tests for removeDigits function -/
def tests : IO Unit := do
  -- Basic test
  assert! (removeDigits "abc123def" == "abcdef")
  -- No digits
  assert! (removeDigits "no numbers" == "no numbers")
  -- Only digits
  assert! (removeDigits "123" == "")
  -- Edge case: empty string
  assert! (removeDigits "" == "")
  IO.println "All tests passed!"

end VeriBench.RemoveDigits
```
