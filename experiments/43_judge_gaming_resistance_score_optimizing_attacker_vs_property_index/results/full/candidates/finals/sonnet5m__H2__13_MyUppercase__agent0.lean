import Mathlib
import Lean

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

def upperChar (c : Char) : Char :=
  if c.isLower then c.toUpper else c

def UppercaseSpec (s out : String) : Prop :=
  out.toList = s.toList.map upperChar

theorem pre_is_true (s : String) : pre s = true := rfl

/-- The output satisfies the pointwise uppercase specification. -/
theorem prog_correct (s : String) : UppercaseSpec s (prog s) := by sorry

theorem prog_toList (s : String) :
    (prog s).toList = s.toList.map upperChar := by sorry

/-- The specification determines a unique output string. -/
theorem UppercaseSpec_unique (s out₁ out₂ : String)
    (h₁ : UppercaseSpec s out₁) (h₂ : UppercaseSpec s out₂) :
    out₁ = out₂ := by
  apply String.ext
  exact h₁.trans h₂.symm

theorem prog_spec_iff (s out : String) :
    UppercaseSpec s out ↔ out = prog s := by
  constructor
  · intro h
    exact UppercaseSpec_unique s out (prog s) h (prog_correct s)
  · rintro rfl
    exact prog_correct s

theorem upperChar_of_lower (c : Char) (h : c.isLower) :
    upperChar c = c.toUpper := by
  simp [upperChar, h]

theorem upperChar_of_not_lower (c : Char) (h : ¬ c.isLower) :
    upperChar c = c := by
  simp [upperChar, h]

/-- Characters not selected for conversion are left unchanged. -/
theorem prog_length (s : String) : (prog s).length = s.length := by
  sorry

theorem prog_unchanged_if_no_lower (s : String)
    (h : ∀ c ∈ s.toList, ¬ c.isLower) : prog s = s := by sorry

/-- Mapping the conversion over a concatenation converts both parts. -/
theorem prog_append (s t : String) :
    prog (s ++ t) = prog s ++ prog t := by sorry

/-- Applying the conversion twice has the same result as applying it once. -/
theorem prog_idempotent (s : String) : prog (prog s) = prog s := by
  sorry

theorem prog_empty : prog "" = "" := by
  native_decide

theorem prog_hello : prog "hello" = "HELLO" := by
  native_decide

theorem prog_mixed_case :
    prog "Hello, World! 123" = "HELLO, WORLD! 123" := by
  native_decide

theorem prog_nonletters_unchanged : prog "123 !?" = "123 !?" := by
  native_decide

end VeriBench.StringToUpper
