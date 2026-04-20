import Mathlib

namespace MyOddSumParity


def parity (n : Nat) : Nat := n % 2


def sumList : List Nat → Nat
  | [] => 0
  | x :: xs => x + sumList xs


def myOddSumParity (xs : List Nat) : Nat :=
  parity (sumList xs)


def myOddSumParityImp (xs : List Nat) : Nat :=
  Id.run do
    let mut sum := 0
    for x in xs do
      sum := sum + x
    return sum % 2



/-!
# Tests
-/

/-- expected: 1 -/
example : myOddSumParity [1, 3, 5] = 1 := by native_decide
#eval myOddSumParity [1, 3, 5] -- expected: 1

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : myOddSumParity [] = 0 := by native_decide
#eval myOddSumParity [] -- expected: 0

/-- expected: 1 -/
example : myOddSumParity [1] = 1 := by native_decide
#eval myOddSumParity [1] -- expected: 1

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: two odd numbers sum to even (parity 0) -/
example : myOddSumParity [1, 3] = 0 := by native_decide
#eval myOddSumParity [1, 3] -- expected: 0

/-- positive: three odd numbers sum to odd (parity 1) -/
example : myOddSumParity [1, 3, 7] = 1 := by native_decide
#eval myOddSumParity [1, 3, 7] -- expected: 1

/-- negative: result should only be 0 or 1 -/
example : ¬ (myOddSumParity [1, 3, 5] > 1) := by native_decide
#eval (decide (myOddSumParity [1, 3, 5] > 1)) -- expected: false

/-- negative: empty list should not have odd parity -/
example : ¬ (myOddSumParity [] = 1) := by native_decide
#eval (decide (myOddSumParity [] = 1)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: two odd numbers sum to even (parity 0) -/
example : myOddSumParityImp [1, 3] = 0 := by native_decide
#eval myOddSumParityImp [1, 3] -- expected: 0

/-- negative: result should only be 0 or 1 -/
example : ¬ (myOddSumParityImp [1, 3, 5] > 1) := by native_decide
#eval (decide (myOddSumParityImp [1, 3, 5] > 1)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem sum_loop_aux (xs : List Nat) (acc : Nat) :
    Id.run (do
      let mut sum := acc
      for x in xs do
        sum := sum + x
      return sum) = acc + sumList xs := by
  induction xs generalizing acc with
  | nil => simp [sumList]
  | cons a tl ih =>
    calc
      Id.run (do
        let mut sum := acc
        for x in a :: tl do
          sum := sum + x
        return sum) =
          Id.run (do
            let mut sum := acc + a
            for x in tl do
              sum := sum + x
            return sum) := by simp
      _ = acc + a + sumList tl := ih (acc + a)
      _ = acc + (a + sumList tl) := by omega
      _ = acc + sumList (a :: tl) := by simp [sumList]

private theorem sum_loop_mod_aux (xs : List Nat) (acc : Nat) :
    Id.run (do
      let mut sum := acc
      for x in xs do
        sum := sum + x
      return sum % 2) = (acc + sumList xs) % 2 := by
  induction xs generalizing acc with
  | nil => simp [sumList]
  | cons a tl ih =>
    calc
      Id.run (do
        let mut sum := acc
        for x in a :: tl do
          sum := sum + x
        return sum % 2) =
          Id.run (do
            let mut sum := acc + a
            for x in tl do
              sum := sum + x
            return sum % 2) := by simp
      _ = (acc + a + sumList tl) % 2 := ih (acc + a)
      _ = (acc + (a + sumList tl)) % 2 := by omega
      _ = (acc + sumList (a :: tl)) % 2 := by simp [sumList]

theorem myOddSumParity_equivalence_thm (xs : List Nat) :
  myOddSumParity xs = myOddSumParityImp xs := by
  unfold myOddSumParity myOddSumParityImp parity
  simpa using (sum_loop_mod_aux xs 0).symm




end MyOddSumParity