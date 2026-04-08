import Batteries

/-- Test if given string is a palindrome -/
def is_palindrome (string : String) : Bool :=
  string == string.reverse

/-- 
  Find the shortest palindrome that begins with a supplied string.
  Algorithm idea is simple:
  - Find the longest postfix of supplied string that is a palindrome.
  - Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
-/
def make_palindrome (string : String) : String :=
  if string.isEmpty then
    ""
  else
    let rec find_palindrome_suffix (beginning_of_suffix : Nat) : String :=
      if is_palindrome (string.extract beginning_of_suffix string.length) then
        string ++ (string.extract 0 beginning_of_suffix).reverse
      else
        find_palindrome_suffix (beginning_of_suffix + 1)
    find_palindrome_suffix 0

/-- Tests for make_palindrome -/
def make_palindrome_test : IO Unit := do
  assert! (make_palindrome "" == "")
  assert! (make_palindrome "x" == "x")
  assert! (make_palindrome "xyz" == "xyzyx")
  assert! (make_palindrome "xyx" == "xyx")
  assert! (make_palindrome "jerry" == "jerryrrej")
  IO.println "All tests passed!"

/-- Specification: The result of make_palindrome should be a palindrome -/
def make_palindrome_post (string : String) (result : String) : Prop :=
  is_palindrome result

/-- Specification: The result of make_palindrome should start with the input string -/
def make_palindrome_post_prefix (string : String) (result : String) : Prop :=
  result.startsWith string

/-- Specification: The result of make_palindrome should be the shortest palindrome starting with the input string -/
def make_palindrome_post_shortest (string : String) (result : String) : Prop :=
  ∀ (s : String), is_palindrome s → s.startsWith string → result.length ≤ s.length

/-- Theorem: make_palindrome produces a palindrome -/
theorem make_palindrome_correct (string : String) : 
  make_palindrome_post string (make_palindrome string) := sorry

/-- Theorem: make_palindrome result starts with the input string -/
theorem make_palindrome_correct_prefix (string : String) : 
  make_palindrome_post_prefix string (make_palindrome string) := sorry

/-- Theorem: make_palindrome produces the shortest palindrome starting with the input string -/
theorem make_palindrome_correct_shortest (string : String) : 
  make_palindrome_post_shortest string (make_palindrome string) := sorry
