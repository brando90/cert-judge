import Mathlib

namespace LongestString


def longest (strings : List String) : Option String :=
  match strings with
  | [] => none
  | xs =>
    let maxlen := xs.map String.length |>.maximum?.getD 0
    xs.find? (fun s => s.length = maxlen)


def longestImp (strings : List String) : Option String :=
  match strings with
  | [] => none
  | head :: tail =>
    let rec loop (current : String) (remaining : List String) : String :=
      match remaining with
      | [] => current
      | x :: xs => 
        if x.length > current.length then loop x xs
        else if x.length = current.length then loop current xs
        else loop current xs
    some (loop head tail)



/-!
# Tests
-/

/-- expected: none -/
example : longest [] = none := by native_decide
#eval longest []

/-- expected: some "x" -/
example : longest ["x", "y", "z"] = some "x" := by native_decide
#eval longest ["x", "y", "z"]

/-!
# Tests: Edge Cases
-/

/-- expected: some "zzzz" -/
example : longest ["x", "yyy", "zzzz", "www", "kkkk", "abc"] = some "zzzz" := by native_decide
#eval longest ["x", "yyy", "zzzz", "www", "kkkk", "abc"]

/-- expected: some "ccc" -/
example : longest ["a", "bb", "ccc"] = some "ccc" := by native_decide
#eval longest ["a", "bb", "ccc"]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: equal length strings return first -/
example : longest ["abc", "def", "ghi"] = some "abc" := by native_decide
#eval longest ["abc", "def", "ghi"] -- expected: some "abc"

/-- positive: empty strings handled -/
example : longest ["", "a", "bb"] = some "bb" := by native_decide
#eval longest ["", "a", "bb"] -- expected: some "bb"

/-- negative: empty list doesn't return first element -/
example : ¬ (longest [] = some "") := by native_decide
#eval (decide (longest [] = some "")) -- expected: false

/-- negative: doesn't return shorter string when longer exists -/
example : ¬ (longest ["short", "verylongstring"] = some "short") := by native_decide
#eval (decide (longest ["short", "verylongstring"] = some "short")) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single element -/
example : longestImp ["hello"] = some "hello" := by native_decide
#eval longestImp ["hello"] -- expected: some "hello"

/-- negative: empty list doesn't return something -/
example : ¬ ((longestImp []).isSome) := by native_decide
#eval (decide ((longestImp []).isSome)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem longest_equivalence_thm (strings : List String) :
  longest strings = longestImp strings := sorry




end LongestString