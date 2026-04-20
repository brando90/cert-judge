import Mathlib

namespace HowManyTimes


def how_many_times (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    string.length + 1
  else if substring.length > string.length then
    0
  else
    let rec aux (pos : Nat) (acc : Nat) : Nat :=
      if pos + substring.length > string.length then
        acc
      else
        let match_here := string.extract ⟨pos⟩ ⟨pos + substring.length⟩ = substring
        aux (pos + 1) (if match_here then acc + 1 else acc)
    aux 0 0


def how_many_times_imp (string : String) (substring : String) : Nat :=
  if substring.isEmpty then
    string.length + 1
  else if substring.length > string.length then
    0
  else
    let mut count := 0
    let mut pos := 0
    while pos + substring.length ≤ string.length do
      if string.extract ⟨pos⟩ ⟨pos + substring.length⟩ = substring then
        count := count + 1
      pos := pos + 1
    count



/-!
# Tests
-/

/-- expected: 0 -/
example : how_many_times "" "a" = 0 := by native_decide
#eval how_many_times "" "a" -- expected: 0

/-- expected: 3 -/
example : how_many_times "aaa" "a" = 3 := by native_decide
#eval how_many_times "aaa" "a" -- expected: 3

/-!
# Tests: Edge Cases
-/

/-- expected: 1 -/
example : how_many_times "" "" = 1 := by native_decide
#eval how_many_times "" "" -- expected: 1

/-- expected: 3 -/
example : how_many_times "aaaa" "aa" = 3 := by native_decide
#eval how_many_times "aaaa" "aa" -- expected: 3

/-- expected: 4 -/
example : how_many_times "xyxyxyx" "x" = 4 := by native_decide
#eval how_many_times "xyxyxyx" "x" -- expected: 4

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: overlapping matches -/
example : how_many_times "cacacacac" "cac" = 4 := by native_decide
#eval how_many_times "cacacacac" "cac" -- expected: 4

/-- positive: single occurrence -/
example : how_many_times "john doe" "john" = 1 := by native_decide
#eval how_many_times "john doe" "john" -- expected: 1

/-- negative: substring longer than string -/
example : ¬ (how_many_times "abc" "abcd" > 0) := by native_decide
#eval (decide (how_many_times "abc" "abcd" > 0)) -- expected: false

/-- positive: empty substring matches at every position -/
example : how_many_times "a" "" = 2 := by native_decide
#eval how_many_times "a" "" -- expected: 2

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: empty string -/
example : how_many_times_imp "" "a" = 0 := by native_decide
#eval how_many_times_imp "" "a" -- expected: 0

/-- positive: empty string with empty substring matches once -/
example : how_many_times_imp "" "" = 1 := by native_decide
#eval how_many_times_imp "" "" -- expected: 1

/-- positive: empty substring matches at every position -/
example : how_many_times_imp "a" "" = 2 := by native_decide
#eval how_many_times_imp "a" "" -- expected: 2

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem how_many_times_equivalence_thm (string substring : String) :
  how_many_times string substring = how_many_times_imp string substring := sorry




end HowManyTimes