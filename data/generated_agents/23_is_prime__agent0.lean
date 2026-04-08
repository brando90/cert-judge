import Mathlib.Tactic
import Mathlib.Data.Nat.Prime

namespace VeriBench

/-- Check if a non-negative integer is prime.

A prime number is a natural number greater than 1 that is not divisible by any positive integer other than 1 and itself.

Edge cases:
- 0 and 1 are not prime.
- Negative inputs are invalid and raise error.
-/
def is_prime (n : Int) : Bool :=
  if n ≤ 1 then
    false
  else if n ≤ 3 then
    true
  else if n % 2 = 0 || n % 3 = 0 then
    false
  else
    let sqrt_n := Int.sqrt n
    let rec check (i : Int) : Bool :=
      if i > sqrt_n then
        true
      else if n % i = 0 || n % (i + 2) = 0 then
        false
      else
        check (i + 6)
    check 5

/-- Precondition: input must be a non-negative integer -/
def is_prime.pre (n : Int) : Prop := n ≥ 0

/-- Postcondition: returns true if and only if n is a prime number -/
def is_prime.post (n : Int) (result : Bool) : Prop :=
  result = Nat.Prime n.toNat

/-- Basic test case -/
example : is_prime 7 = true := by decide

/-- Edge case: 0 is not prime -/
example : is_prime 0 = false := by decide

/-- Edge case: 1 is not prime -/
example : is_prime 1 = false := by decide

/-- Composite number test -/
example : is_prime 4 = false := by decide

/-- Correctness theorem for is_prime -/
theorem is_prime_correct (n : Int) (h : is_prime.pre n) : is_prime.post n (is_prime n) := by
  unfold is_prime.post
  unfold is_prime.pre at h
  
  -- Case analysis
  cases n with
  | ofNat n => 
    -- Handle natural number case
    simp
    sorry
  | negSucc n =>
    -- Handle negative case (contradicts precondition)
    have : ¬(Int.negSucc n ≥ 0) := by simp
    contradiction
    
end VeriBench
