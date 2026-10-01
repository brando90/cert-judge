import Mathlib
import Lean

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

def uppercaseChar (c : Char) : Char :=
  if c.isLower then c.toUpper else c

def uppercaseSpec (s : String) : String :=
  s.map uppercaseChar

def SatisfiesUppercaseSpec (input output : String) : Prop :=
  output = uppercaseSpec input

theorem pre_holds_for_every_string (s : String) : pre s = true := rfl

theorem prog_correct (s : String) :
    prog s = uppercaseSpec s := rfl

theorem prog_satisfies_spec (s : String) :
    SatisfiesUppercaseSpec s (prog s) := rfl

theorem uppercaseChar_lowercase_branch (c : Char) (h : c.isLower = true) :
    uppercaseChar c = c.toUpper := by
  simp [uppercaseChar, h]

theorem uppercaseChar_nonlowercase_branch (c : Char) (h : c.isLower = false) :
    uppercaseChar c = c := by
  simp [uppercaseChar, h]

theorem prog_empty : prog "" = "" := by native_decide

theorem prog_lowercase_example : prog "hello" = "HELLO" := by native_decide

theorem prog_preserves_nonletters : prog "123 !?-" = "123 !?-" := by
  native_decide

theorem prog_preserves_uppercase : prog "ABC XYZ" = "ABC XYZ" := by
  native_decide

theorem prog_mixed_example : prog "Hello, 123!" = "HELLO, 123!" := by
  native_decide

theorem prog_mixed_letters_and_symbols : prog "aB-9 z" = "AB-9 Z" := by
  native_decide

theorem prog_lowercase_ascii : prog "abcdefghijklmnopqrstuvwxyz" =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

/-- A small model of inputs before the Python string type check. -/
inductive RuntimeInput where
  | text (value : String)
  | nonText
  deriving DecidableEq

/-- The precondition is explicit when inputs are not restricted to `String`. -/
def runtimePre : RuntimeInput → Bool
  | .text _ => true
  | .nonText => false

/-- The result type records the exception path for inputs that are not strings. -/
def checkedProg : RuntimeInput → Except Unit String
  | .text s => .ok (prog s)
  | .nonText => .error ()

theorem runtimePre_text (s : String) : runtimePre (.text s) = true := rfl

theorem runtimePre_nonText : runtimePre .nonText = false := rfl

theorem checkedProg_text (s : String) :
    checkedProg (.text s) = .ok (uppercaseSpec s) := by
  simp [checkedProg, prog_correct]

theorem checkedProg_nonText :
    checkedProg .nonText = (.error () : Except Unit String) := rfl

/-- The checked model returns the uppercase result for strings and an error otherwise. -/
def CheckedSatisfiesSpec (input : RuntimeInput)
    (result : Except Unit String) : Prop :=
  match input with
  | .text s => result = .ok (uppercaseSpec s)
  | .nonText => ∃ e, result = .error e

theorem checkedProg_satisfies_spec (input : RuntimeInput) :
    CheckedSatisfiesSpec input (checkedProg input) := by
  cases input with
  | text s =>
      simp [CheckedSatisfiesSpec, checkedProg, prog_correct]
  | nonText =>
      exact ⟨(), rfl⟩

/-- The output consists of the input characters transformed one at a time. -/
theorem prog_toList (s : String) :
    (prog s).toList = s.toList.map uppercaseChar := by
  sorry

/-- Uppercasing distributes over concatenation. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by
  sorry

/-- Character-wise uppercasing does not change the number of characters. -/
theorem prog_length (s : String) :
    (prog s).length = s.length := by
  sorry

/-- Applying the conversion repeatedly has no further effect. -/
theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

theorem prog_preserves_digits_and_punctuation :
    prog "09!?.,:;+-*/" = "09!?.,:;+-*/" := by
  native_decide

theorem prog_preserves_already_uppercase :
    prog "LEAN 4" = "LEAN 4" := by
  native_decide

theorem prog_converts_mixed_ascii :
    prog "Lean is Fun!" = "LEAN IS FUN!" := by
  native_decide

theorem prog_preserves_whitespace_and_symbols :
    prog " \t\n!?_-=+()[]{} " = " \t\n!?_-=+()[]{} " := by
  native_decide

theorem prog_converts_letters_around_digits :
    prog "a1b2c3" = "A1B2C3" := by
  native_decide

theorem prog_converts_sentence :
    prog "The quick brown fox jumps over the lazy dog." =
      "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG." := by
  native_decide

theorem prog_idempotent_ascii_example :
    prog (prog "MiXeD 123!?") = prog "MiXeD 123!?" := by
  native_decide

theorem prog_length_ascii_example :
    (prog "MiXeD 123!?").length = ("MiXeD 123!?").length := by
  native_decide

theorem prog_append_ascii_example :
    prog ("hello" ++ ", world!") = prog "hello" ++ prog ", world!" := by
  native_decide

end VeriBench.StringToUpper
