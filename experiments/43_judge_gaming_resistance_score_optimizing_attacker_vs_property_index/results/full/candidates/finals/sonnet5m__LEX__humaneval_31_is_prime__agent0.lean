import Mathlib
/-
File: humaneval_31_is_prime.lean
-/

import Mathlib.Tactic


/--
Return true if a given number is prime, and false otherwise.
-/
def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec checkDivisors (k : Nat) : Bool :=
      if k ≥ n - 1 then
        true
      else if n % k == 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/-- The Boolean result of `isPrime` agrees with primality. -/
def isPrimeSpec (n : Nat) : Prop :=
  isPrime n = true ↔ Nat.Prime n

/-- The implementation satisfies its primality specification. -/
theorem isPrime_correct (n : Nat) : isPrimeSpec n := by
  sorry

/-- The implementation returns the expected results on the supplied examples. -/
theorem isPrime_examples :
    isPrime 6 = false ∧
    isPrime 101 = true ∧
    isPrime 11 = true ∧
    isPrime 13441 = true ∧
    isPrime 61 = true ∧
    isPrime 4 = false ∧
    isPrime 1 = false ∧
    isPrime 5 = true ∧
    isPrime 17 = true ∧
    isPrime (5 * 17) = false ∧
    isPrime (11 * 7) = false ∧
    isPrime (13441 * 19) = false := by
  native_decide

/-- Test suite for `isPrime` -/
def isPrimeTests : List (Nat × Bool) := [
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

/-- Run the test suite for `isPrime` -/
def runIsPrimeTests : IO Unit := do
  for (input, expected) in isPrimeTests do
    let actual := isPrime input
    if actual != expected then
      throw (IO.userError s!"Test failed: isPrime {input} = {actual}, but expected {expected}")
  IO.println "All tests passed!"

def main : IO Unit :=
  runIsPrimeTests
