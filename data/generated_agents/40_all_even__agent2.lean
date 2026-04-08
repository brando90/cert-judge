import Lean
import Mathlib.Tactic

/-- Check if all elements in the list are even integers.

Edge cases:
- Empty list returns True.
- Non-integer elements are invalid and raise ValueError.
-/

def allEven (xs : List Int) : Bool :=
  xs.all (fun x => x % 2 == 0)

/-- Tests for the `allEven` function -/
def allEvenTests : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {allEven [2, 4, 6] = true}"
  assert! (allEven [2, 4, 6] = true)
  
  -- Edge case: empty list
  IO.println s!"Test 2: {allEven [] = true}"
  assert! (allEven [] = true)
  
  -- Mixed case
  IO.println s!"Test 3: {allEven [2, 3, 4] = false}"
  assert! (allEven [2, 3, 4] = false)
  
  -- All odd
  IO.println s!"Test 4: {allEven [1, 3, 5] = false}"
  assert! (allEven [1, 3, 5] = false)
  
  IO.println "All tests passed!"

/-- Specification for the `allEven` function -/

/-- Precondition: The input is a list of integers (always satisfied in Lean) -/
def allEvenPre (_xs : List Int) : Prop := True

/-- Postcondition: The result is true if and only if all elements are even -/
def allEvenPost (xs : List Int) (result : Bool) : Prop :=
  result = xs.all (fun x => x % 2 == 0)

/-- Theorem: `allEven` satisfies its specification -/
theorem allEven_correct (xs : List Int) : 
  allEvenPre xs → allEvenPost xs (allEven xs) := by
  intro _
  unfold allEvenPost
  unfold allEven
  rfl
  
#eval allEvenTests
