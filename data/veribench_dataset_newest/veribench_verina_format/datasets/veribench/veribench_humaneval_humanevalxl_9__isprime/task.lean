-- !benchmark @start import type=solution
import Mathlib
namespace IsPrime
-- !benchmark @end import

-- !benchmark @start solution_aux
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
  if n < 2 then false
  else
    let rec check (k : Nat) : Bool :=
      if k * k > n then true
      else if n % k == 0 then false
      else check (k + 1)
    check 2
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
/-- **Helper**: Mathematical definition of primality. -/
def isPrimeNumber (n : Nat) : Prop :=
  n ≥ 2 ∧ ∀ k, 2 ≤ k ∧ k < n → n % k ≠ 0

/-- **Zero property**: Zero is not prime. -/
def zero_prop : Prop := isPrime 0 (by simp) = false

/-- **Zero theorem**: Zero is not prime. -/
@[simp] theorem zero_thm : zero_prop := sorry

/-- **One property**: One is not prime. -/
def one_prop : Prop := isPrime 1 (by simp) = false

/-- **One theorem**: One is not prime. -/
@[simp] theorem one_thm : one_prop := sorry

/-- **Two property**: Two is prime. -/
def two_prop : Prop := isPrime 2 (by simp) = true

/-- **Two theorem**: Two is prime. -/
@[simp] theorem two_thm : two_prop := sorry

/-- **Small numbers property**: All numbers less than 2 are not prime. -/
def small_numbers_prop (n : Nat) : Prop := n < 2 → isPrime n (by simp) = false

/-- **Small numbers theorem**: All numbers less than 2 are not prime. -/
@[simp] theorem small_numbers_thm (n : Nat) : small_numbers_prop n := sorry

/-- **Equivalence property**: isPrime matches mathematical definition. -/
def equivalence_prop (n : Nat) : Prop := isPrime n (by simp) = true ↔ isPrimeNumber n
-- !benchmark @end proof_aux

@[reducible, simp]
def isPrime_postcond (n : Nat) (result : Bool) (h_precond : isPrime_precond (n)) : Prop :=
  -- !benchmark @start postcond
  (zero_prop) ∧
  (one_prop) ∧
  (two_prop) ∧
  (small_numbers_prop n) ∧
  (equivalence_prop n)
  -- !benchmark @end postcond

theorem isPrime_spec_satisfied (n : Nat) (h_precond : isPrime_precond (n)) :
    isPrime_postcond (n) (isPrime (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof