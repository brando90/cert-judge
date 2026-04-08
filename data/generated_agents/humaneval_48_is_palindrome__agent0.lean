```lean
/- VeriBench problem: HumanEval/48 -/

/--
  Checks if given string is a palindrome
-/

def isPalindrome (text : String) : Bool := 
  let rec checkPalindrome (s : String) (i : Nat) : Bool :=
    if i >= s.length / 2 then
      true
    else if s.get! i != s.get! (s.length - 1 - i) then
      false
    else
      checkPalindrome s (i + 1)
  checkPalindrome text 0

/-- Tests for isPalindrome -/
def isPalindromeTests : List (String × Bool) := [
  ("", true),
  ("aba", true),
  ("aaaaa", true),
  ("zbcd", false),
  ("xywyx", true),
  ("xywyz", false),
  ("xywzx", false)
]

/-- Run the tests -/
def runIsPalindromeTests : IO Unit := do
  for (input, expected) in isPalindromeTests do
    let result := isPalindrome input
    if result != expected then
      throw (IO.userError s!"Test failed for input '{input}': expected {expected}, got {result}")
    IO.println s!"Test passed for input '{input}'"
  IO.println "All tests passed!"

/-- Specification for isPalindrome -/
def isPalindromeSpec (text : String) : Bool :=
  let rec allMatch (i : Nat) : Bool :=
    if i >= text.length / 2 then
      true
    else if text.get! i != text.get! (text.length - 1 - i) then
      false
    else
      allMatch (i + 1)
  allMatch 0

/-- Correctness theorem for isPalindrome -/
theorem isPalindrome_correct (text : String) : isPalindrome text = isPalindromeSpec text := by
  sorry

#eval runIsPalindromeTests
```
