import Mathlib

namespace MyRemoveSpaces

/-!
# Implementation of `myRemoveSpaces`.**

`myRemoveSpaces s` returns a new string with all spaces removed.
Uses fold to accumulate non-space characters.
-/

def myRemoveSpaces (s : String) : String :=
  s.foldl (fun acc c => if isSpace c then acc else acc.push c) ""

/-!
# Imperative Implementation
-/


def myRemoveSpacesImp (s : String) : String := Id.run do
  let mut result := ""
  for c in s.data do
    if ¬isSpace c then
      result := result.push c
  return result

/-!
# Property Theorem Proofs
-/



/-!
# Unit Tests
-/

/-- expected: "helloworld" -/
example : myRemoveSpaces "hello world" = "helloworld" := by native_decide
#eval myRemoveSpaces "hello world" -- expected: "helloworld"

/-- expected: "spaceseverywhere" -/
example : myRemoveSpaces "   spaces   everywhere   " = "spaceseverywhere" := by native_decide
#eval myRemoveSpaces "   spaces   everywhere   " -- expected: "spaceseverywhere"

/-- expected: "nospaces" (edge cases)-/
example : myRemoveSpaces "no spaces" = "nospaces" := by native_decide
#eval myRemoveSpaces "no spaces" -- expected: "nospaces"

/-!
# Positive / Negative Test-Suite
-/

/-- positive: no spaces means no change -/
example : myRemoveSpaces "hello" = "hello" := by native_decide
#eval myRemoveSpaces "hello" -- expected: "hello"

/-- positive: empty string remains empty -/
example : myRemoveSpaces "" = "" := by native_decide
#eval myRemoveSpaces "" -- expected: ""

/-- positive: only spaces becomes empty -/
example : myRemoveSpaces "   " = "" := by native_decide
#eval myRemoveSpaces "   " -- expected: ""

/-- negative: result should not contain spaces -/
example : ¬ (' ' ∈ (myRemoveSpaces "a b c").data) := by native_decide

#eval (decide (' ' ∈ (myRemoveSpaces "a b c").data)) -- expected: false

/-- negative: applying twice should be same as once -/
example : ¬ (myRemoveSpaces (myRemoveSpaces "a b") ≠ myRemoveSpaces "a b") := by native_decide
#eval (decide (myRemoveSpaces (myRemoveSpaces "a b") ≠ myRemoveSpaces "a b")) -- expected: false

/-!
# Positive / Negative Test-Suite
-/

/-- positive: maintains space removal computation -/
example : myRemoveSpacesImp "a b c" = "abc" := by native_decide
#eval myRemoveSpacesImp "a b c" -- expected: "abc"

/-- negative: result should not contain spaces -/
example : ¬ (' ' ∈ (myRemoveSpacesImp "x y z").data) := by native_decide

#eval (decide (' ' ∈ (myRemoveSpacesImp "x y z").data)) -- expected: false

/-- **Equivalence**: functional and imperative space removal coincide. -/
private theorem myRemoveSpacesImp_aux (cs : List Char) (acc : String) :
    Id.run (do
      let mut result := acc
      for c in cs do
        if ¬isSpace c then
          result := result.push c
      return result) =
    cs.foldl (fun acc c => if isSpace c then acc else acc.push c) acc := by
  induction cs generalizing acc with
  | nil =>
      simp
  | cons c cs ih =>
      cases hsc : isSpace c with
      | false =>
          simpa [hsc, Bool.eq_false_eq_not_eq_true] using ih (acc.push c)
      | true =>
          simpa [hsc, Bool.eq_false_eq_not_eq_true] using ih acc

theorem myRemoveSpaces_equivalence (s : String) :
  myRemoveSpaces s = myRemoveSpacesImp s := by
  unfold myRemoveSpaces myRemoveSpacesImp
  rw [String.foldl_eq]
  simpa using (myRemoveSpacesImp_aux s.data "").symm




end MyRemoveSpaces