/-!

# VeriBench – All Prefixes

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## All Prefixes

Implements `all_prefixes`, which generates all prefixes of a string.-/

namespace AllPrefixes

/--
**Implementation of `all_prefixes`.**

Returns a list of all prefixes from shortest to longest of the input string.
The prefixes are ordered from shortest to longest, and include the full string
as the last element.

## Examples

#eval all_prefixes "abc" -- expected: ["a", "ab", "abc"]
#eval all_prefixes "" -- expected: []
#eval all_prefixes "WWW" -- expected: ["W", "WW", "WWW"]
-/
def all_prefixes (s : String) : List String :=
  let rec build_prefixes (n : Nat) (fuel : Nat) : List String :=
    match fuel with
    | 0 => []
    | fuel'+1 =>
      if n > s.length then []
      else (s.take n) :: build_prefixes (n+1) fuel'
  build_prefixes 1 (s.length)

/-!
# Tests
-/

/-- expected: ["a", "ab", "abc"] -/
example : all_prefixes "abc" = ["a", "ab", "abc"] := by sorry
#eval all_prefixes "abc"

/-- expected: [] -/
example : all_prefixes "" = [] := by sorry
#eval all_prefixes ""

/-!
# Tests: Edge Cases
-/

/-- expected: ["W", "WW", "WWW"] -/
example : all_prefixes "WWW" = ["W", "WW", "WWW"] := by sorry
#eval all_prefixes "WWW"

/-- expected: ["a"] -/
example : all_prefixes "a" = ["a"] := by sorry
#eval all_prefixes "a"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: two characters -/
example : all_prefixes "xy" = ["x", "xy"] := by sorry
#eval all_prefixes "xy" -- expected: ["x", "xy"]

/-- positive: longer string -/
example : all_prefixes "Hello" = ["H", "He", "Hel", "Hell", "Hello"] := by sorry
#eval all_prefixes "Hello" -- expected: ["H", "He", "Hel", "Hell", "Hello"]

/-- negative: empty string doesn't produce single character -/
example : ¬ (all_prefixes "" = ["a"]) := by sorry
#eval (decide (all_prefixes "" = ["a"])) -- expected: false

/-- negative: doesn't include suffixes -/
example : ¬ (all_prefixes "abc" = ["a", "ab", "abc", "bc", "c"]) := by sorry
#eval (decide (all_prefixes "abc" = ["a", "ab", "abc", "bc", "c"])) -- expected: false

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any string is valid input. -/
def Pre (s : String) : Prop := True

/-!
# Property Theorems
-/

/-- **Empty string property**: Empty string returns empty list. -/
def empty_string_prop : Prop := all_prefixes "" = []

/-- **Empty string theorem**: Empty string returns empty list. -/
@[simp] theorem empty_string_thm : empty_string_prop := sorry

/-- **Single character property**: Single character returns list with that character. -/
def single_char_prop (c : Char) : Prop := all_prefixes (String.mk [c]) = [String.mk [c]]

/-- **Single character theorem**: Single character returns list with that character. -/
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := sorry

/-- **Length bound property**: Number of prefixes is at most string length. -/
def length_bound_prop (s : String) : Prop := (all_prefixes s).length ≤ s.length

/-- **Length bound theorem**: Number of prefixes is at most string length. -/
@[simp] theorem length_bound_thm (s : String) : length_bound_prop s := sorry

/-- **Prefix validity property**: All returned strings are actual prefixes. -/
def prefix_validity_prop (s : String) : Prop :=
  ∀ p ∈ all_prefixes s, ∃ n, s.take n = p

/-- **Prefix validity theorem**: All returned strings are actual prefixes. -/
@[simp] theorem prefix_validity_thm (s : String) : prefix_validity_prop s := sorry

/-- **Ordering property**: Prefixes are ordered by increasing length. -/
def ordering_prop (s : String) : Prop :=
  ∀ i j, i < j → j < (all_prefixes s).length →
  (all_prefixes s)[i]!.length < (all_prefixes s)[j]!.length

/-- **Ordering theorem**: Prefixes are ordered by increasing length. -/
@[simp] theorem ordering_thm (s : String) : ordering_prop s := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for all_prefixes. -/
def Post_prop (s : String) : Prop :=
  (empty_string_prop) ∧                                  -- empty_string_prop
  (∀ c, single_char_prop c) ∧                            -- single_char_prop
  (length_bound_prop s) ∧                                -- length_bound_prop
  (prefix_validity_prop s) ∧                             -- prefix_validity_prop
  (ordering_prop s)                                      -- ordering_prop

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (s : String) (hPre : Pre s) : Post_prop s := sorry

/-!
# Imperative Implementation
-/

/--
`all_prefixesImp s` computes the same result using imperative style with explicit loops.

Generates all prefixes of a string using an imperative
approach with explicit loops.
-/
def all_prefixesImp (s : String) : List String :=
  Id.run do
    let mut result := []
    for i in [1:s.length + 1] do
      result := result ++ [s.take i]
    return result

/-!
# Imperative Tests
-/

/-- expected: ["a", "ab", "abc"] -/
example : all_prefixesImp "abc" = ["a", "ab", "abc"] := by sorry
#eval all_prefixesImp "abc"

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: [] -/
example : all_prefixesImp "" = [] := by sorry
#eval all_prefixesImp ""

/-- expected: ["W", "WW", "WWW"] -/
example : all_prefixesImp "WWW" = ["W", "WW", "WWW"] := by sorry
#eval all_prefixesImp "WWW"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: numbers -/
example : all_prefixesImp "123" = ["1", "12", "123"] := by sorry
#eval all_prefixesImp "123" -- expected: ["1", "12", "123"]

/-- negative: doesn't produce empty prefix for non-empty string -/
example : ¬ (all_prefixesImp "a" = ["", "a"]) := by sorry
#eval (decide (all_prefixesImp "a" = ["", "a"])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem all_prefixes_equivalence_thm (s : String) :
  all_prefixes s = all_prefixesImp s := sorry

end AllPrefixes
