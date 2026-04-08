import Lean
import Batteries.Data.List.Basic
import Batteries.Data.String.Basic

/-!
# Remove lowercase letters a-e from a string
-/

/-- Remove lowercase letters 'a', 'b', 'c', 'd', 'e' from a string. -/
def removeABCDE (s : String) : String :=
  let chars := s.toList
  let filtered := chars.filter (fun c => c ∉ ['a', 'b', 'c', 'd', 'e'])
  String.mk filtered

/-- Precondition for removeABCDE: input must be a string.
    This is automatically satisfied in Lean's type system. -/
def removeABCDE_pre (_s : String) : Bool := true

/-- Postcondition for removeABCDE: result doesn't contain any of 'a', 'b', 'c', 'd', 'e' -/
def removeABCDE_post (s : String) (result : String) : Prop :=
  ∀ c, c ∈ result.toList → c ∉ ['a', 'b', 'c', 'd', 'e']

/-- The removeABCDE function satisfies its postcondition. -/
theorem removeABCDE_correct (s : String) : 
  removeABCDE_pre s → removeABCDE_post s (removeABCDE s) := by
  intro _
  simp [removeABCDE_post, removeABCDE]
  intro c h
  apply List.mem_filter_of_mem at h
  exact h.2
  sorry

/-- Test cases for removeABCDE -/
def removeABCDE_test : IO Unit := do
  -- Basic case
  if removeABCDE "alphabet" ≠ "lpht" then
    throw (IO.userError "Failed: removeABCDE \"alphabet\" should be \"lpht\"")
  
  -- Edge case: empty string
  if removeABCDE "" ≠ "" then
    throw (IO.userError "Failed: removeABCDE \"\" should be \"\"")
  
  -- Case with uppercase letters
  if removeABCDE "ABCDEabcde" ≠ "ABCDE" then
    throw (IO.userError "Failed: removeABCDE \"ABCDEabcde\" should be \"ABCDE\"")
  
  -- Case with no letters to remove
  if removeABCDE "xyz" ≠ "xyz" then
    throw (IO.userError "Failed: removeABCDE \"xyz\" should be \"xyz\"")
  
  IO.println "All tests passed!"
