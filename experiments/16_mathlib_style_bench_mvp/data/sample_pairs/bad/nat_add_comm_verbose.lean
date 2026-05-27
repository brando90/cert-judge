import Mathlib

example (a b : Nat) : a + b = b + a := by
  induction b with
  | zero =>
      rw [Nat.add_zero]
      rfl
  | succ b ih =>
      rw [Nat.add_succ, ih, Nat.succ_add]
