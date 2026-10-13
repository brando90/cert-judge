import Mathlib

/-
This file defines the `isPrime` function that determines if a number is prime.
-/

def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec checkDivisors (k : Nat) : Bool :=
      if k >= n - 1 then
        true
      else if n % k == 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/-- `isPrime` agrees with the trial-division divisibility specification. -/
theorem isPrime_spec (n : Nat) :
  isPrime n = true ↔ n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → ¬(k ∣ n) := by
  sorry

/-- A modulo-based version of the trial-division specification. -/
def IsPrimeByTrialDivision (n : Nat) : Prop :=
  n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → n % k ≠ 0

theorem isPrime_trialDivision_spec (n : Nat) :
    isPrime n = true ↔ IsPrimeByTrialDivision n := by
  sorry

/-- The trial-division implementation recognizes exactly the natural primes. -/
theorem isPrime_eq_true_iff_nat_prime (n : Nat) :
    isPrime n = true ↔ Nat.Prime n := by
  sorry

theorem isPrime_eq_false_iff_not_nat_prime (n : Nat) :
    isPrime n = false ↔ ¬ Nat.Prime n := by
  sorry

theorem isPrime_below_two (n : Nat) (h : n < 2) :
    isPrime n = false := by
  simp [isPrime, h]

/-- Tests for the `isPrime` function. -/
def isPrime_tests : List (Nat × Bool) := [
  (6, false),
  (101, true),
  (11, true),
  (13441, true),
  (61, true),
  (4, false),
  (1, false),
  (5, true),
  (17, true),
  (5 * 17, false),
  (11 * 7, false),
  (13441 * 19, false)
]

theorem isPrime_tests_pass :
    isPrime_tests.all (fun (input, expected) => isPrime input == expected) = true := by
  native_decide

/- Run all tests -/
#eval isPrime_tests.all (fun (input, expected) => isPrime input == expected)
