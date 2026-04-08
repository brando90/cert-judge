import Mathlib.Tactic.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Nat.Pow

/- Return base raised to the power of exponent for natural numbers.

   Edge cases:
   - power(n, 0) = 1 for any n
   - power(0, n) = 0 for n > 0
   - power(0, 0) = 1 by convention
-/

def power (base : Nat) (exponent : Nat) : Nat :=
  match exponent with
  | 0 => 1
  | _ + 1 => base * power base exponent

/- Tests -/

#eval power 2 3 -- 8
#eval power 0 0 -- 1
#eval power 5 0 -- 1
#eval power 0 5 -- 0

/- Specification -/

def powerSpec (base : Nat) (exponent : Nat) : Nat :=
  base ^ exponent

/- Verification -/

theorem power_correct (base : Nat) (exponent : Nat) : 
  power base exponent = powerSpec base exponent := by
  induction exponent with
  | zero => 
    simp [power, powerSpec, Nat.pow_zero]
  | succ n ih =>
    simp [power, powerSpec, Nat.pow_succ]
    rw [ih]
    sorry
