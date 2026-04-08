/-
File: humaneval_31_is_prime.lean
-/

import Mathlib.Tactic
import Mathlib.Data.Nat.Prime

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

/-- Predicate stating that `isPrime` returns true if and only if n is prime. -/
def isPrimeSpec (n : Nat) : Prop :=
  isPrime n = Nat.Prime n

/-- Theorem stating that `isPrime` satisfies its specification. -/
theorem isPrime_correct (n : Nat) : isPrimeSpec n := by
  sorry

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
