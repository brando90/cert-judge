import Mathlib

example (n : Nat) : 0 + n = n := by
  simpa using Nat.zero_add n
