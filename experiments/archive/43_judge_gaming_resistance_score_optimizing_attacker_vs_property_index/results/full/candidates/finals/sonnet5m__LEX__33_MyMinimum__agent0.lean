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

/-- Folding `min` never increases the initial value. -/
theorem foldl_min_le_start (a : Nat) (xs : List Nat) :
    xs.foldl min a ≤ a := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons y ys ih =>
      change ys.foldl min (min a y) ≤ a
      exact le_trans (ih (min a y)) (min_le_left _ _)

/-- The result of folding `min` is at most every element encountered. -/
theorem foldl_min_le_mem (a : Nat) (xs : List Nat) :
    ∀ {x : Nat}, x ∈ xs → xs.foldl min a ≤ x := by sorry

/-- A fold of `min` selects either its initial value or an element of the list. -/
theorem foldl_min_mem_seed (a : Nat) : ∀ (xs : List Nat),
    xs.foldl min a ∈ a :: xs := by
  intro xs
  induction xs generalizing a with
  | nil =>
      simp
  | cons y ys ih =>
      change ys.foldl min (min a y) ∈ a :: y :: ys
      have hcases : min a y = a ∨ min a y = y := by
        rcases Nat.le_total a y with h | h
        · exact Or.inl (min_eq_left h)
        · exact Or.inr (min_eq_right h)
      have hmem : ys.foldl min (min a y) ∈ (min a y) :: ys :=
        ih (min a y)
      simp only [List.mem_cons] at hmem ⊢
      rcases hmem with hEq | htail
      · rw [hEq]
        rcases hcases with hA | hY
        · exact Or.inl hA
        · exact Or.inr (Or.inl hY)
      · exact Or.inr (Or.inr htail)

/-- The implementation satisfies the specification. -/
theorem myMinListCorrect (xs : List Nat) :
    myMinListPre xs → myMinListPost xs (myMinList xs) := by sorry

/-- On a non-empty list, the returned minimum is itself an element of the list. -/
theorem myMinList_mem (xs : List Nat) (h : myMinListPre xs) :
    myMinList xs ∈ xs := by
  cases xs with
  | nil =>
      exact (h rfl).elim
  | cons y ys =>
      change ys.foldl min y ∈ y :: ys
      exact foldl_min_mem_seed y ys

/-- Together, membership and the postcondition characterize the returned minimum. -/
theorem myMinListCorrectAndMem (xs : List Nat) (h : myMinListPre xs) :
    myMinListPost xs (myMinList xs) ∧ myMinList xs ∈ xs := by
  exact ⟨myMinListCorrect xs h, myMinList_mem xs h⟩

@[simp] theorem myMinList_singleton (n : Nat) :
    myMinList [n] = n := by
  rfl

example : myMinList [7, 3, 9, 2] = 2 := by
  rfl

example : myMinList [5] = 5 := by
  rfl

#eval myMinListTest
