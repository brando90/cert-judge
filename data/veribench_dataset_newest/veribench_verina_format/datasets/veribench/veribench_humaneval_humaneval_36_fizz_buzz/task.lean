-- !benchmark @start import type=solution
import Mathlib
namespace FizzBuzz
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def fizzBuzz_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def fizzBuzz (n : Nat) (h_precond : fizzBuzz_precond (n)) : Nat :=
  -- !benchmark @start code
  let ns := (List.range n).filter (fun i => i % 11 = 0 ∨ i % 13 = 0)
  let s := String.join (ns.map toString)
  s.data.foldl (fun acc c => acc + if c = '7' then 1 else 0) 0
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Non-negative property**: The count is always non-negative. -/
def non_negative_prop (n : Nat) : Prop := fizzBuzz (n) (by simp) ≥ 0

/-- **Non-negative theorem**: The count is always non-negative. -/
@[simp] theorem non_negative_thm (n : Nat) : non_negative_prop n := sorry

/-- **Monotonicity property**: Increasing n cannot decrease the count. -/
def monotonicity_prop (n m : Nat) : Prop := n ≤ m → fizzBuzz (n) (by simp) ≤ fizzBuzz (m) (by simp)

/-- **Monotonicity theorem**: Increasing n cannot decrease the count. -/
@[simp] theorem monotonicity_thm (n m : Nat) : monotonicity_prop n m := sorry

/-- **Small inputs property**: The count is zero for inputs less than 11. -/
def small_inputs_prop (n : Nat) : Prop := n < 11 → fizzBuzz (n) (by simp) = 0

/-- **Small inputs theorem**: The count is zero for inputs less than 11. -/
@[simp] theorem small_inputs_thm (n : Nat) : small_inputs_prop n := sorry

/-- **Bounded property**: The count is bounded by the number of divisible numbers. -/
def bounded_prop (n : Nat) : Prop :=
  fizzBuzz (n) (by simp) ≤ ((List.range n).filter (fun i => i % 11 = 0 ∨ i % 13 = 0)).length

/-- **Bounded theorem**: The count is bounded by the number of divisible numbers. -/
@[simp] theorem bounded_thm (n : Nat) : bounded_prop n := sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def fizzBuzz_postcond (n : Nat) (result : Nat) (h_precond : fizzBuzz_precond (n)) :=
  -- !benchmark @start postcond
  (result ≥ 0) ∧
    (∀ m, n ≤ m → result ≤ fizzBuzz (m) (by simp)) ∧
    (n < 11 → result = 0) ∧
    (result ≤ ((List.range n).filter (fun i => i % 11 = 0 ∨ i % 13 = 0)).length)
  -- !benchmark @end postcond

theorem fizzBuzz_spec_satisfied (n : Nat) (h_precond : fizzBuzz_precond (n)) :
    fizzBuzz_postcond (n) (fizzBuzz (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof