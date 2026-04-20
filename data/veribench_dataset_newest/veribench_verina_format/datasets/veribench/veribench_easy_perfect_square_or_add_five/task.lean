-- !benchmark @start import type=solution
import Mathlib
namespace PerfectSquareOrAddFive
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def perfectSquareOrAddFive_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

/-- Returns true if `n` is a perfect square, using an imperative loop. -/
def isPerfectSquare (n : Nat) : Bool :=
  Id.run do
    let mut k := 0
    while k * k ≤ n do
      if k * k = n then
        return true
      k := k + 1
    return false

-- !benchmark @end code_aux

def perfectSquareOrAddFive (n : Nat) (h_precond : perfectSquareOrAddFive_precond (n)) : Nat :=
  -- !benchmark @start code
  if isPerfectSquare n then n else n + 5
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def perfectSquareOrAddFive_postcond (n : Nat) (result : Nat)
    (h_precond : perfectSquareOrAddFive_precond (n)) : Prop :=
  -- !benchmark @start postcond
  result = n ∨ result = n + 5
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

/-- **Perfect square property**: Perfect squares return themselves. -/
def perfect_square_prop (n : Nat) : Prop :=
  (∃ k, k * k = n) → perfectSquareOrAddFive n (by simp) = n

/-- **Perfect square theorem**: Perfect squares return themselves. -/
@[simp] theorem perfect_square_thm (n : Nat) : perfect_square_prop n := by
  sorry

/-- **Non-perfect square property**: Non-perfect squares get 5 added. -/
def non_perfect_square_prop (n : Nat) : Prop :=
  (∀ k, k * k ≠ n) → perfectSquareOrAddFive n (by simp) = n + 5

/-- **Non-perfect square theorem**: Non-perfect squares get 5 added. -/
@[simp] theorem non_perfect_square_thm (n : Nat) : non_perfect_square_prop n := by
  sorry

/-- **Zero property**: Zero is a perfect square. -/
def zero_prop : Prop :=
  perfectSquareOrAddFive 0 (by simp) = 0

/-- **Zero theorem**: Zero is a perfect square. -/
@[simp] theorem zero_thm : zero_prop := by
  sorry

/-- **Result bounds property**: Result is either n or n+5. -/
def result_bounds_prop (n : Nat) : Prop :=
  perfectSquareOrAddFive n (by simp) = n ∨ perfectSquareOrAddFive n (by simp) = n + 5

/-- **Result bounds theorem**: Result is either n or n+5. -/
@[simp] theorem result_bounds_thm (n : Nat) : result_bounds_prop n := by
  sorry

/-- **Monotonicity property**: If n is perfect square, result equals n. -/
def monotonicity_prop (n : Nat) : Prop :=
  isPerfectSquare n = true → perfectSquareOrAddFive n (by simp) = n

/-- **Monotonicity theorem**: If n is perfect square, result equals n. -/
@[simp] theorem monotonicity_thm (n : Nat) : monotonicity_prop n := by
  sorry

-- !benchmark @end proof_aux

theorem perfectSquareOrAddFive_spec_satisfied (n : Nat)
    (h_precond : perfectSquareOrAddFive_precond (n)) :
    perfectSquareOrAddFive_postcond (n) (perfectSquareOrAddFive (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof