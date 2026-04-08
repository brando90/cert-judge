import VeriBench

namespace IsPrime

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

/-- Tests for isPrime -/
def tests : List (Nat × Bool) := [
  (0, false),
  (1, false),
  (4, false),
  (5, true),
  (6, false),
  (11, true),
  (17, true),
  (61, true),
  (85, false), -- 5 * 17
  (77, false), -- 11 * 7
  (101, true),
  (13441, true),
  (255379, false) -- 13441 * 19
]

/-- Runs the tests for isPrime -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let actual := isPrime input
    if actual != expected then
      throw (IO.userError s!"Test failed for input {input}. Expected: {expected}, Actual: {actual}")
  IO.println "All tests passed!"

/-- The function isPrime should return true if the input is prime, false otherwise -/
def isPrimeSpec (n : Nat) (result : Bool) : Prop :=
  result = true ↔ (n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → n % k ≠ 0)

/-- isPrime satisfies isPrimeSpec -/
theorem isPrime_correct (n : Nat) : isPrimeSpec n (isPrime n) := by
  sorry

end IsPrime

def main : IO Unit := IsPrime.runTests
