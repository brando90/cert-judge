-- !benchmark @start import type=solution
import Mathlib
namespace PrimeFib
-- !benchmark @end import

-- !benchmark @start solution_aux
def isPrime (n : Nat) : Bool :=
  if n < 2 then false
  else
    let rec checkDivisors (k : Nat) (fuel : Nat) : Bool :=
      if fuel = 0 then true
      else if k * k > n then true
      else if n % k = 0 then false
      else checkDivisors (k + 1) (fuel - 1)
    checkDivisors 2 n

def fib : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def prime_fib_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  n > 0
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def prime_fib (n : Nat) (h_precond : prime_fib_precond (n)) : Nat :=
  -- !benchmark @start code
  let rec helper (count : Nat) (i : Nat) (n : Nat) (fuel : Nat) : Nat :=
    if fuel = 0 then 0
    else
      let f := fib i
      if isPrime f then
        if count + 1 = n then f
        else helper (count + 1) (i + 1) n (fuel - 1)
      else
        helper count (i + 1) n (fuel - 1)
  helper 0 3 n 1000
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def prime_fib_postcond (n : Nat) (result : Nat) (h_precond : prime_fib_precond (n)) : Prop :=
  -- !benchmark @start postcond
  (n > 0 → result > 0) ∧
    (n > 0 → isPrime result) ∧
    (n > 0 → ∃ k, fib k = result) ∧
    (n > 0 → result < prime_fib (n + 1) (by sorry))
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def positivity_prop (n : Nat) : Prop :=
  n > 0 → prime_fib n (by sorry) > 0

@[simp] theorem positivity_thm (n : Nat) : positivity_prop n := by
  sorry

def primality_prop (n : Nat) : Prop :=
  n > 0 → isPrime (prime_fib n (by sorry))

@[simp] theorem primality_thm (n : Nat) : primality_prop n := by
  sorry

def fibonacci_property_prop (n : Nat) : Prop :=
  n > 0 → ∃ k, fib k = prime_fib n (by sorry)

@[simp] theorem fibonacci_property_thm (n : Nat) : fibonacci_property_prop n := by
  sorry

def monotonicity_prop (n : Nat) : Prop :=
  n > 0 → prime_fib n (by sorry) < prime_fib (n + 1) (by sorry)

@[simp] theorem monotonicity_thm (n : Nat) : monotonicity_prop n := by
  sorry

-- !benchmark @end proof_aux

theorem prime_fib_spec_satisfied (n : Nat) (h_precond : prime_fib_precond (n)) :
    prime_fib_postcond (n) (prime_fib (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof

end PrimeFib