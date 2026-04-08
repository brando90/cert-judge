import Lean.Data.HashMap

namespace RemoveDigits

def isDigit (c : Char) : Bool :=
  '0' ≤ c && c ≤ '9'

/-- Pre-condition: input must be a string -/
def pre (s : String) : Prop := True

/-- Post-condition: result contains no digit characters -/
def post (s : String) (result : String) : Prop :=
  ∀ c, c ∈ result.data → ¬isDigit c

/-- Implementation: Remove all digit characters from a string -/
def remove_digits (s : String) : String :=
  ⟨s.data.filter (fun c => ¬isDigit c)⟩

theorem remove_digits_spec (s : String) (h : pre s) :
  post s (remove_digits s) :=
sorry

/-- Tests for remove_digits function -/
def test : IO Unit := do
  -- Basic test
  assert! (remove_digits "abc123def" == "abcdef")
  -- No digits
  assert! (remove_digits "no numbers" == "no numbers")
  -- Only digits
  assert! (remove_digits "123" == "")
  -- Empty string
  assert! (remove_digits "" == "")
  IO.println "All tests passed."

end RemoveDigits
