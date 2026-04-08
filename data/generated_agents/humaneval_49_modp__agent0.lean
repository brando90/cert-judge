import Mathlib.Tactic
import Mathlib.Data.Nat.ModEq
import Mathlib.Data.Nat.Order.Basic
import Mathlib.Data.Nat.Pow
import Std.Data.Nat.Lemmas

namespace VeriBench.HumanEval.Prob49

/-- Return 2^n modulo p (be aware of numerics). -/
def modp (n p : Nat) : Nat :=
  let rec helper (i acc : Nat) : Nat :=
    if i = n then
      acc
    else
      helper (i + 1) ((2 * acc) % p)
  helper 0 1

/-- Specification of modp in terms of Nat.pow -/
def modp_spec (n p : Nat) : Nat :=
  (2 ^ n) % p

theorem modp_eq_modp_spec (n p : Nat) (h : p > 0) : modp n p = modp_spec n p := by
  unfold modp modp_spec
  have helper_correct : ∀ i acc, i ≤ n → acc = (2^i % p) → helper i acc = (2^n % p) := by
    intro i acc i_le_n acc_eq
    induction i generalizing acc with
    | zero =>
      simp at acc_eq
      subst acc_eq
      cases Nat.eq_or_lt_of_le i_le_n with
      | inl i_eq_n =>
        subst i_eq_n
        simp [helper]
      | inr i_lt_n =>
        simp [helper]
        apply ih
        · exact Nat.le_of_lt_succ (Nat.succ_lt_succ i_lt_n)
        · simp [Nat.pow_succ]
          rw [← Nat.mul_mod, acc_eq]
    | succ i ih =>
      cases Nat.eq_or_lt_of_le i_le_n with
      | inl i_succ_eq_n =>
        simp [helper, i_succ_eq_n]
      | inr i_succ_lt_n =>
        simp [helper, i_succ_lt_n.decide_eq_false]
        apply ih
        · exact Nat.le_of_lt_succ (Nat.succ_lt_succ i_succ_lt_n)
        · simp [Nat.pow_succ]
          rw [← Nat.mul_mod, acc_eq]

  apply helper_correct 0 1 (Nat.zero_le n)
  simp

/-- Tests for modp -/
def tests : List (Nat × Nat × Nat) := [
  (3, 5, 3),
  (1101, 101, 2),
  (0, 101, 1),
  (3, 11, 8),
  (100, 101, 1),
  (30, 5, 4),
  (31, 5, 3)
]

/-- Run tests for modp -/
def runTests : IO Unit := do
  for (n, p, expected) in tests do
    let result := modp n p
    if result != expected then
      throw (IO.userError s!"Test failed: modp {n} {p} = {result}, expected {expected}")
  IO.println "All tests passed!"

/-- Precondition for modp: p must be positive -/
def modp_pre (n p : Nat) : Prop :=
  p > 0

/-- Postcondition for modp: result is 2^n mod p -/
def modp_post (n p result : Nat) : Prop :=
  result = (2 ^ n) % p

/-- Correctness theorem for modp -/
theorem modp_correct (n p : Nat) (h : modp_pre n p) : modp_post n p (modp n p) := by
  unfold modp_post
  rw [modp_eq_modp_spec n p h]
  unfold modp_spec
  rfl

end VeriBench.HumanEval.Prob49
