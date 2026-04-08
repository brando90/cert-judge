```lean
import Lean.Data.RBMap
import Mathlib.Data.String.Basic
import Mathlib.Data.Set.Basic

/-- Remove lowercase letters a-e from a string.

Edge cases:
- Empty string returns empty string.
- Non-string input is invalid and raises ValueError. -/

/-- Precondition for `remove_abcde` -/
def pre (s : String) : Prop := True

/-- Return a new string with all lowercase letters 'a', 'b', 'c', 'd', 'e' removed. -/
def remove_abcde (s : String) : String :=
  s.foldl (fun acc c => 
    if c = 'a' || c = 'b' || c = 'c' || c = 'd' || c = 'e' then
      acc
    else
      acc.push c) ""

/-- Postcondition for `remove_abcde` -/
def post (s : String) (result : String) : Prop :=
  let letters_to_remove : Char → Prop := fun c => c = 'a' || c = 'b' || c = 'c' || c = 'd' || c = 'e'
  ∀ c, c ∈ result.data → c ∈ s.data ∧ ¬letters_to_remove c

/-- Tests for `remove_abcde` -/
def remove_abcde_test : IO Unit := do
  -- Basic test
  assert! (remove_abcde "alphabet" = "lpht")
  -- Edge case
  assert! (remove_abcde "" = "")
  -- Additional tests
  assert! (remove_abcde "ABCDEabcde" = "ABCDE")
  assert! (remove_abcde "xyz" = "xyz")
  IO.println "All tests passed!"

/-- Correctness theorem for `remove_abcde` -/
theorem remove_abcde_correct (s : String) (h : pre s) :
  post s (remove_abcde s) := by
  sorry
```
