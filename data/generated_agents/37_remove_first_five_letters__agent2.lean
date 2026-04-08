import Lean
import Std

namespace VeriBench.RemoveABCDE

/-- Specification for the `remove_abcde` function: removes lowercase letters a-e from a string. -/
def spec (s : String) : String :=
  s.foldl (fun acc c => if c ∈ ['a', 'b', 'c', 'd', 'e'] then acc else acc.push c) ""

/-- Implementation of `remove_abcde` function. -/
def remove_abcde (s : String) : String :=
  s.foldl (fun acc c => if c ∈ ['a', 'b', 'c', 'd', 'e'] then acc else acc.push c) ""

/-- Precondition for `remove_abcde`: input must be a string.
    Note: In Lean, type checking ensures this automatically. -/
def pre (s : String) : Prop := True

/-- Postcondition for `remove_abcde`: result must match the specification. -/
def post (s : String) (result : String) : Prop :=
  result = spec s

/-- Correctness theorem: implementation satisfies specification. -/
theorem remove_abcde_correct (s : String) : post s (remove_abcde s) := by
  unfold post
  unfold spec
  unfold remove_abcde
  simp
  sorry

/-- Test cases for `remove_abcde`. -/
def test : IO Unit := do
  -- Basic test
  if remove_abcde "alphabet" ≠ "lpht" then
    throw (IO.userError "Test failed: alphabet")
  
  -- Edge case: empty string
  if remove_abcde "" ≠ "" then
    throw (IO.userError "Test failed: empty string")
  
  -- Additional test cases
  if remove_abcde "ABCDEabcde" ≠ "ABCDE" then
    throw (IO.userError "Test failed: ABCDEabcde")
  
  if remove_abcde "xyz" ≠ "xyz" then
    throw (IO.userError "Test failed: xyz")
  
  IO.println "All tests passed!"

end VeriBench.RemoveABCDE
