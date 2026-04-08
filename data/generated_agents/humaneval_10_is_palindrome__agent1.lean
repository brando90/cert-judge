import Std.Data.String.Basic
import Std.Tactic.SeqFocus

/-- Test if given string is a palindrome -/
def is_palindrome (string : String) : Bool :=
  string == string.reverse

/-- Find the shortest palindrome that begins with a supplied string.
Algorithm idea is simple:
- Find the longest postfix of supplied string that is a palindrome.
- Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
-/
def make_palindrome (string : String) : String :=
  if string = "" then
    ""
  else
    let rec find_suffix (beginning_of_suffix : Nat) : String :=
      if is_palindrome (string.drop beginning_of_suffix) then
        string ++ (string.take beginning_of_suffix).reverse
      else
        find_suffix (beginning_of_suffix + 1)
    find_suffix 0

/-- Specification for make_palindrome: The result is a palindrome -/
def make_palindrome_post (string : String) (result : String) : Prop :=
  is_palindrome result = true

/-- Specification for make_palindrome: The result starts with the input string -/
def make_palindrome_post_prefix (string : String) (result : String) : Prop :=
  result.take string.length = string

/-- Tests for make_palindrome -/
theorem make_palindrome_test : 
  make_palindrome "" = "" ∧
  make_palindrome "x" = "x" ∧
  make_palindrome "xyz" = "xyzyx" ∧
  make_palindrome "xyx" = "xyx" ∧
  make_palindrome "jerry" = "jerryrrej" := by
  decide

/-- Correctness theorem for make_palindrome -/
theorem make_palindrome_correct (string : String) : 
  make_palindrome_post string (make_palindrome string) ∧
  make_palindrome_post_prefix string (make_palindrome string) := by
  sorry
