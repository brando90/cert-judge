import Mathlib
import Lean

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

/-- The character transformation used by `prog`. -/
def upperChar (c : Char) : Char :=
  if c.isLower then c.toUpper else c

/-- On the Lean `String` input domain, the precondition is always satisfied. -/
theorem pre_true (s : String) : pre s = true := rfl

/-- The implementation applies its character transformation to every character. -/
theorem prog_characterwise (s : String) :
    prog s = String.map upperChar s := by
  rfl

theorem upperChar_of_lower (c : Char) (h : c.isLower = true) :
    upperChar c = c.toUpper := by
  simp [upperChar, h]

theorem upperChar_of_not_lower (c : Char) (h : c.isLower = false) :
    upperChar c = c := by
  simp [upperChar, h]

/-- Mapping characters does not change the number of characters in the string. -/
theorem prog_preserves_length (s : String) :
    (prog s).length = s.length := by sorry

/-- Applying the conversion twice has the same result as applying it once. -/
theorem prog_idempotent (s : String) :
    prog (prog s) = prog s := by
  sorry

theorem prog_empty : prog "" = "" := by
  native_decide

theorem test_basic : prog "hello" = "HELLO" := by
  native_decide

theorem test_punctuation_and_digits :
    prog "Hello, world! 123" = "HELLO, WORLD! 123" := by
  native_decide

theorem test_nonletters_unchanged : prog "123 !?" = "123 !?" := by
  native_decide

/-- The character-list view of the result is the mapped character-list view
of the input. -/
theorem prog_toList (s : String) :
    (prog s).toList = s.toList.map upperChar := by sorry

/-- Strings containing no lowercase characters are left unchanged. -/
def NoLowercase (s : String) : Prop :=
  ∀ c ∈ s.toList, c.isLower = false

theorem prog_eq_self_of_noLowercase (s : String) (h : NoLowercase s) :
    prog s = s := by
  sorry

theorem test_already_uppercase : prog "LEAN 4!" = "LEAN 4!" := by
  native_decide

theorem test_mixed_case_and_whitespace :
    prog "aBc DeF\n123" = "ABC DEF\n123" := by
  native_decide

/-- Every ASCII lowercase letter is converted to its ASCII uppercase
counterpart. -/
theorem test_ascii_lowercase_alphabet :
    prog "abcdefghijklmnopqrstuvwxyz" = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem test_ascii_mixed_alphabet :
    prog "AbCdEfGhIjKlMnOpQrStUvWxYz" =
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ" := by
  native_decide

theorem test_ascii_symbols_preserved :
    prog "0123456789 !@#$%^&*()-_=+[]{};:',.<>/?\\|`~" =
      "0123456789 !@#$%^&*()-_=+[]{};:',.<>/?\\|`~" := by
  native_decide

theorem test_newline_and_tab :
    prog "a\tb\nc" = "A\tB\nC" := by
  native_decide

/-- A small tagged input type models the distinction between Python strings
and values that violate the Python precondition. -/
inductive RuntimeInput where
  | string (value : String)
  | other (repr : String)
  deriving DecidableEq, Repr

/-- Runtime version of the Python precondition on tagged inputs. -/
def runtimePre : RuntimeInput → Bool
  | .string _ => true
  | .other _ => false

inductive PythonException where
  | valueError (message : String)
  deriving DecidableEq, Repr

/-- Evaluation on tagged inputs, including the `ValueError` case that cannot
be represented by the statically typed `String → String` implementation. -/
def runtimeProg : RuntimeInput → Except PythonException String
  | .string s => .ok (prog s)
  | .other repr =>
      .error (.valueError ("Require string input (got s=" ++ repr ++ ")"))

theorem runtimePre_string (s : String) : runtimePre (.string s) = true := rfl

theorem runtimePre_other (repr : String) : runtimePre (.other repr) = false := rfl

theorem runtimeProg_string (s : String) :
    runtimeProg (.string s) = .ok (prog s) := rfl

theorem runtimeProg_other (repr : String) :
    runtimeProg (.other repr) =
      .error (.valueError ("Require string input (got s=" ++ repr ++ ")")) := rfl

theorem runtimeProg_rejects_none :
    runtimeProg (.other "None") =
      .error (.valueError "Require string input (got s=None)") := rfl

theorem runtimeProg_rejects_integer :
    runtimeProg (.other "123") =
      .error (.valueError "Require string input (got s=123)") := rfl

end VeriBench.StringToUpper
