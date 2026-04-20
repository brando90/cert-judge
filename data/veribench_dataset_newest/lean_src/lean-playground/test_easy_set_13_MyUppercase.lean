import Mathlib

namespace MyUppercase


def toUpper (c : Char) : Char :=
  c.toUpper


def myUppercase (s : String) : String :=
  s.map toUpper


def myUppercaseImp (s : String) : String :=
  Id.run do
    let mut result := ""
    for c in s.data do
      result := result ++ String.mk [toUpper c]
    return result

/-!
# Tests
-/

/-- expected: "HELLO" -/
example : myUppercase "hello" = "HELLO" := by native_decide
#eval myUppercase "hello" -- expected: "HELLO"

/-- expected: "HELLO, WORLD!" -/
example : myUppercase "Hello, World!" = "HELLO, WORLD!" := by native_decide
#eval myUppercase "Hello, World!" -- expected: "HELLO, WORLD!"

/-!
# Tests: Edge Cases
-/

/-- expected: "123!@#" (non-alphabetic preserved) -/
example : myUppercase "123!@#" = "123!@#" := by native_decide
#eval myUppercase "123!@#" -- expected: "123!@#"

/-- expected: "" (empty string) -/
example : myUppercase "" = "" := by native_decide
#eval myUppercase "" -- expected: ""

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: converts mixed case -/
example : myUppercase "aBcDeF" = "ABCDEF" := by native_decide
#eval myUppercase "aBcDeF" -- expected: "ABCDEF"

/-- positive: preserves already uppercase -/
example : myUppercase "HELLO" = "HELLO" := by native_decide
#eval myUppercase "HELLO" -- expected: "HELLO"

/-- negative: should not change non-alphabetic characters -/
example : ¬ (myUppercase "123" ≠ "123") := by native_decide
#eval (decide (myUppercase "123" ≠ "123")) -- expected: false

/-- negative: applying twice should be same as once -/
example : ¬ (myUppercase (myUppercase "hello") ≠ myUppercase "hello") := by native_decide
#eval (decide (myUppercase (myUppercase "hello") ≠ myUppercase "hello")) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: maintains uppercase computation -/
example : myUppercaseImp "test" = "TEST" := by
  unfold myUppercaseImp
  simp
  rfl
#eval myUppercaseImp "test" -- expected: "TEST"

/-- negative: non-alphabetic should remain unchanged -/
example : ¬ (myUppercaseImp "123" ≠ "123") := by native_decide
#eval (decide (myUppercaseImp "123" ≠ "123")) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem myUppercaseImp_aux (cs : List Char) (acc : String) :
    Id.run (do
      let mut result := acc
      for c in cs do
        result := result ++ String.mk [toUpper c]
      return result) = acc ++ String.mk (cs.map toUpper) := by
  induction cs generalizing acc with
  | nil =>
      simp
  | cons c cs ih =>
      calc
        Id.run (do
          let mut result := acc
          for c in c :: cs do
            result := result ++ String.mk [toUpper c]
          return result) =
            Id.run (do
              let mut result := acc ++ String.mk [toUpper c]
              for c in cs do
                result := result ++ String.mk [toUpper c]
              return result) := by
                simp
        _ = (acc ++ String.mk [toUpper c]) ++ String.mk (cs.map toUpper) := ih (acc ++ String.mk [toUpper c])
        _ = acc ++ String.mk ((c :: cs).map toUpper) := by
              apply String.ext
              simp [String.data_append, List.map, List.append_assoc]

theorem myUppercase_equivalence_thm (s : String) :
  myUppercase s = myUppercaseImp s := by
  unfold myUppercase myUppercaseImp
  rw [String.map_eq]
  simpa using (myUppercaseImp_aux s.data "").symm




end MyUppercase