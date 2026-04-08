import Std.Data.List.Basic

/-- Tests if a given string is a palindrome -/
def is_palindrome (s : String) : Bool :=
  s == s.reverse

/-- Finds the shortest palindrome that begins with a supplied string.
    Algorithm idea is simple:
    - Find the longest postfix of supplied string that is a palindrome.
    - Append to the end of the string reverse of a string prefix that comes before the palindromic suffix.
-/
def make_palindrome (s : String) : String :=
  if s == "" then
    ""
  else
    let rec find_suffix (beginning_of_suffix : Nat) : String :=
      if is_palindrome (s.extract beginning_of_suffix s.length) then
        s ++ (s.extract 0 beginning_of_suffix).reverse
      else
        find_suffix (beginning_of_suffix + 1)
    find_suffix 0

/-- Tests for make_palindrome -/
def make_palindrome_test : IO Unit := do
  assert! (make_palindrome "" == "")
  assert! (make_palindrome "x" == "x")
  assert! (make_palindrome "xyz" == "xyzyx")
  assert! (make_palindrome "xyx" == "xyx")
  assert! (make_palindrome "jerry" == "jerryrrej")
  IO.println "All tests passed!"

/-- Specification: The result is a palindrome -/
def make_palindrome_post (s : String) (result : String) : Prop :=
  is_palindrome result = true

/-- Specification: The original string is a prefix of the result -/
def make_palindrome_post_prefix (s : String) (result : String) : Prop :=
  s.isPrefixOf result

/-- Specification: The result is the shortest palindrome starting with s -/
def make_palindrome_post_shortest (s : String) (result : String) : Prop :=
  ∀ (p : String), is_palindrome p = true → s.isPrefixOf p → result.length ≤ p.length

/-- Correctness theorem: make_palindrome satisfies its specification -/
theorem make_palindrome_correct (s : String) :
  let result := make_palindrome s
  make_palindrome_post s result ∧ 
  make_palindrome_post_prefix s result ∧
  make_palindrome_post_shortest s result := by
  sorry
