import Lean
import Std

namespace VeriBench.HumanEval14

/--
Returns a list of all prefixes from shortest to longest of the input string.
For example, `all_prefixes "abc"` returns `["a", "ab", "abc"]`.
-/
def all_prefixes (string : String) : List String :=
  let rec aux (i : Nat) (acc : List String) : List String :=
    if i ≥ string.length then
      acc.reverse
    else
      aux (i + 1) (string.extract 0 (i + 1) :: acc)
  aux 0 []

/-- Tests for `all_prefixes` function -/
def all_prefixes_test : IO Unit := do
  assert! (all_prefixes "" = [])
  assert! (all_prefixes "asdfgh" = ["a", "as", "asd", "asdf", "asdfg", "asdfgh"])
  assert! (all_prefixes "WWW" = ["W", "WW", "WWW"])
  IO.println "All tests passed!"

/--
Specification for `all_prefixes`:
For a string `s`, the result should contain all prefixes of `s` from shortest to longest.
-/
def all_prefixes_spec (string : String) (result : List String) : Prop :=
  -- The result should contain exactly the prefixes of the string
  result.length = string.length ∧
  ∀ i, 0 ≤ i → i < string.length → 
      result.get? i = some (string.extract 0 (i + 1))

/-- 
Theorem stating that `all_prefixes` satisfies its specification.
-/
theorem all_prefixes_correct (string : String) : 
  all_prefixes_spec string (all_prefixes string) := by
  sorry

end VeriBench.HumanEval14
