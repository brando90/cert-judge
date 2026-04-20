import Mathlib

namespace MyMinList


def myMinList : List Nat → Nat
  | [] => 0        -- Default case for empty list, though function is intended for non-empty lists
  | [x] => x
  | x :: xs => min x (myMinList xs)


def myMinListImperative (xs : List Nat) : Nat :=
  match xs with
  | [] => 0
  | x :: xs => Id.run do
    let mut m := x
    for y in xs do
      if y < m then
        m := y
    return m

/-!
# Property Theorems
-/


def empty_list_prop : Prop := myMinList [] = 0


def single_element_prop (x : Nat) : Prop := myMinList [x] = x


def minimum_prop (xs : List Nat) : Prop :=
  xs ≠ [] → (myMinList xs ∈ xs ∧ ∀ z ∈ xs, myMinList xs ≤ z)


def membership_prop (xs : List Nat) : Prop :=
  xs ≠ [] → myMinList xs ∈ xs


def two_elements_prop (x y : Nat) : Prop := myMinList [x, y] = min x y


# Pre‑Condition
-/


def Pre (xs : List Nat) : Prop := True

/-!
# Post‑Condition  (conjunction of all desired properties)
-/


def Post_prop (xs : List Nat) : Prop :=
  (empty_list_prop) ∧                                    -- empty_list_prop
  (∀ x, single_element_prop x) ∧                         -- single_element_prop
  (minimum_prop xs) ∧                                    -- minimum_prop
  (membership_prop xs) ∧                                 -- membership_prop
  (∀ x y, two_elements_prop x y)                         -- two_elements_prop

/-!
# Correctness Theorem
-/



/-!
# Tests
-/

/-- expected: 2 -/
example : myMinList [7, 3, 9, 2] = 2 := by native_decide
#eval! myMinList [7, 3, 9, 2] -- expected: 2

/-- expected: 5 -/
example : myMinList [5] = 5 := by native_decide
#eval! myMinList [5] -- expected: 5

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : myMinList [] = 0 := by
  unfold myMinList
  rfl
#eval! myMinList [] -- expected: 0

/-- expected: 1 -/
example : myMinList [3, 1, 4] = 1 := by native_decide
#eval! myMinList [3, 1, 4] -- expected: 1

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: two elements -/
example : myMinList [10, 5] = 5 := by native_decide
#eval! myMinList [10, 5] -- expected: 5

/-- positive: duplicate elements -/
example : myMinList [3, 3, 3] = 3 := by native_decide
#eval! myMinList [3, 3, 3] -- expected: 3

/-- negative: empty list returns default -/
example : myMinList [] ≠ 42 := by native_decide

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: multiple elements -/
example : myMinListImperative [10, 3, 7, 1] = 1 := by native_decide
#eval! myMinListImperative [10, 3, 7, 1] -- expected: 1

/-- negative: empty list returns default -/
example : myMinListImperative [] ≠ 100 := by native_decide

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
-- Aux lemma: the loop computes min of m and the myMinList of a non-empty list
private theorem myMinListImp_aux (y : Nat) (ys : List Nat) (m : Nat) :
    Id.run (do
      let mut m : Nat := m
      for z in y :: ys do
        if z < m then
          m := z
      return m) = min m (myMinList (y :: ys)) := by
  induction ys generalizing m y with
  | nil =>
    simp only [myMinList]
    by_cases h : y < m
    · simp [h, min_eq_right (Nat.le_of_lt h)]
    · push_neg at h; simp [show ¬(y < m) from not_lt.mpr h, min_eq_left h]
  | cons z zs ih =>
    by_cases h : y < m
    · calc
        Id.run (do
          let mut m := m
          for z_1 in y :: z :: zs do
            if z_1 < m then m := z_1
          return m) =
            Id.run (do
              let mut m := y
              for z_1 in z :: zs do
                if z_1 < m then m := z_1
              return m) := by simp [h]
        _ = min y (myMinList (z :: zs)) := ih z y
        _ = min m (myMinList (y :: z :: zs)) := by
              simp [myMinList]; omega
    · push_neg at h
      calc
        Id.run (do
          let mut m := m
          for z_1 in y :: z :: zs do
            if z_1 < m then m := z_1
          return m) =
            Id.run (do
              let mut m := m
              for z_1 in z :: zs do
                if z_1 < m then m := z_1
              return m) := by simp [show ¬(y < m) from not_lt.mpr h]
        _ = min m (myMinList (z :: zs)) := ih z m
        _ = min m (myMinList (y :: z :: zs)) := by
              simp [myMinList]; omega

theorem myMinList_equivalence_thm (xs : List Nat) :
  myMinList xs = myMinListImperative xs := by
  cases xs with
  | nil => simp [myMinList, myMinListImperative]
  | cons x xs =>
    cases xs with
    | nil => simp [myMinList, myMinListImperative]
    | cons y ys =>
      unfold myMinListImperative
      simpa [myMinList] using (myMinListImp_aux y ys x).symm




end MyMinList