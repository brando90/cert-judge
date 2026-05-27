import Mathlib

example (n : Nat) : 0 + n = n := by
  induction n with
  | zero =>
      rfl
  | succ n ih =>
      change Nat.succ (0 + n) = Nat.succ n
      rw [ih]
