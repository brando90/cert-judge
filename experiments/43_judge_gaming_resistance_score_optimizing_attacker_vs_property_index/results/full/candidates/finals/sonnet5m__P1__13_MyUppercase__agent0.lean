import Mathlib
import Lean

namespace VeriBench.StringToUpper

/-- In this model every input is already a `String`, so the Python string
    precondition is satisfied for every argument in the domain. -/
def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

theorem pre_true (s : String) : pre s = true := rfl

/-- The character transformation used by `prog`. -/
def upperChar (c : Char) : Char :=
  if c.isLower then c.toUpper else c

theorem upperChar_of_lower (c : Char) (h : c.isLower = true) :
    upperChar c = c.toUpper := by
  simp [upperChar, h]

theorem upperChar_of_not_lower (c : Char) (h : c.isLower = false) :
    upperChar c = c := by
  simp [upperChar, h]

/-- `prog` maps the character transformation over the input string. -/
theorem prog_eq_map_upperChar (s : String) :
    prog s = s.map upperChar := rfl

/-- A list-level characterization of the output, one transformed character at a time. -/
theorem prog_toList (s : String) :
    (prog s).toList = s.toList.map (fun c => if c.isLower then c.toUpper else c) := by
  sorry

theorem prog_empty : prog "" = "" := by
  native_decide

theorem prog_hello : prog "hello" = "HELLO" := by
  native_decide

theorem prog_mixed_case_and_punctuation :
    prog "Hello, world! 123" = "HELLO, WORLD! 123" := by
  native_decide

theorem prog_non_alphabetic :
    prog "123 !?.,-" = "123 !?.,-" := by
  native_decide

/-- A string containing no lowercase characters is unchanged. -/
theorem prog_eq_self_of_no_lower (s : String)
    (h : ∀ c ∈ s.toList, c.isLower = false) :
    prog s = s := by
  sorry

/-- Mapping the conversion preserves the number of characters. -/
theorem prog_length (s : String) :
    (prog s).length = s.length := by
  sorry

/-- Conversion acts independently on the two parts of a concatenated string. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

/-- The conversion is deterministic: equal inputs have equal outputs. -/
theorem prog_congr {s t : String} (h : s = t) :
    prog s = prog t := by
  simpa [h]

/-- The complete lowercase ASCII alphabet is converted to uppercase. -/
theorem prog_ascii_lowercase :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

/-- Already-uppercase ASCII letters are unchanged. -/
theorem prog_ascii_uppercase :
    prog "ABCDEFGHIJKLMNOPQRSTUVWXYZ" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

/-- Digits and punctuation are preserved while lowercase letters are converted. -/
theorem prog_lowercase_with_digits_and_punctuation :
    prog "a1! b2?" = "A1! B2?" := by
  native_decide

/-- The empty input satisfies the input precondition in the string-valued model. -/
theorem pre_empty : pre "" = true := rfl

/-- Every string-valued input satisfies the modeled precondition. -/
theorem every_string_is_valid (s : String) : pre s = true := pre_true s

end VeriBench.StringToUpper
