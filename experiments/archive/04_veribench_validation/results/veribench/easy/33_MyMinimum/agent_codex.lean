import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

/--
Return the smallest element in a non-empty list of non-negative integers.

Edge cases:
- Single-element list returns that element.
- Empty list is invalid.
-/

def myMinList (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | x :: xs => xs.foldl min x

/-- Test the function with various inputs. -/
def myMinListTest : IO Unit := do
  IO.println s!"Test 1: {myMinList [7, 3, 9, 2]}"  -- Should be 2
  IO.println s!"Test 2: {myMinList [5]}"           -- Should be 5
  -- The following would panic:
  -- IO.println s!"Test 3: {myMinList []}"

/-- Precondition: the list must be non-empty. -/
def myMinListPre (xs : List Nat) : Prop :=
  xs ≠ []

/-- Postcondition: the result is less than or equal to all elements in the list. -/
def myMinListPost (xs : List Nat) (result : Nat) : Prop :=
  ∀ x ∈ xs, result ≤ x

/-- The implementation satisfies the specification. -/
theorem myMinListCorrect (xs : List Nat) :
  myMinListPre xs → myMinListPost xs (myMinList xs) := by
  intro h
  unfold myMinListPost
  intro x hx
  cases xs with
  | nil => contradiction
  | cons y ys =>
    unfold myMinList
    induction ys with
    | nil =>
      simp at hx
      cases hx with
      | inl hx => rw [hx]; simp
      | inr hx => contradiction
    | cons z zs ih =>
      sorry  -- Proof omitted

#eval myMinListTest
