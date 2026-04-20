import Mathlib

namespace MyPower


def myPower : Nat → Nat → Nat
  | _, 0 => 1
  | b, e + 1 => b * myPower b e


def myPowerImp (b e : Nat) : Nat :=
  if e = 0 then 1
  else (List.range' 0 e).foldl (fun acc _ => acc * b) 1



/-!
# Tests
-/

/-- expected: 8 -/
example : myPower 2 3 = 8 := by native_decide
#eval myPower 2 3 -- expected: 8

/-- expected: 9 -/
example : myPower 3 2 = 9 := by native_decide
#eval myPower 3 2 -- expected: 9

/-!
# Tests: Edge Cases
-/

/-- expected: 1 (any base to power 0) -/
example : myPower 0 0 = 1 := by native_decide
#eval myPower 0 0 -- expected: 1

/-- expected: 5 (any base to power 1) -/
example : myPower 5 1 = 5 := by native_decide
#eval myPower 5 1 -- expected: 5

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: any number to power 0 is 1 -/
example : myPower 7 0 = 1 := by native_decide
#eval myPower 7 0 -- expected: 1

/-- positive: 1 to any power is 1 -/
example : myPower 1 5 = 1 := by native_decide
#eval myPower 1 5 -- expected: 1

/-- negative: zero base with positive exponent should be zero -/
example : ¬ (myPower 0 3 ≠ 0) := by native_decide
#eval (decide (myPower 0 3 ≠ 0)) -- expected: false

/-- negative: power should not decrease with larger exponent (for base > 1) -/
example : ¬ (myPower 3 3 < myPower 3 2) := by native_decide
#eval (decide (myPower 3 3 < myPower 3 2)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: maintains power computation -/
example : myPowerImp 3 3 = 27 := by native_decide
#eval myPowerImp 3 3 -- expected: 27

/-- negative: zero base with positive exponent should be zero -/
example : ¬ (myPowerImp 0 2 ≠ 0) := by native_decide
#eval (decide (myPowerImp 0 2 ≠ 0)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem power_foldl_aux (xs : List Nat) (b acc : Nat) :
    xs.foldl (fun acc _ => acc * b) acc = acc * myPower b xs.length := by
  induction xs generalizing acc with
  | nil =>
      simp [myPower]
  | cons x xs ih =>
      simp [ih, myPower, Nat.mul_assoc]

theorem myPower_equivalence_thm (b e : Nat) :
  myPower b e = myPowerImp b e := by
  unfold myPowerImp
  by_cases h : e = 0
  · simp [h, myPower]
  · simp [h]
    simpa [List.length_range', Nat.one_mul, Nat.mul_assoc] using
      (power_foldl_aux (List.range' 0 e) b 1).symm




end MyPower