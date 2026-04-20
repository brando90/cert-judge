import Mathlib

namespace MyFactorial


def myFactorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * myFactorial n


def myFactorialImp (n : Nat) : Nat :=
  (List.range' 1 n).foldl (fun acc i => acc * i) 1



/-!
# Tests
-/

/-- expected: 6 -/
example : myFactorial 3 = 6 := by native_decide
#eval myFactorial 3 -- expected: 6

/-- expected: 24 -/
example : myFactorial 4 = 24 := by native_decide
#eval myFactorial 4 -- expected: 24

/-!
# Tests: Edge Cases
-/

/-- expected: 1 (base case) -/
example : myFactorial 0 = 1 := by native_decide
#eval myFactorial 0 -- expected: 1

/-- expected: 1 -/
example : myFactorial 1 = 1 := by native_decide
#eval myFactorial 1 -- expected: 1

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: factorial of small numbers -/
example : myFactorial 2 = 2 := by native_decide
#eval myFactorial 2 -- expected: 2

/-- positive: factorial of medium numbers -/
example : myFactorial 5 = 120 := by native_decide
#eval myFactorial 5 -- expected: 120

/-- negative: factorial should not be zero for any input -/
example : ¬ (myFactorial 3 = 0) := by native_decide
#eval (decide (myFactorial 3 = 0)) -- expected: false

/-- negative: factorial should not decrease -/
example : ¬ (myFactorial 4 < myFactorial 3) := by native_decide
#eval (decide (myFactorial 4 < myFactorial 3)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: maintains factorial computation -/
example : myFactorialImp 5 = 120 := by native_decide
#eval myFactorialImp 5 -- expected: 120

/-- negative: should not be zero -/
example : ¬ (myFactorialImp 4 = 0) := by native_decide
#eval (decide (myFactorialImp 4 = 0)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem myFactorial_eq_factorial (n : Nat) : myFactorial n = Nat.factorial n := by
  induction n with
  | zero =>
      simp [myFactorial]
  | succ n ih =>
      simp [myFactorial, ih, Nat.factorial_succ, Nat.mul_comm]

private theorem foldl_mul_range_aux (start len acc : Nat) :
    (List.range' start len).foldl (fun acc i => acc * i) acc = acc * start.ascFactorial len := by
  induction len generalizing start acc with
  | zero =>
      simp [Nat.ascFactorial_zero]
  | succ len ih =>
      rw [List.range'_succ, List.foldl_cons, ih]
      simp [Nat.ascFactorial_succ, Nat.succ_ascFactorial, Nat.mul_assoc]

theorem myFactorial_equivalence_thm (n : Nat) :
  myFactorial n = myFactorialImp n := by
  unfold myFactorialImp
  simpa [myFactorial_eq_factorial, Nat.one_ascFactorial] using
    (foldl_mul_range_aux 1 n 1).symm




end MyFactorial