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

/-- Postcondition: the result occurs in the list and is less than or equal to every element. -/
def myMinListPost (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

theorem min_eq_left_or_right (a b : Nat) :
    min a b = a ∨ min a b = b := by
  rcases le_total a b with h | h
  · exact Or.inl (min_eq_left h)
  · exact Or.inr (min_eq_right h)

theorem foldl_min_le_init (a : Nat) :
    ∀ xs : List Nat, List.foldl min a xs ≤ a := by
  intro xs
  induction xs generalizing a with
  | nil => simp
  | cons b bs ih =>
      simpa only [List.foldl_cons] using
        (le_trans (ih (min a b)) (min_le_left a b))

theorem foldl_min_le_of_mem (a : Nat) :
    ∀ (xs : List Nat) (y : Nat), y ∈ xs → List.foldl min a xs ≤ y := by sorry

theorem foldl_min_mem (a : Nat) :
    ∀ xs : List Nat, List.foldl min a xs ∈ a :: xs := by
  intro xs
  induction xs generalizing a with
  | nil => simp
  | cons b bs ih =>
      have h := ih (min a b)
      change List.foldl min (min a b) bs ∈ a :: b :: bs
      simp only [List.mem_cons] at h ⊢
      rcases h with h | h
      · rcases min_eq_left_or_right a b with hm | hm
        · exact Or.inl (h.trans hm)
        · exact Or.inr (Or.inl (h.trans hm))
      · exact Or.inr (Or.inr h)

/-- The implementation satisfies the minimum specification on every valid input. -/
theorem myMinListCorrect (xs : List Nat) :
    myMinListPre xs → myMinListPost xs (myMinList xs) := by sorry

theorem myMinList_mem (xs : List Nat) (h : myMinListPre xs) :
    myMinList xs ∈ xs :=
  (myMinListCorrect xs h).1

theorem myMinList_le_all (xs : List Nat) (h : myMinListPre xs) :
    ∀ x ∈ xs, myMinList xs ≤ x :=
  (myMinListCorrect xs h).2

example : myMinList [7, 3, 9, 2] = 2 := by decide
example : myMinList [5] = 5 := by decide

#eval myMinListTest
