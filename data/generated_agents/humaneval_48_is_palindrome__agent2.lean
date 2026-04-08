```lean
import Std.Tactic.Basic

/--
  Checks if given string is a palindrome
-/
def is_palindrome (text : String) : Bool :=
  List.all (fun i => text.get? i = text.get? (text.length - 1 - i)) (List.range text.length)

/-- Tests for is_palindrome -/
def is_palindrome_test : IO Unit := do
  assert $ is_palindrome "" == true
  assert $ is_palindrome "aba" == true
  assert $ is_palindrome "aaaaa" == true
  assert $ is_palindrome "zbcd" == false
  assert $ is_palindrome "xywyx" == true
  assert $ is_palindrome "xywyz" == false
  assert $ is_palindrome "xywzx" == false

/-- Specification for is_palindrome -/
def is_palindrome_spec (text : String) : Bool :=
  let chars := text.toList
  chars == chars.reverse

/-- Lemma about the equivalence of the implementation and specification -/
theorem is_palindrome_correct (text : String) : is_palindrome text = is_palindrome_spec text := by
  sorry
```
