import Mathlib.Tactic.LibrarySearch
import Mathlib.Data.Nat.Prime

namespace VeriBench.IsPrime

/--
  Check if a non-negative integer is prime.
  A prime number is a natural number greater than 1 that is not divisible by any positive integer other than 1 and itself.
-/
def isPrime (n : Nat) : Bool :=
  if n ≤ 1 then
    false
  else if n ≤ 3 then
    true
  else if n % 2 = 0 || n % 3 = 0 then
    false
  else
    let sqrtN := Nat.sqrt n
    let rec checkDivisors (i : Nat) : Bool :=
      if i > sqrtN then
        true
      else if n % i = 0 || n % (i + 2) = 0 then
        false
      else
        checkDivisors (i + 6)
    checkDivisors 5

-- Specification
def isPrimePred (n : Nat) : Prop :=
  Nat.Prime n

-- Precondition: Input must be a non-negative integer
-- This is automatically enforced by Lean's type system for Nat

-- Tests
#eval isPrime 2 -- true
#eval isPrime 4 -- false
#eval isPrime 0 -- false
#eval isPrime 7 -- true

-- Edge cases
example : isPrime 0 = false := by rfl
example : isPrime 1 = false := by rfl
example : isPrime 2 = true := by rfl
example : isPrime 3 = true := by rfl
example : isPrime 4 = false := by rfl
example : isPrime 7 = true := by rfl

-- Correctness theorem
theorem isPrime_correct (n : Nat) : isPrime n = isPrimePred n := by
  unfold isPrime isPrimePred
  cases n with
  | zero => simp [Nat.Prime]
  | succ n' =>
    cases n' with
    | zero => simp [Nat.Prime]
    | succ n'' =>
      sorry

end VeriBench.IsPrime
