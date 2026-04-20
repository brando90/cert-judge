-- !benchmark @start import type=solution
import Mathlib
namespace ReverseWords
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Helper function: reverses a string by reversing its list of characters. -/
def reverseString (s : String) : String :=
  String.mk (s.data.reverse)
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def reverseWords_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def reverseWords (s : String) (h_precond : reverseWords_precond (s)) : String :=
  -- !benchmark @start code
  String.intercalate " " ((s.splitOn " ").map reverseString)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def reverseWords_postcond (s : String) (result : String) (h_precond : reverseWords_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (result = String.intercalate " " ((s.splitOn " ").map reverseString))
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Empty string property**: Empty string remains empty. -/
def empty_string_prop : Prop := reverseWords "" (by simp) = ""

/-- **Empty string theorem**: Empty string remains empty. -/
@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

/-- **Single word property**: Single word gets reversed. -/
def single_word_prop (w : String) : Prop :=
  ¬w.contains ' ' → reverseWords w (by simp) = reverseString w

/-- **Single word theorem**: Single word gets reversed. -/
@[simp] theorem single_word_thm (w : String) : single_word_prop w := by
  sorry

/-- **Word count preservation property**: Number of words preserved. -/
def word_count_prop (s : String) : Prop :=
  ((reverseWords s (by simp)).splitOn " ").length = (s.splitOn " ").length

/-- **Word count preservation theorem**: Number of words preserved. -/
@[simp] theorem word_count_thm (s : String) : word_count_prop s := by
  sorry

/-- **Length preservation property**: String length is preserved. -/
def length_preservation_prop (s : String) : Prop :=
  (reverseWords s (by simp)).length = s.length

/-- **Length preservation theorem**: String length is preserved. -/
@[simp] theorem length_preservation_thm (s : String) : length_preservation_prop s := by
  sorry

/-- **Word order property**: Words appear in same order. -/
def word_order_prop (s : String) : Prop :=
  let words := s.splitOn " "
  let revWords := (reverseWords s (by simp)).splitOn " "
  words.length = revWords.length ∧ ∀ i < words.length,
    (words[i]?).isSome → (revWords[i]?) = (words[i]?).map reverseString

/-- **Word order theorem**: Words appear in same order. -/
@[simp] theorem word_order_thm (s : String) : word_order_prop s := by
  sorry
-- !benchmark @end proof_aux

theorem reverseWords_spec_satisfied (s : String) (h_precond : reverseWords_precond (s)) :
    reverseWords_postcond (s) (reverseWords (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof