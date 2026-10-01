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

/-- A minimum is an element of the list and is less than or equal to every element. -/
def myMinListPost (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

private theorem foldl_min_le_start (a : Nat) (xs : List Nat) :
    List.foldl min a xs ≤ a := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons b bs ih =>
      simp only [List.foldl_cons]
      exact le_trans (ih (min a b)) (min_le_left _ _)

private theorem foldl_min_le_each (a : Nat) (xs : List Nat) (y : Nat)
    (hy : y ∈ xs) : List.foldl min a xs ≤ y := by
  induction xs generalizing a with
  | nil =>
      simp at hy
  | cons b bs ih =>
      simp only [List.foldl_cons]
      simp only [List.mem_cons] at hy
      rcases hy with hy | hy
      · subst y
        exact le_trans (foldl_min_le_start (min a b) bs) (min_le_right _ _)
      · exact ih (min a b) hy

private theorem foldl_min_mem (a : Nat) (xs : List Nat) :
    List.foldl min a xs ∈ a :: xs := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons b bs ih =>
      simp only [List.foldl_cons]
      have htail := ih (min a b)
      simp only [List.mem_cons] at htail ⊢
      rcases htail with hEq | hMem
      · rw [hEq]
        rcases le_total a b with hab | hba
        · exact Or.inl (min_eq_left hab)
        · exact Or.inr (Or.inl (min_eq_right hba))
      · exact Or.inr (Or.inr hMem)

/-- The implementation satisfies the minimum specification. -/
theorem myMinListCorrect (xs : List Nat) :
    myMinListPre xs → myMinListPost xs (myMinList xs) := by
  intro h
  cases xs with
  | nil =>
      exact False.elim (h rfl)
  | cons a as =>
      constructor
      · change List.foldl min a as ∈ a :: as
        exact foldl_min_mem a as
      · intro x hx
        change List.foldl min a as ≤ x
        simp only [List.mem_cons] at hx
        rcases hx with hx | hx
        · subst x
          exact foldl_min_le_start a as
        · exact foldl_min_le_each a as x hx

/-- For every valid input, the returned value occurs in the input. -/
theorem myMinList_mem (xs : List Nat) (h : myMinListPre xs) :
    myMinList xs ∈ xs :=
  (myMinListCorrect xs h).1

/-- For every valid input, the returned value is no greater than any input element. -/
theorem myMinList_le_of_mem (xs : List Nat) (h : myMinListPre xs)
    (x : Nat) (hx : x ∈ xs) : myMinList xs ≤ x :=
  (myMinListCorrect xs h).2 x hx

/-- The specification uniquely determines the result. -/
theorem myMinList_unique (xs : List Nat) (h : myMinListPre xs)
    (r : Nat) (hr : myMinListPost xs r) : r = myMinList xs := by sorry

/-- On a singleton list, the sole element is returned. -/
@[simp] theorem myMinList_singleton (a : Nat) :
    myMinList [a] = a := by
  simp [myMinList]

/-- The recursive case computes the fold of `min` starting from the head. -/
@[simp] theorem myMinList_cons (a : Nat) (xs : List Nat) :
    myMinList (a :: xs) = List.foldl min a xs := rfl

theorem myMinList_example :
    myMinList [7, 3, 9, 2] = 2 ∧ myMinList [5] = 5 := by
  decide

#eval myMinListTest
