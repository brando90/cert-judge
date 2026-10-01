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

/-- isPrime n returns true if n is a prime number, false otherwise. -/
theorem isPrime_spec (n : Nat) : 
  isPrime n = true ↔ n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → ¬(k ∣ n) := by
  sorry

/-- Tests for the isPrime function -/
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

/- Run all tests -/
#eval isPrime_tests.all (fun (input, expected) => isPrime input == expected)
