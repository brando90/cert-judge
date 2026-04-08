import Mathlib.Tactic.Basic
import Mathlib.Data.Nat.Prime
import Mathlib.Data.Nat.Sqrt

/--
Check if a non-negative integer is prime.
A prime number is a natural number greater than 1 that is not divisible by any positive integer other than 1 and itself.

Edge cases:
- 0 and 1 are not prime.
-/

def isPrime (n : Nat) : Bool :=
  if n ≤ 1 then
    false
  else if n ≤ 3 then
    true
  else if n % 2 == 0 || n % 3 == 0 then
    false
  else
    let sqrtN := n.sqrt
    let rec checkDivisors (i : Nat) : Bool :=
      if i > sqrtN then
        true
      else if n % i == 0 || n % (i + 2) == 0 then
        false
      else
        checkDivisors (i + 6)
    checkDivisors 5

/-- Predicate defining when isPrime should return true -/
def isPrimePred (n : Nat) : Prop :=
  Nat.Prime n

/-- Precondition: n must be a non-negative integer -/
def isPrimePre (n : Nat) : Prop := True

/-- Postcondition: isPrime returns true iff n is prime -/
def isPrimePost (n : Nat) (result : Bool) : Prop :=
  result = true ↔ isPrimePred n

/-- Correctness theorem: isPrime satisfies its specification -/
theorem isPrimeCorrect (n : Nat) (h : isPrimePre n) : isPrimePost n (isPrime n) := by
  sorry

/-- Test cases for isPrime -/
def testIsPrime : IO Unit := do
  -- Basic case
  IO.println s!"isPrime 7 = {isPrime 7}"
  assert! (isPrime 7 = true)

  -- Edge cases
  IO.println s!"isPrime 0 = {isPrime 0}"
  assert! (isPrime 0 = false)
  IO.println s!"isPrime 1 = {isPrime 1}"
  assert! (isPrime 1 = false)
  
  -- Other test cases
  IO.println s!"isPrime 2 = {isPrime 2}"
  assert! (isPrime 2 = true)
  IO.println s!"isPrime 3 = {isPrime 3}"
  assert! (isPrime 3 = true)
  IO.println s!"isPrime 4 = {isPrime 4}"
  assert! (isPrime 4 = false)
  IO.println s!"isPrime 13 = {isPrime 13}"
  assert! (isPrime 13 = true)
  IO.println s!"isPrime 15 = {isPrime 15}"
  assert! (isPrime 15 = false)
  IO.println s!"isPrime 97 = {isPrime 97}"
  assert! (isPrime 97 = true)

#eval testIsPrime
