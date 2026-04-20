import Mathlib

namespace MyMaxList


def myMaxList : List Nat → Nat
  | [] => 0        -- Default case for empty list, though function is intended for non-empty lists
  | [x] => x
  | x :: xs => max x (myMaxList xs)


def myMaxListImp (xs : List Nat) : Nat := Id.run do
  let mut m : Nat := 0
  for x in xs do
    if m ≤ x then
      m := x
  return m



/-!
# Unit Tests
-/

/-- expected: 9 -/
example : myMaxList [7, 3, 9, 2] = 9 := by native_decide

#eval myMaxList [7, 3, 9, 2] -- expected: 9

/-- expected: 5 (edge cases)-/
example : myMaxList [5] = 5 := by native_decide

#eval myMaxList [5] -- expected: 5

/-- expected: 0 -/
example : myMaxList [] = 0 := by native_decide

#eval myMaxList [] -- expected: 0

/-!
# Positive / Negative Test-Suite
-/

/-- positive: finds maximum in various positions -/
example : myMaxList [1, 8, 3] = 8 := by native_decide

#eval myMaxList [1, 8, 3] -- expected: 8

/-- positive: handles duplicates correctly -/
example : myMaxList [5, 5, 3] = 5 := by native_decide

#eval myMaxList [5, 5, 3] -- expected: 5

/-- positive: maximum at end -/
example : myMaxList [1, 2, 10] = 10 := by native_decide

#eval myMaxList [1, 2, 10] -- expected: 10

/-- negative: result should not be smaller than any element -/
example : ¬ (myMaxList [3, 7, 4] < 3) := by native_decide

#eval (decide (myMaxList [3, 7, 4] < 3)) -- expected: false

/-- negative: empty list result should not be positive -/
example : ¬ (myMaxList [] > 0) := by native_decide

#eval (decide (myMaxList [] > 0)) -- expected: false

/-!
# Positive / Negative Test-Suite
-/

/-- positive: maintains maximum computation -/
example : myMaxListImp [1, 8, 3] = 8 := by native_decide

#eval myMaxListImp [1, 8, 3] -- expected: 8

/-- negative: result should not be smaller than any element -/
example : ¬ (myMaxListImp [3, 7, 4] < 3) := by native_decide

#eval (decide (myMaxListImp [3, 7, 4] < 3)) -- expected: false

/-- **Equivalence**: functional and imperative maximum list coincide. -/
private theorem myMaxListImp_aux (xs : List Nat) (m : Nat) :
    Id.run (do
      let mut m : Nat := m
      for y in xs do
        if m ≤ y then
          m := y
      return m) = max m (myMaxList xs) := by
  induction xs generalizing m with
  | nil =>
      simp [myMaxList]
  | cons y ys ih =>
      cases ys with
      | nil =>
          by_cases h : m ≤ y
          · simp [h, myMaxList, max_eq_right h]
          · have hy : y ≤ m := Nat.le_of_lt (Nat.lt_of_not_ge h)
            simp [h, myMaxList, max_eq_left hy]
      | cons z zs =>
          by_cases h : m ≤ y
          · calc
              Id.run (do
                let mut m : Nat := m
                for y in y :: z :: zs do
                  if m ≤ y then
                    m := y
                return m) =
                  Id.run (do
                    let mut m : Nat := y
                    for y in z :: zs do
                      if m ≤ y then
                        m := y
                    return m) := by
                      simp [h]
              _ = max y (myMaxList (z :: zs)) := ih y
              _ = max m (myMaxList (y :: z :: zs)) := by
                    simp [myMaxList, h, Nat.max_assoc, Nat.max_left_comm, Nat.max_comm]
          · have hy : y ≤ m := Nat.le_of_lt (Nat.lt_of_not_ge h)
            calc
              Id.run (do
                let mut m : Nat := m
                for y in y :: z :: zs do
                  if m ≤ y then
                    m := y
                return m) =
                  Id.run (do
                    let mut m : Nat := m
                    for y in z :: zs do
                      if m ≤ y then
                        m := y
                    return m) := by
                      simp [h]
              _ = max m (myMaxList (z :: zs)) := ih m
              _ = max m (myMaxList (y :: z :: zs)) := by
                    simp [myMaxList, hy, Nat.max_assoc, Nat.max_left_comm, Nat.max_comm]

theorem myMaxList_equivalence (xs : List Nat) :
  myMaxList xs = myMaxListImp xs := by
  cases xs with
  | nil =>
      simp [myMaxList, myMaxListImp]
  | cons x xs =>
      cases xs with
      | nil =>
          simp [myMaxList, myMaxListImp]
      | cons y ys =>
          unfold myMaxListImp
          simpa [myMaxList] using (myMaxListImp_aux (y :: ys) x).symm




end MyMaxList