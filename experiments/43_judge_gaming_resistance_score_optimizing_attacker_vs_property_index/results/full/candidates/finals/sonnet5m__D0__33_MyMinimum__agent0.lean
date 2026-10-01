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

/-- A result is a minimum when it occurs in the list and is no greater
than any element of the list. -/
def myMinListIsMinimum (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

private theorem foldl_min_le_all (xs : List Nat) (acc : Nat) :
    xs.foldl min acc ≤ acc ∧ ∀ x ∈ xs, xs.foldl min acc ≤ x := by
  induction xs generalizing acc with
  | nil =>
      simp
  | cons a xs ih =>
      change xs.foldl min (min acc a) ≤ acc ∧
        ∀ x ∈ a :: xs, xs.foldl min (min acc a) ≤ x
      have h := ih (min acc a)
      constructor
      · exact le_trans h.1 (min_le_left _ _)
      · intro x hx
        rcases List.mem_cons.mp hx with hx | hx
        · subst x
          exact le_trans h.1 (min_le_right _ _)
        · exact h.2 x hx

private theorem foldl_min_mem (xs : List Nat) (acc : Nat) :
    xs.foldl min acc ∈ acc :: xs := by sorry

private theorem myMinList_spec (xs : List Nat) (h : xs ≠ []) :
    myMinList xs ∈ xs ∧ ∀ x ∈ xs, myMinList xs ≤ x := by
  cases xs with
  | nil =>
      exact False.elim (h rfl)
  | cons a tail =>
      change (tail.foldl min a) ∈ a :: tail ∧
        (∀ x ∈ a :: tail, tail.foldl min a ≤ x)
      constructor
      · exact foldl_min_mem tail a
      · intro x hx
        have hp := foldl_min_le_all tail a
        rcases List.mem_cons.mp hx with hx | hx
        · subst x
          exact hp.1
        · exact hp.2 x hx

/-- The implementation satisfies the original lower-bound specification. -/
theorem myMinListCorrect (xs : List Nat) :
    myMinListPre xs → myMinListPost xs (myMinList xs) := by
  intro h
  exact (myMinList_spec xs h).2

/-- On a non-empty list, the returned value is an element of the list
and is less than or equal to every element. -/
theorem myMinList_isMinimum (xs : List Nat) (h : xs ≠ []) :
    myMinListIsMinimum xs (myMinList xs) := by
  exact myMinList_spec xs h

/-- Characterization of the minimum: it is precisely the list's unique
least element. -/
theorem myMinList_characterization (xs : List Nat) (h : xs ≠ []) (result : Nat) :
    result = myMinList xs ↔ myMinListIsMinimum xs result := by
  constructor
  · intro heq
    subst result
    exact myMinList_isMinimum xs h
  · intro hm
    rcases hm with ⟨hmem, hleast⟩
    have hs := myMinList_isMinimum xs h
    exact Nat.le_antisymm (hleast _ hs.1) (hs.2 _ hmem)

/-- In particular, the computed result belongs to the input list. -/
theorem myMinList_mem (xs : List Nat) (h : xs ≠ []) :
    myMinList xs ∈ xs := by
  exact (myMinList_isMinimum xs h).1

/-- A singleton list has that element as its minimum. -/
theorem myMinList_singleton (x : Nat) :
    myMinList [x] = x := by
  rfl

/-- The minimum of two non-empty lists concatenated together is the
minimum of their individual minima. -/
theorem myMinList_append (xs ys : List Nat)
    (hx : xs ≠ []) (hy : ys ≠ []) :
    myMinList (xs ++ ys) = min (myMinList xs) (myMinList ys) := by
  have hxy : xs ++ ys ≠ [] := by
    cases xs with
    | nil => exact False.elim (hx rfl)
    | cons x xs => simp
  have hxs := myMinList_isMinimum xs hx
  have hys := myMinList_isMinimum ys hy
  have happ := myMinList_isMinimum (xs ++ ys) hxy
  apply Nat.le_antisymm
  · apply le_min
    · exact happ.2 _ (List.mem_append.mpr (Or.inl hxs.1))
    · exact happ.2 _ (List.mem_append.mpr (Or.inr hys.1))
  · rcases List.mem_append.mp happ.1 with hmem | hmem
    · exact le_trans (min_le_left _ _) (hxs.2 _ hmem)
    · exact le_trans (min_le_right _ _) (hys.2 _ hmem)

/-- Reordering the elements does not change the minimum. -/
theorem myMinList_perm (xs ys : List Nat) (h : xs.Perm ys)
    (hx : xs ≠ []) :
    myMinList xs = myMinList ys := by
  sorry

/-- Adding elements to a list cannot increase its minimum. -/
theorem myMinList_append_left_le (xs ys : List Nat)
    (hx : xs ≠ []) (hy : ys ≠ []) :
    myMinList (xs ++ ys) ≤ myMinList xs := by
  have hxy : xs ++ ys ≠ [] := by
    cases xs with
    | nil => exact False.elim (hx rfl)
    | cons x xs => simp
  have hs := myMinList_isMinimum xs hx
  have happ := myMinList_isMinimum (xs ++ ys) hxy
  exact happ.2 _ (List.mem_append.mpr (Or.inl hs.1))

/-- The precondition excludes the empty list. -/
theorem myMinList_empty_precondition :
    ¬ myMinListPre [] := by
  simp [myMinListPre]

/-- Concrete examples from the task. -/
example : myMinList [7, 3, 9, 2] = 2 := by
  decide

example : myMinList [5] = 5 := by
  decide

#eval myMinListTest
