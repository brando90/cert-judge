/-
  Return the smallest element in a non-empty list of non-negative integers.

  Edge cases:
  - Single-element list returns that element.
  - Empty list or non-integers are invalid and raise ValueError.
-/

def my_min_list (xs : List Nat) : Nat :=
  match xs with
  | [] => panic! "Require non-empty list of non-negative integers"
  | [x] => x
  | x :: xs =>
    let min_rest := my_min_list xs
    if x < min_rest then x else min_rest

/-- The precondition for `my_min_list`: The list must be non-empty. -/
def my_min_list_pre (xs : List Nat) : Prop :=
  xs.length > 0

/-- The postcondition for `my_min_list`: The result is the minimum element in the list. -/
def my_min_list_post (xs : List Nat) (result : Nat) : Prop :=
  result ∈ xs ∧ ∀ x ∈ xs, result ≤ x

/-- On every nonempty list, the computed element belongs to the list
and is less than or equal to every element in it. -/
theorem my_min_list_spec :
    ∀ xs : List Nat, xs ≠ [] → my_min_list_post xs (my_min_list xs) := by sorry

theorem my_min_list_correct (xs : List Nat) (h : my_min_list_pre xs) :
    my_min_list_post xs (my_min_list xs) := by
  apply my_min_list_spec
  intro he
  subst xs
  simp [my_min_list_pre] at h

theorem my_min_list_result_mem (xs : List Nat) (h : my_min_list_pre xs) :
    my_min_list xs ∈ xs := by
  have hpost := my_min_list_correct xs h
  exact hpost.1

theorem my_min_list_le_of_mem (xs : List Nat) (h : my_min_list_pre xs)
    (x : Nat) (hx : x ∈ xs) :
    my_min_list xs ≤ x := by
  have hpost := my_min_list_correct xs h
  exact hpost.2 x hx

/-- Any lower bound for every member of the list is a lower bound for its minimum. -/
theorem my_min_list_lower_bound (xs : List Nat) (h : my_min_list_pre xs)
    (k : Nat) (hk : ∀ x ∈ xs, k ≤ x) :
    k ≤ my_min_list xs := by
  have hmem := my_min_list_result_mem xs h
  exact hk (my_min_list xs) hmem

/-- The minimum of a list containing zero is zero. -/
theorem my_min_list_eq_zero_of_mem (xs : List Nat) (h : my_min_list_pre xs)
    (hz : 0 ∈ xs) :
    my_min_list xs = 0 := by
  have hle := my_min_list_le_of_mem xs h 0 hz
  exact Nat.eq_zero_of_le_zero hle

/-- The result depends only on which values occur in a nonempty list. -/
theorem my_min_list_extensional (xs ys : List Nat) (hne : xs ≠ [])
    (hmem : ∀ x, x ∈ xs ↔ x ∈ ys) :
    my_min_list xs = my_min_list ys := by
  have hx := my_min_list_spec xs hne
  have hyne : ys ≠ [] := by
    intro hy
    subst ys
    have hnil : my_min_list xs ∈ ([] : List Nat) :=
      (hmem (my_min_list xs)).mp hx.1
    simp at hnil
  have hy := my_min_list_spec ys hyne
  apply Nat.le_antisymm
  · exact hx.2 (my_min_list ys) ((hmem (my_min_list ys)).mpr hy.1)
  · exact hy.2 (my_min_list xs) ((hmem (my_min_list xs)).mp hx.1)

theorem my_min_list_example_basic :
    my_min_list [7, 3, 9, 2] = 2 := by
  decide

theorem my_min_list_example_singleton :
    my_min_list [5] = 5 := by
  decide

theorem my_min_list_example_duplicates :
    my_min_list [4, 1, 1, 8] = 1 := by
  decide

theorem my_min_list_example_increasing :
    my_min_list [1, 2, 3, 4] = 1 := by
  decide

theorem my_min_list_example_zero :
    my_min_list [4, 0, 2] = 0 := by
  decide

theorem my_min_list_empty_not_pre :
    ¬ my_min_list_pre [] := by
  simp [my_min_list_pre]

/-- A lower bound for all list members is exactly a lower bound for the result. -/
theorem my_min_list_lower_bound_iff (xs : List Nat) (h : my_min_list_pre xs)
    (k : Nat) :
    (∀ x ∈ xs, k ≤ x) ↔ k ≤ my_min_list xs := by
  sorry

/-- A value is above the minimum precisely when some list member is below it. -/
theorem my_min_list_le_iff_exists (xs : List Nat) (h : my_min_list_pre xs)
    (k : Nat) :
    my_min_list xs ≤ k ↔ ∃ x ∈ xs, x ≤ k := by
  sorry

/-- The minimum of a cons list is no larger than its head. -/
theorem my_min_list_cons_le_head (x : Nat) (xs : List Nat) :
    my_min_list (x :: xs) ≤ x := by
  sorry

/-- When the tail is nonempty, a cons list minimum is the minimum
of its head and the tail minimum. -/
theorem my_min_list_cons (x : Nat) (xs : List Nat) (hne : xs ≠ []) :
    my_min_list (x :: xs) = min x (my_min_list xs) := by
  sorry

/-- Appending a singleton adds one candidate to the minimum. -/
theorem my_min_list_append_singleton (xs : List Nat) (h : my_min_list_pre xs)
    (x : Nat) :
    my_min_list (xs ++ [x]) = min (my_min_list xs) x := by
  sorry

/-- For two nonempty lists, the minimum of their concatenation
is the smaller of their two minima. -/
theorem my_min_list_append (xs ys : List Nat)
    (hx : my_min_list_pre xs) (hy : my_min_list_pre ys) :
    my_min_list (xs ++ ys) = min (my_min_list xs) (my_min_list ys) := by
  sorry

/-- Reordering a nonempty list does not change its minimum. -/
theorem my_min_list_perm (xs ys : List Nat) (hne : xs ≠ [])
    (hperm : List.Perm xs ys) :
    my_min_list xs = my_min_list ys := by
  sorry

/-- Adding more elements cannot increase a list's minimum. -/
theorem my_min_list_antitone_of_subset (xs ys : List Nat)
    (hx : my_min_list_pre xs) (hy : my_min_list_pre ys)
    (hsub : ∀ x, x ∈ xs → x ∈ ys) :
    my_min_list ys ≤ my_min_list xs := by
  sorry

/-- Translating every element by the same natural number translates
the minimum by that number. -/
theorem my_min_list_map_add (xs : List Nat) (h : my_min_list_pre xs)
    (k : Nat) :
    my_min_list (xs.map (fun x => x + k)) = my_min_list xs + k := by
  sorry

theorem my_min_list_example_two_elements :
    my_min_list [8, 3] = 3 := by
  decide

theorem my_min_list_example_descending :
    my_min_list [9, 7, 4, 1] = 1 := by
  decide

theorem my_min_list_example_repeated_minimum :
    my_min_list [2, 5, 2, 8, 2] = 2 := by
  decide
