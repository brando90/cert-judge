-- !benchmark @start import type=solution
import Mathlib
namespace SortNumbers
-- !benchmark @end import

-- !benchmark @start solution_aux
/--
Helper function to convert a word representation of a number to its numeric value.
Supports words like "zero", "one", "two", etc. up to "nine".
Returns the corresponding natural number.
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
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def sort_numbers_precond (numbers : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def sort_numbers (numbers : String) (h_precond : sort_numbers_precond (numbers)) : String :=
  -- !benchmark @start code
  if numbers = "" then
    ""
  else
    let words := String.splitOn numbers " "
    let nonEmpty := words.filter (· ≠ "")
    String.intercalate " " nonEmpty
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def sort_numbers_postcond (numbers : String) (result : String) (h_precond : sort_numbers_precond (numbers)) : Prop :=
  -- !benchmark @start postcond
  (sort_numbers "" (by simp) = "") ∧
    (let words := String.splitOn (sort_numbers numbers h_precond) " "
     let inputWords := (String.splitOn numbers " ").filter (· ≠ "")
     words = inputWords) ∧
    (sort_numbers (sort_numbers numbers h_precond) (by simp) = sort_numbers numbers h_precond) ∧
    (sort_numbers "  one  two  " (by simp) = "one two") ∧
    (∀ word, word ≠ "" → sort_numbers word (by simp) = word)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string returns empty string. -/
def empty_string_prop : Prop := sort_numbers "" (by simp) = ""

/-- **Empty string theorem**: Empty string returns empty string. -/
@[simp] theorem empty_string_thm : empty_string_prop := sorry

/-- **Order preservation property**: Original order is preserved. -/
def order_preservation_prop (numbers : String) : Prop :=
  let words := String.splitOn (sort_numbers numbers (by simp)) " "
  let inputWords := (String.splitOn numbers " ").filter (· ≠ "")
  words = inputWords

/-- **Order preservation theorem**: Original order is preserved. -/
@[simp] theorem order_preservation_thm (numbers : String) : order_preservation_prop numbers := sorry

/-- **Idempotent property**: Applying twice gives same result as once. -/
def idempotent_prop (numbers : String) : Prop :=
  sort_numbers (sort_numbers numbers (by simp)) (by simp) = sort_numbers numbers (by simp)

/-- **Idempotent theorem**: Applying twice gives same result as once. -/
@[simp] theorem idempotent_thm (numbers : String) : idempotent_prop numbers := sorry

/-- **Space normalization property**: Extra spaces are normalized. -/
def space_normalization_prop : Prop :=
  sort_numbers "  one  two  " (by simp) = "one two"

/-- **Space normalization theorem**: Extra spaces are normalized. -/
@[simp] theorem space_normalization_thm : space_normalization_prop := sorry

/-- **Single word property**: Single word is preserved. -/
def single_word_prop (word : String) : Prop :=
  word ≠ "" → sort_numbers word (by simp) = word

/-- **Single word theorem**: Single word is preserved. -/
@[simp] theorem single_word_thm (word : String) : single_word_prop word := sorry
-- !benchmark @end proof_aux

theorem sort_numbers_spec_satisfied (numbers : String) (h_precond : sort_numbers_precond (numbers)) :
    sort_numbers_postcond (numbers) (sort_numbers (numbers) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof