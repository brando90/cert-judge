import Std.Data.Nat.Basic
import Std.Tactic.Basic
import Std.Data.Int.Basic

/--
  Return max(a, b) for non-negative integers a and b.
-/
def max_nat (a : Nat) (b : Nat) : Nat :=
  if a ≤ b then b else a

/--
  The precondition for max_nat: both inputs must be natural numbers.
  In Lean, this is automatically satisfied by the type system.
-/
def max_nat_pre (a : Nat) (b : Nat) : Prop := True

/--
  The postcondition for max_nat: the result is the maximum of the two inputs.
-/
def max_nat_post (a : Nat) (b : Nat) (result : Nat) : Prop :=
  result = max a b

/--
  Correctness theorem: max_nat satisfies its postcondition when the precondition is met.
-/
theorem max_nat_correct (a : Nat) (b : Nat) (pre : max_nat_pre a b) :
  max_nat_post a b (max_nat a b) := by
  unfold max_nat_post
  unfold max_nat
  simp [max]
  split
  . simp [Nat.max_eq_right]
    intro h
    exact h
  . simp [Nat.max_eq_left]
    intro h
    exact Nat.not_le.mp h

/--
  Unit tests for max_nat
-/
def max_nat_tests : IO Unit := do
  -- Basic test
  assert! (max_nat 7 3 = 7)
  
  -- Edge case
  assert! (max_nat 0 0 = 0)
  
  -- Symmetric test
  assert! (max_nat 3 7 = 7)
  
  -- Additional test
  assert! (max_nat 5 5 = 5)
  
  IO.println "All tests passed!"
