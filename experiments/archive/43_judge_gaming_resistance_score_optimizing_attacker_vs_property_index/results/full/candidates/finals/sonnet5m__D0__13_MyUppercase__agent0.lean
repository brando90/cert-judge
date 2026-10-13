import Mathlib
import Lean

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

def upperChar (c : Char) : Char :=
  if c.isLower then c.toUpper else c

/-- A small model of Python inputs, including values that are not strings. -/
inductive DynamicInput where
  | string (value : String)
  | other

def preDynamic : DynamicInput → Bool
  | .string _ => true
  | .other => false

/-- The checked interface models the exception raised for non-string inputs. -/
def checkedProg : DynamicInput → Except String String
  | .string s => .ok (prog s)
  | .other => .error "ValueError"

theorem pre_always_true (s : String) : pre s = true := by
  rfl

theorem prog_characterwise (s : String) :
    prog s = s.map upperChar := by
  rfl

theorem upperChar_lower (c : Char) (h : c.isLower = true) :
    upperChar c = c.toUpper := by
  simp [upperChar, h]

theorem upperChar_not_lower (c : Char) (h : c.isLower = false) :
    upperChar c = c := by
  simp [upperChar, h]

theorem prog_empty : prog "" = "" := by native_decide

theorem prog_hello : prog "hello" = "HELLO" := by native_decide

theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

theorem prog_preserves_length (s : String) :
    String.length (prog s) = String.length s := by
  sorry

theorem prog_unchanged_when_no_lowercase
    (s : String)
    (h : ∀ c ∈ s.toList, c.isLower = false) :
    prog s = s := by
  sorry

/-- The output string is obtained by applying the character conversion to
    each input character, in order. -/
theorem prog_toList (s : String) :
    (prog s).toList = (s.toList).map upperChar := by
  sorry

/-- Conversion preserves the number of characters. -/
theorem prog_preserves_character_count (s : String) :
    (prog s).toList.length = s.toList.length := by
  sorry

/-- Applying the conversion to an already converted string has no further
    effect. -/
theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

/-- Characters that are not lowercase are left unchanged. -/
theorem prog_unchanged_when_all_chars_not_lowercase
    (s : String)
    (h : ∀ c ∈ s.toList, c.isLower = false) :
    prog s = s := by
  sorry

theorem prog_uppercase_unchanged : prog "HELLO" = "HELLO" := by
  native_decide

theorem prog_mixed_example :
    prog "Hello, World! 123" = "HELLO, WORLD! 123" := by
  native_decide

theorem prog_punctuation_and_digits_unchanged :
    prog "123 !?-_.,:" = "123 !?-_. ,:" := by
  sorry

theorem preDynamic_string (s : String) :
    preDynamic (.string s) = true := by
  rfl

theorem preDynamic_other : preDynamic .other = false := by
  rfl

theorem checkedProg_string (s : String) :
    checkedProg (.string s) = .ok (prog s) := by
  rfl

theorem checkedProg_other :
    checkedProg .other = .error "ValueError" := by
  rfl

theorem checkedProg_empty :
    checkedProg (.string "") = .ok "" := by sorry

theorem checkedProg_hello :
    checkedProg (.string "hello") = .ok "HELLO" := by sorry

/-- Digits and punctuation are preserved exactly. -/
theorem prog_punctuation_and_digits_exact :
    prog "123 !?-_.,:" = "123 !?-_. ,:" := by
  sorry

/-- The checked interface rejects inputs that are not strings. -/
theorem checkedProg_rejects_other :
    checkedProg .other = .error "ValueError" := by
  rfl

end VeriBench.StringToUpper
