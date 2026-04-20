-- !benchmark @start import type=solution
import Mathlib
namespace MyPrime
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Helper function to check if a number is divisible by any number in a range -/
partial def hasDivisorInRange (n start end_val : Nat) : Bool :=
  if start > end_val then
    false
  else if n % start = 0 then
    true
  else
    hasDivisorInRange n (start + 1) end_val
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def isPrime_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

partial def isPrime (n : Nat) (h_precond : isPrime_precond (n)) : Bool :=
  -- !benchmark @start code
  if n ≤ 1 then
    false
  else if n ≤ 3 then
    true
  else if n % 2 = 0 ∨ n % 3 = 0 then
    false
  else
    let sqrt_n := (Float.floor (Float.sqrt (n.toFloat))).toUInt64.toNat
    let rec check (i : Nat) : Bool :=
      if i > sqrt_n then
        true
      else if n % i = 0 ∨ n % (i + 2) = 0 then
        false
      else
        check (i + 6)
    check 5
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- Property props and their theorems (kept as auxiliary declarations for the spec).

/-- **Base cases property**: 0 and 1 are not prime, 2 is prime. -/
def base_cases_prop : Prop :=
  isPrime 0 (by simp) = false ∧ isPrime 1 (by simp) = false ∧ isPrime 2 (by simp) = true

/-- **Base cases theorem**: 0 and 1 are not prime, 2 is prime. -/
@[simp] theorem base_cases_thm : base_cases_prop := by
  sorry

/-- **Composite property**: If n has a divisor other than 1 and n, then n is not prime. -/
def composite_prop (n : Nat) : Prop :=
  (n > 1 ∧ ∃ d, d > 1 ∧ d < n ∧ n % d = 0) → isPrime n (by simp) = false

/-- **Composite theorem**: If n has a divisor other than 1 and n, then n is not prime. -/
@[simp] theorem composite_thm (n : Nat) : composite_prop n := by
  sorry

/-- **Boolean result property**: Result is always true or false. -/
def boolean_result_prop (n : Nat) : Prop :=
  isPrime n (by simp) = true ∨ isPrime n (by simp) = false

/-- **Boolean result theorem**: Result is always true or false. -/
@[simp] theorem boolean_result_thm (n : Nat) : boolean_result_prop n := by
  sorry

/-- **Even non-prime property**: Even numbers greater than 2 are not prime. -/
def even_non_prime_prop (n : Nat) : Prop :=
  (n > 2 ∧ n % 2 = 0) → isPrime n (by simp) = false

/-- **Even non-prime theorem**: Even numbers greater than 2 are not prime. -/
@[simp] theorem even_non_prime_thm (n : Nat) : even_non_prime_prop n := by
  sorry
-- !benchmark @end postcond_aux

@[reducible, simp]
def isPrime_postcond (n : Nat) (result : Bool) (h_precond : isPrime_precond (n)) : Prop :=
  -- !benchmark @start postcond
  (base_cases_prop) ∧
    (composite_prop n) ∧
    (boolean_result_prop n) ∧
    (even_non_prime_prop n)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem isPrime_spec_satisfied (n : Nat) (h_precond : isPrime_precond (n)) :
    isPrime_postcond (n) (isPrime (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof