namespace HumanEval23

/--
Return length of given string
-/
def strlen (string : String) : Nat :=
  string.length

/-- Specification for strlen: returns the length of the input string -/
def strlen_spec (string : String) : Nat :=
  string.length

/-- strlen satisfies its specification -/
theorem strlen_correct (string : String) : strlen string = strlen_spec string := by
  unfold strlen
  unfold strlen_spec
  simp

/-- Tests for strlen -/
def strlen_tests : List (String × Nat) := [
  ("", 0),
  ("x", 1),
  ("asdasnakj", 9)
]

/-- Verify that strlen passes all tests -/
theorem strlen_passes_tests : ∀ (test : String × Nat), test ∈ strlen_tests → strlen test.1 = test.2 := by
  intro test test_in_tests
  cases test with
  | mk s expected =>
    simp [strlen]

end HumanEval23
