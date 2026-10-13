import Mathlib

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

theorem my_min_list_correct (xs : List Nat) (h : my_min_list_pre xs) :
  my_min_list_post xs (my_min_list xs) := by
  induction xs with
  | nil =>
      simp [my_min_list_pre] at h
  | cons x xs ih =>
      cases xs with
      | nil =>
          simp [my_min_list, my_min_list_post]
      | cons y ys =>
          have htail : my_min_list_pre (y :: ys) := by
            simp [my_min_list_pre]
          have hi := ih htail
          have hi_mem : my_min_list (y :: ys) ∈ y :: ys := by
            simpa [my_min_list_post] using hi.1
          have hi_le : ∀ z ∈ y :: ys, my_min_list (y :: ys) ≤ z := by
            simpa [my_min_list_post] using hi.2
          change
            (if x < my_min_list (y :: ys) then x else my_min_list (y :: ys)) ∈
                x :: y :: ys ∧
              ∀ z ∈ x :: y :: ys,
                (if x < my_min_list (y :: ys) then x else my_min_list (y :: ys)) ≤ z
          by_cases hx : x < my_min_list (y :: ys)
          · rw [if_pos hx]
            constructor
            · simp
            · intro z hz
              rcases List.mem_cons.mp hz with hzx | hzt
              · subst z
                exact Nat.le_refl _
              · exact le_trans (Nat.le_of_lt hx) (hi_le z hzt)
          · rw [if_neg hx]
            have hmx : my_min_list (y :: ys) ≤ x := by
              omega
            constructor
            · exact List.mem_cons.mpr (Or.inr hi_mem)
            · intro z hz
              rcases List.mem_cons.mp hz with hzx | hzt
              · subst z
                exact hmx
              · exact hi_le z hzt

theorem my_min_list_mem (xs : List Nat) (h : my_min_list_pre xs) :
    my_min_list xs ∈ xs :=
  (my_min_list_correct xs h).1

theorem my_min_list_le_all (xs : List Nat) (h : my_min_list_pre xs) :
    ∀ x ∈ xs, my_min_list xs ≤ x :=
  (my_min_list_correct xs h).2

theorem my_min_list_unique (xs : List Nat) (h : my_min_list_pre xs)
    (r : Nat) (hr : r ∈ xs ∧ ∀ x ∈ xs, r ≤ x) :
    r = my_min_list xs := by
  rcases hr with ⟨hrmem, hrle⟩
  apply Nat.le_antisymm
  · exact hrle (my_min_list xs) (my_min_list_mem xs h)
  · exact my_min_list_le_all xs h r hrmem

/-- The precondition and postcondition hold for a singleton list. -/
theorem my_min_list_singleton (x : Nat) :
    my_min_list [x] = x := by
  rfl

theorem my_min_list_example :
    my_min_list [7, 3, 9, 2] = 2 := by
  rfl

/--
Test cases for `my_min_list`
-/
def test_my_min_list : IO Unit := do
  -- Basic test
  IO.println s!"Test 1: {my_min_list [7, 3, 9, 2]}"
  assert! my_min_list [7, 3, 9, 2] = 2

  -- Edge case: single element
  IO.println s!"Test 2: {my_min_list [5]}"
  assert! my_min_list [5] = 5

  -- The empty list case would cause a runtime error, not tested here
  
  IO.println "All tests passed!"

#eval test_my_min_list
