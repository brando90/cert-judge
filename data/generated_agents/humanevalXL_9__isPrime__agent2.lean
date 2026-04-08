import VeriBench.Common
import Batteries.Data.Int.Basic

namespace IsPrime

/--
Return true if a given number is prime, and false otherwise.
-/
def isPrime (n : Int) : Bool :=
  if n < 2 then
    false
  else
    let rec checkDivisors (k : Int) : Bool :=
      if k ≥ n - 1 then
        true
      else if n % k == 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/-- Predicate stating that `n` has no divisors in the range `[2, n-1]` -/
def hasNoDivisorsInRange (n : Int) (from to : Int) : Prop :=
  ∀ k, from ≤ k → k ≤ to → n % k ≠ 0

/-- Predicate for primality -/
def isPrimeSpec (n : Int) : Prop :=
  n ≥ 2 ∧ hasNoDivisorsInRange n 2 (n - 2)

/-- Specification for the `isPrime` function -/
theorem isPrime_spec (n : Int) : isPrime n = true ↔ isPrimeSpec n := by
  sorry

/-- Tests for the `isPrime` function -/
def isPrime_test : IO Unit := do
  VeriBench.Common.test "isPrime 0" (isPrime 0) false
  VeriBench.Common.test "isPrime 6" (isPrime 6) false
  VeriBench.Common.test "isPrime 101" (isPrime 101) true
  VeriBench.Common.test "isPrime 11" (isPrime 11) true
  VeriBench.Common.test "isPrime 13441" (isPrime 13441) true
  VeriBench.Common.test "isPrime 61" (isPrime 61) true
  VeriBench.Common.test "isPrime 4" (isPrime 4) false
  VeriBench.Common.test "isPrime 1" (isPrime 1) false
  VeriBench.Common.test "isPrime 5" (isPrime 5) true
  VeriBench.Common.test "isPrime 17" (isPrime 17) true
  VeriBench.Common.test "isPrime (5 * 17)" (isPrime (5 * 17)) false
  VeriBench.Common.test "isPrime (11 * 7)" (isPrime (11 * 7)) false
  VeriBench.Common.test "isPrime (13441 * 19)" (isPrime (13441 * 19)) false

end IsPrime
