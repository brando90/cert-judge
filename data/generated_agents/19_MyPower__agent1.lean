import Mathlib.Tactic

/-- Return base raised to the power of exponent for natural numbers.

Edge cases:
- power(n, 0) = 1 for any n
- power(0, n) = 0 for n > 0
- power(0, 0) = 1 by convention
-/

def pre (base : Nat) (exponent : Nat) : Prop :=
  True  -- All natural numbers satisfy the precondition

def power (base : Nat) (exponent : Nat) : Nat :=
  match exponent with
  | 0 => 1
  | _ + 1 => base * power base exponent

def post (base : Nat) (exponent : Nat) (result : Nat) : Prop :=
  result = base ^ exponent

theorem power_correct (base : Nat) (exponent : Nat)
    (h : pre base exponent) :
    post base exponent (power base exponent) := by
  unfold post
  induction exponent with
  | zero => simp [power]
  | succ n ih => 
    simp [power]
    rw [pow_succ]
    rw [ih]
  sorry

-- Tests
#eval power 2 3 -- 8
#eval power 0 0 -- 1
#eval power 3 0 -- 1
#eval power 0 5 -- 0
#eval power 2 10 -- 1024

example : power 2 3 = 8 := by rfl
example : power 0 0 = 1 := by rfl
example : power 3 0 = 1 := by rfl
example : power 0 5 = 0 := by
  simp [power]
  repeat rw [Nat.mul_zero]

example : power 2 10 = 1024 := by rfl
