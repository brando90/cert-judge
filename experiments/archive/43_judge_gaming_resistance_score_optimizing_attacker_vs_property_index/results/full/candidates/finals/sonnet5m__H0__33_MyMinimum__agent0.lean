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

/-- A fold of `min` never exceeds its initial accumulator or any list element. -/
theorem foldl_min_le (a : Nat) (xs : List Nat) :
    List.foldl min a xs ≤ a ∧
      ∀ x ∈ xs, List.foldl min a xs ≤ x := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons b xs ih =>
      simp only [List.foldl_cons]
      have hi := ih (min a b)
      constructor
      · exact le_trans hi.1 (min_le_left a b)
      · intro x hx
        rcases List.mem_cons.mp hx with hhead | htail
        · cases hhead
          exact le_trans hi.1 (min_le_right a b)
        · exact hi.2 x htail

/-- Folding `min` from an accumulator returns either that accumulator
or an element of the folded list. -/
theorem foldl_min_mem (a : Nat) (xs : List Nat) :
    List.foldl min a xs = a ∨
      ∃ x, x ∈ xs ∧ List.foldl min a xs = x := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons b xs ih =>
      simp only [List.foldl_cons]
      have h := ih (min a b)
      rcases h with h | ⟨x, hx, hEq⟩
      · rcases le_total a b with hab | hba
        · left
          simpa [min_eq_left hab] using h
        · right
          refine ⟨b, by simp, ?_⟩
          simpa [min_eq_right hba] using h
      · right
        exact ⟨x, by simp [hx], hEq⟩

/-- The implementation satisfies the lower-bound part of the specification. -/
theorem myMinListCorrect (xs : List Nat) :
  myMinListPre xs → myMinListPost xs (myMinList xs) := by
  cases xs with
  | nil =>
      intro h
      exact False.elim (h rfl)
  | cons a tl =>
      intro _h
      intro x hx
      have hm := foldl_min_le a tl
      change List.foldl min a tl ≤ x
      rcases List.mem_cons.mp hx with hhead | htail
      · subst x
        exact hm.1
      · exact hm.2 x htail

/-- On a non-empty list, the returned minimum is one of its elements. -/
theorem myMinList_mem (xs : List Nat) (h : myMinListPre xs) :
    myMinList xs ∈ xs := by
  cases xs with
  | nil =>
      exact False.elim (h rfl)
  | cons a tl =>
      have hm := foldl_min_mem a tl
      simp only [myMinList]
      rcases hm with hEq | ⟨x, hx, hEq⟩
      · rw [hEq]
        simp
      · rw [hEq]
        simp [hx]

/-- Exact postcondition: the result is an element of the list and is
less than or equal to every element. -/
def myMinListExactPost (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ myMinListPost xs result

theorem myMinListExact (xs : List Nat) (h : myMinListPre xs) :
    myMinListExactPost xs (myMinList xs) := by
  constructor
  · exact myMinList_mem xs h
  · exact myMinListCorrect xs h

/-- The computed value is the unique list value that is less than or
equal to every element. -/
theorem myMinList_iff_minimum (xs : List Nat) (h : myMinListPre xs)
    (n : Nat) :
    n = myMinList xs ↔ n ∈ xs ∧ ∀ x ∈ xs, n ≤ x := by
  constructor
  · intro hn
    subst n
    exact myMinListExact xs h
  · rintro ⟨hnmem, hnle⟩
    apply le_antisymm
    · exact hnle _ (myMinList_mem xs h)
    · exact myMinListCorrect xs h _ hnmem

theorem myMinList_singleton (n : Nat) :
    myMinList [n] = n := by
  rfl

theorem myMinList_pair (a b : Nat) :
    myMinList [a, b] = min a b := by
  rfl

theorem myMinList_example :
    myMinList [7, 3, 9, 2] = 2 := by
  rfl

theorem myMinList_singleton_example :
    myMinList [5] = 5 := by
  rfl

#eval myMinListTest
