import Batteries.Data.List
import Batteries.Lean.Util

namespace VB.MaxList

/-!
# Find the maximum value in a list of natural numbers
-/

/-
Return the largest element in a non-empty list of natural numbers.

Edge cases:
- Single element list returns that element.
- The function raises ValueError if the list is empty or contains non-natural numbers.
-/

def pre (xs : List Nat) : Prop :=
  xs ≠ []

def post (xs : List Nat) (res : Nat) : Prop :=
  res ∈ xs ∧ ∀ x ∈ xs, x ≤ res

def prog (xs : List Nat) : Option Nat :=
  match xs with
  | [] => none
  | (x::xs) => some (xs.foldl (fun acc y => max acc y) x)

theorem prog_correct (xs : List Nat) :
  pre xs → Option.isSome (prog xs) ∧ ∀ res, prog xs = some res → post xs res := by
  sorry

/-- Test cases for the implementation -/
def tests : IO Unit := do
  -- Basic unit test
  IO.println s!"Basic test: {prog [7, 3, 9, 2]}"
  assert! prog [7, 3, 9, 2] == some 9

  -- Edge unit test
  IO.println s!"Single element test: {prog [5]}"
  assert! prog [5] == some 5

  -- Negative test
  IO.println s!"Empty list test: {prog []}"
  assert! prog [] == none

#eval tests

end VB.MaxList
