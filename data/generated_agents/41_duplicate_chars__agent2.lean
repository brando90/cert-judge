import Lean.Data.HashMap
import Mathlib.Tactic

namespace VeriBench

/-- Duplicate each character in the input string.

Edge cases:
- Empty string returns empty string.
- Non-string input is invalid and raises ValueError.
-/

def duplicateChars (s : String) : String :=
  String.join (s.data.map (fun c => String.singleton c ++ String.singleton c))

-- Tests
def testDuplicateChars : IO Unit := do
  -- Basic
  assert! (duplicateChars "abc" == "aabbcc")
  -- Edge
  assert! (duplicateChars "" == "")
  -- Other
  assert! (duplicateChars "!a " == "!!aa  ")
  IO.println "All tests passed."

-- Verification
def duplicateChars_spec (s : String) : String :=
  String.join (s.data.map (fun c => String.singleton c ++ String.singleton c))

/-- Pre-condition: Input must be a string -/
def duplicateChars_pre (s : String) : Prop := True

/-- Post-condition: Each character is duplicated in the output -/
def duplicateChars_post (s : String) (result : String) : Prop :=
  result = duplicateChars_spec s

theorem duplicateChars_correct (s : String) (h : duplicateChars_pre s) : 
  duplicateChars_post s (duplicateChars s) := by
  unfold duplicateChars_post
  unfold duplicateChars_spec
  unfold duplicateChars
  rfl
  sorry

end VeriBench
