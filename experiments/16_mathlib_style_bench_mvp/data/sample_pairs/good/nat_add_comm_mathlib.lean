import Mathlib

example (a b : Nat) : a + b = b + a := by
  simpa using Nat.add_comm a b
