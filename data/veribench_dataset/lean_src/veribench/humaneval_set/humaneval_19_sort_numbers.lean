/-!

# VeriBench – Sort Numbers

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

## Sort Numbers

Implements `sort_numbers`, which processes a space-delimited string of number words.-/

namespace SortNumbers

/--
Helper function to convert a word representation of a number to its numeric value.
Supports words like "zero", "one", "two", etc. up to "nine".
Returns the corresponding natural number.

## Examples
#eval wordToNum "zero" -- expected: 0
#eval wordToNum "one" -- expected: 1
-/
def wordToNum (word : String) : Nat :=
  match word with
  | "zero"  => 0
  | "one"   => 1
  | "two"   => 2
  | "three" => 3
  | "four"  => 4
  | "five"  => 5
  | "six"   => 6
  | "seven" => 7
  | "eight" => 8
  | "nine"  => 9
  | _       => 0

/--
**Implementation of `sort_numbers`.**

Given a space-delimited string of numerals from 'zero' to 'nine',
returns the string with numbers in their original order.

Valid input words are: 'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'.

## Examples

#eval sort_numbers "three five nine" -- expected: "three five nine"
#eval sort_numbers "five zero four" -- expected: "five zero four"
-/
def sort_numbers (numbers : String) : String :=
  if numbers = "" then
    ""
  else
    let words := String.splitOn numbers " "
    let nonEmpty := words.filter (· ≠ "")
    String.intercalate " " nonEmpty

/-!
# Tests
-/

/-- expected: "" -/
example : sort_numbers "" == "" := by sorry
#eval sort_numbers ""

/-- expected: "three" -/
example : sort_numbers "three" == "three" := by sorry
#eval sort_numbers "three"

/-!
# Tests: Edge Cases
-/

/-- expected: "three five nine" -/
example : sort_numbers "three five nine" == "three five nine" := by sorry
#eval sort_numbers "three five nine"

/-- expected: "five zero four seven nine eight" -/
example : sort_numbers "five zero four seven nine eight" == "five zero four seven nine eight" := by sorry
#eval sort_numbers "five zero four seven nine eight"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: handles extra spaces -/
example : sort_numbers "  one  two  three  " == "one two three" := by sorry
#eval sort_numbers "  one  two  three  " -- expected: "one two three"

/-- positive: single word -/
example : sort_numbers "zero" == "zero" := by sorry
#eval sort_numbers "zero" -- expected: "zero"

/-- negative: empty string doesn't produce words -/
example : ¬ (sort_numbers "" == "zero") := by sorry
#eval (decide (sort_numbers "" == "zero")) -- expected: false

/-- negative: preserves original order -/
example : ¬ (sort_numbers "nine one" == "one nine") := by sorry
#eval (decide (sort_numbers "nine one" == "one nine")) -- expected: false

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any string is valid input. -/
def Pre (numbers : String) : Prop := True

/-!
# Property Theorems
-/

/-- **Empty string property**: Empty string returns empty string. -/
def empty_string_prop : Prop := sort_numbers "" = ""

/-- **Empty string theorem**: Empty string returns empty string. -/
@[simp] theorem empty_string_thm : empty_string_prop := sorry

/-- **Order preservation property**: Original order is preserved. -/
def order_preservation_prop (numbers : String) : Prop :=
  let words := String.splitOn (sort_numbers numbers) " "
  let inputWords := (String.splitOn numbers " ").filter (· ≠ "")
  words = inputWords

/-- **Order preservation theorem**: Original order is preserved. -/
@[simp] theorem order_preservation_thm (numbers : String) : order_preservation_prop numbers := sorry

/-- **Idempotent property**: Applying twice gives same result as once. -/
def idempotent_prop (numbers : String) : Prop :=
  sort_numbers (sort_numbers numbers) = sort_numbers numbers

/-- **Idempotent theorem**: Applying twice gives same result as once. -/
@[simp] theorem idempotent_thm (numbers : String) : idempotent_prop numbers := sorry

/-- **Space normalization property**: Extra spaces are normalized. -/
def space_normalization_prop : Prop :=
  sort_numbers "  one  two  " = "one two"

/-- **Space normalization theorem**: Extra spaces are normalized. -/
@[simp] theorem space_normalization_thm : space_normalization_prop := sorry

/-- **Single word property**: Single word is preserved. -/
def single_word_prop (word : String) : Prop :=
  word ≠ "" → sort_numbers word = word

/-- **Single word theorem**: Single word is preserved. -/
@[simp] theorem single_word_thm (word : String) : single_word_prop word := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for sort_numbers. -/
def Post_prop (numbers : String) : Prop :=
  (empty_string_prop) ∧                                  -- empty_string_prop
  (order_preservation_prop numbers) ∧                    -- order_preservation_prop
  (idempotent_prop numbers) ∧                            -- idempotent_prop
  (space_normalization_prop) ∧                           -- space_normalization_prop
  (∀ word, single_word_prop word)                        -- single_word_prop

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (numbers : String) (hPre : Pre numbers) : Post_prop numbers := sorry

/-!
# Imperative Implementation
-/

/--
`sort_numbersImp numbers` computes the same result using imperative style with explicit loops.
-/
def sort_numbersImp (numbers : String) : String :=
  Id.run do
    if numbers = "" then
      return ""
    let words := String.splitOn numbers " "
    let mut result : List String := []
    for word in words do
      if word ≠ "" then
        result := result ++ [word]
    return String.intercalate " " result

/-!
# Imperative Tests
-/

/-- expected: "" -/
example : sort_numbersImp "" == "" := by sorry
#eval sort_numbersImp ""

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: "three" -/
example : sort_numbersImp "three" == "three" := by sorry
#eval sort_numbersImp "three"

/-- expected: "three five nine" -/
example : sort_numbersImp "three five nine" == "three five nine" := by sorry
#eval sort_numbersImp "three five nine"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: space handling -/
example : sort_numbersImp "  one  two  " == "one two" := by sorry
#eval sort_numbersImp "  one  two  " -- expected: "one two"

/-- negative: doesn't reorder -/
example : ¬ (sort_numbersImp "five one" == "one five") := by sorry
#eval (decide (sort_numbersImp "five one" == "one five")) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem sort_numbers_equivalence_thm (numbers : String) :
  sort_numbers numbers = sort_numbersImp numbers := sorry

end SortNumbers
