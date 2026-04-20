import Mathlib

namespace MyEvenSumParity


def parity (n : Nat) : Nat := n % 2


def sumList : List Nat → Nat
  | [] => 0
  | x :: xs => x + sumList xs


def myEvenSumParity (xs : List Nat) : Nat :=
  parity (sumList xs)


def myEvenSumParityImp (xs : List Nat) : Nat :=
  Id.run (do
    let mut sum := 0
    for x in xs do
      sum := sum + x
    return sum % 2)

/-!
# Tests
-/

/-- expected: 0 -/
example : myEvenSumParity [2, 4, 6] = 0 := by native_decide
#eval myEvenSumParity [2, 4, 6] -- expected: 0

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : myEvenSumParity [] = 0 := by native_decide
#eval myEvenSumParity [] -- expected: 0

/-- expected: 0 -/
example : myEvenSumParity [2] = 0 := by native_decide
#eval myEvenSumParity [2] -- expected: 0

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: any number of even numbers sum to even (parity 0) -/
example : myEvenSumParity [2, 4] = 0 := by native_decide
#eval myEvenSumParity [2, 4] -- expected: 0

/-- positive: three even numbers still sum to even -/
example : myEvenSumParity [2, 4, 8] = 0 := by native_decide
#eval myEvenSumParity [2, 4, 8] -- expected: 0

/-- negative: result should only be 0 or 1 -/
example : ¬ (myEvenSumParity [2, 4, 6] > 1) := by native_decide
#eval (decide (myEvenSumParity [2, 4, 6] > 1)) -- expected: false

/-- negative: empty list should not have odd parity -/
example : ¬ (myEvenSumParity [] = 1) := by native_decide
#eval (decide (myEvenSumParity [] = 1)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: 2 + 4 = 6, parity 0 -/
example : myEvenSumParityImp [2, 4] = 0 := by native_decide
#eval myEvenSumParityImp [2, 4] -- expected: 0

/-- negative: result should only be 0 or 1 -/
example : ¬ (myEvenSumParityImp [2, 4, 6] > 1) := by native_decide
#eval (decide (myEvenSumParityImp [2, 4, 6] > 1)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
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

theorem myEvenSumParity_equivalence_thm (xs : List Nat) :
  myEvenSumParity xs = myEvenSumParityImp xs := by
  unfold myEvenSumParity myEvenSumParityImp parity
  simpa using (sum_loop_mod_aux xs 0).symm




end MyEvenSumParity