import Mathlib

/-!
# My Min List

Return the smallest element in a non-empty list of non-negative integers.
Natural numbers represent the permitted non-negative integer inputs.
-/

namespace MyMinList

def my_min_list (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | x :: xs => xs.foldl min x

/-- The precondition for `my_min_list` is that the input list is non-empty. -/
def pre (xs : List Nat) : Prop :=
  xs ≠ []

/-- The result is a member of the input and is no greater than any of its elements. -/
def post (xs : List Nat) (result : Nat) : Prop :=
  (∀ x ∈ xs, result ≤ x) ∧ (result ∈ xs)

theorem foldl_min_mem (a : Nat) (xs : List Nat) :
    List.foldl min a xs ∈ a :: xs := by
  induction xs generalizing a with
  | nil =>
      simp
  | cons x xs ih =>
      simp only [List.foldl_cons]
      have hmem : List.foldl min (min a x) xs ∈ min a x :: xs :=
        ih (min a x)
      have hmin : min a x = a ∨ min a x = x := by
        by_cases h : a ≤ x
        · left
          exact min_eq_left h
        · right
          exact min_eq_right (by omega)
      simp only [List.mem_cons] at hmem ⊢
      rcases hmem with hhead | htail
      · rw [hhead]
        rcases hmin with hmin | hmin
        · exact Or.inl hmin
        · exact Or.inr (Or.inl hmin)
      · exact Or.inr (Or.inr htail)

theorem foldl_min_le_mem (a : Nat) (xs : List Nat) :
    ∀ y ∈ a :: xs, List.foldl min a xs ≤ y := by
  induction xs generalizing a with
  | nil =>
      intro y hy
      simp at hy
      subst y
      exact le_rfl
  | cons x xs ih =>
      intro y hy
      simp only [List.foldl_cons]
      rcases List.mem_cons.mp hy with hya | hyrest
      · subst y
        have h0 : List.foldl min (min a x) xs ≤ min a x :=
          ih (min a x) (min a x) (by simp)
        exact le_trans h0 (min_le_left a x)
      · rcases List.mem_cons.mp hyrest with hyx | hyxs
        · subst y
          have h0 : List.foldl min (min a x) xs ≤ min a x :=
            ih (min a x) (min a x) (by simp)
          exact le_trans h0 (min_le_right a x)
        · exact ih (min a x) y (by simp [hyxs])

theorem my_min_list_spec (xs : List Nat) (h : pre xs) :
    post xs (my_min_list xs) := by
  cases xs with
  | nil =>
      simp [pre] at h
  | cons x tail =>
      simp only [post, my_min_list]
      constructor
      · intro y hy
        exact foldl_min_le_mem x tail y hy
      · exact foldl_min_mem x tail

theorem my_min_list_le (xs : List Nat) (h : pre xs) :
    ∀ x ∈ xs, my_min_list xs ≤ x :=
  (my_min_list_spec xs h).1

theorem my_min_list_mem (xs : List Nat) (h : pre xs) :
    my_min_list xs ∈ xs :=
  (my_min_list_spec xs h).2

@[simp] theorem my_min_list_singleton (x : Nat) :
    my_min_list [x] = x := by
  simp [my_min_list]

/-- Any two values satisfying the minimum specification must be equal. -/
theorem post_unique (xs : List Nat) (a b : Nat)
    (ha : post xs a) (hb : post xs b) : a = b := by
  apply Nat.le_antisymm
  · exact ha.1 b hb.2
  · exact hb.1 a ha.2

/-- Characterize the minimum by membership and the lower-bound property. -/
theorem my_min_list_characterization (xs : List Nat) (h : pre xs) (n : Nat) :
    n = my_min_list xs ↔ n ∈ xs ∧ ∀ x ∈ xs, n ≤ x := by
  constructor
  · intro heq
    subst n
    exact ⟨my_min_list_mem xs h, my_min_list_le xs h⟩
  · rintro ⟨hnmem, hnle⟩
    apply Nat.le_antisymm
    · exact hnle _ (my_min_list_mem xs h)
    · exact my_min_list_le xs h n hnmem

/-- The minimum of a larger non-empty set of values cannot exceed the
minimum of a non-empty subset. -/
theorem my_min_list_mono_of_subset {xs ys : List Nat}
    (hxs : pre xs) (hys : pre ys)
    (hsub : ∀ x ∈ xs, x ∈ ys) :
    my_min_list ys ≤ my_min_list xs := by
  exact my_min_list_le ys hys _ (hsub _ (my_min_list_mem xs hxs))

@[simp] theorem pre_cons (x : Nat) (xs : List Nat) :
    pre (x :: xs) := by
  simp [pre]

@[simp] theorem not_pre_nil : ¬ pre ([] : List Nat) := by
  simp [pre]

theorem my_min_list_example :
    my_min_list [7, 3, 9, 2] = 2 := by
  norm_num [my_min_list]

theorem my_min_list_singleton_example :
    my_min_list [5] = 5 := by
  norm_num [my_min_list]

theorem my_min_list_duplicates_example :
    my_min_list [4, 2, 2, 3] = 2 := by
  norm_num [my_min_list]

theorem my_min_list_larger_example :
    my_min_list [100, 42, 99, 101] = 42 := by
  norm_num [my_min_list]

/-- Test cases for my_min_list -/
def test : IO Unit := do
  -- Basic
  assert! (my_min_list [7, 3, 9, 2] = 2)
  -- Edge
  assert! (my_min_list [5] = 5)
  -- Should handle duplicates
  assert! (my_min_list [4, 2, 2, 3] = 2)
  -- Should handle larger numbers
  assert! (my_min_list [100, 42, 99, 101] = 42)
  -- Zero is a valid non-negative input
  assert! (my_min_list [8, 0, 5] = 0)
  IO.println "All tests passed!"

end MyMinList
