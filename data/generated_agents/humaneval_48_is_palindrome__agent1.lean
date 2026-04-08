import VeriBench.Common
import Lean
import Std.Data.List.Basic
open Std

/-- 
Checks if given string is a palindrome
-/
def isPalindrome (text : String) : Bool :=
  let chars := text.toList
  let len := chars.length
  List.foldrMaup
    (fun i acc => 
      if i >= len / 2 then 
        acc 
      else if chars.get! i != chars.get! (len - 1 - i) then 
        false 
      else 
        acc)
    true
    (List.range len)

/-- 
Specification: isPalindrome returns true if the string reads the same forwards and backwards.
-/
def isPalindromeSpec (text : String) : Bool :=
  text.toList = text.toList.reverse

theorem isPalindrome_correct (text : String) : 
  isPalindrome text = isPalindromeSpec text := sorry

/-! ## Test Cases -/

#eval isPalindrome "" -- Expected: true
#eval isPalindrome "aba" -- Expected: true
#eval isPalindrome "aaaaa" -- Expected: true
#eval isPalindrome "zbcd" -- Expected: false
#eval isPalindrome "xywyx" -- Expected: true
#eval isPalindrome "xywyz" -- Expected: false
#eval isPalindrome "xywzx" -- Expected: false

/-- Test that the implementation passes all the test cases. -/
theorem isPalindrome_tests : 
  isPalindrome "" = true ∧
  isPalindrome "aba" = true ∧
  isPalindrome "aaaaa" = true ∧
  isPalindrome "zbcd" = false ∧
  isPalindrome "xywyx" = true ∧
  isPalindrome "xywyz" = false ∧
  isPalindrome "xywzx" = false := by
  simp [isPalindrome]
  sorry
