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
      if k >= n - 1 then
        true
      else if n % k == 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/-- Tests for isPrime function -/
def tests : List (Nat × Bool) := [
  (0, false),
  (1, false),
  (2, true),
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

/-- Specification for isPrime: a number is prime iff it has exactly two divisors: 1 and itself -/
def isPrimeSpec (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let divisors := List.filter (fun k => n % k == 0) (List.range (n + 1))
    divisors.length == 2

/-- Correctness theorem for isPrime -/
theorem isPrime_correct (n : Nat) : isPrime n = isPrimeSpec n := by
  sorry

/-- Run the tests -/
def runTests : IO Unit := do
  for (input, expected) in tests do
    let result := isPrime input
    if result != expected then
      throw (IO.userError s!"Test failed for input {input}: expected {expected} but got {result}")
    IO.println s!"Test passed for input {input}"
  IO.println "All tests passed!"

end IsPrime
