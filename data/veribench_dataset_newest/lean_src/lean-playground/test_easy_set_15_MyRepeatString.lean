import Mathlib

namespace MyRepeatString


def myRepeatString (s : String) (n : Nat) : String :=
  match n with
  | 0 => ""
  | n + 1 => s ++ myRepeatString s n


def myRepeatStringImp (s : String) (n : Nat) : String :=
  (List.range n).foldl (fun acc _ => acc ++ s) ""



/-!
# Unit Tests
-/

/-- expected: "abcabcabc" -/
example : myRepeatString "abc" 3 = "abcabcabc" := by native_decide
#eval myRepeatString "abc" 3 -- expected: "abcabcabc"

/-- expected: "" (edge cases)-/
example : myRepeatString "hello" 0 = "" := by native_decide
#eval myRepeatString "hello" 0 -- expected: ""

/-- expected: "xxxxx" -/
example : myRepeatString "x" 5 = "xxxxx" := by native_decide
#eval myRepeatString "x" 5 -- expected: "xxxxx"

/-!
# Positive / Negative Test-Suite
-/

/-- positive: single repetition gives original -/
example : myRepeatString "test" 1 = "test" := by native_decide
#eval myRepeatString "test" 1 -- expected: "test"

/-- positive: empty string repeated gives empty -/
example : myRepeatString "" 5 = "" := by native_decide
#eval myRepeatString "" 5 -- expected: ""

/-- positive: larger repetition -/
example : myRepeatString "ab" 4 = "abababab" := by native_decide
#eval myRepeatString "ab" 4 -- expected: "abababab"

/-- negative: zero repetitions should not give original (unless original is empty) -/
example : ¬ (myRepeatString "test" 0 = "test") := by native_decide
#eval (decide (myRepeatString "test" 0 = "test")) -- expected: false

/-- negative: repetition should not be shorter than expected -/
example : ¬ (myRepeatString "ab" 3).length < 6 := by
  native_decide

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single repetition gives original -/
example : myRepeatStringImp "test" 1 = "test" := by native_decide
#eval myRepeatStringImp "test" 1 -- expected: "test"

/-- negative: zero repetitions should not give original (unless original is empty) -/
example : ¬ (myRepeatStringImp "test" 0 = "test") := by native_decide
#eval (decide (myRepeatStringImp "test" 0 = "test")) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem repeat_foldl_aux (xs : List Nat) (s acc : String) :
    xs.foldl (fun acc _ => acc ++ s) acc = acc ++ myRepeatString s xs.length := by
  induction xs generalizing acc with
  | nil =>
      simp [myRepeatString]
  | cons x xs ih =>
      simp [ih, myRepeatString, String.append_assoc]

theorem myRepeatString_equivalence_thm (s : String) (n : Nat) :
  myRepeatString s n = myRepeatStringImp s n := by
  unfold myRepeatStringImp
  simpa [List.length_range', String.append_assoc] using
    (repeat_foldl_aux (List.range' 0 n) s "").symm




end MyRepeatString