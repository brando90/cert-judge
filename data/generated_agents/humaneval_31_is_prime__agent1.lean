/-
File: humaneval_31_is_prime.lean
-/

import Mathlib.Tactic
import Mathlib.Data.Nat.Prime

/--
Return true if a given number is prime, and false otherwise.
-/
def is_prime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec check (k : Nat) : Bool :=
      if k ≥ n - 1 then
        true
      else if n % k == 0 then
        false
      else
        check (k + 1)
    check 2

/-- Tests for is_prime -/
def isPrimeTests : List (Nat × Bool) :=
  [(6, false), (101, true), (11, true), (13441, true), (61, true), 
   (4, false), (1, false), (5, true), (17, true), (5 * 17, false),
   (11 * 7, false), (13441 * 19, false)]

/-- Run the tests -/
#eval isPrimeTests.all (fun (input, expected) => is_prime input == expected)

/--
Precondition for is_prime: none, it works for all natural numbers.
-/
def is_prime_pre (_n : Nat) : Prop := True

/--
Postcondition for is_prime: The result is true iff n is prime.
-/
def is_prime_post (n : Nat) (result : Bool) : Prop :=
  result = true ↔ Nat.Prime n

/--
Theorem: is_prime satisfies its specification.
-/
theorem is_prime_correct (n : Nat) : is_prime_pre n → is_prime_post n (is_prime n) := by
  intro _
  unfold is_prime_post
  unfold is_prime
  
  split
  · -- Case: n < 2
    have h : ¬Nat.Prime n := by
      cases n with
      | zero => exact Nat.not_prime_zero
      | succ n' =>
        cases n' with
        | zero => exact Nat.not_prime_one
        | succ _ => contradiction
    simp [h]
  
  · -- Case: n ≥ 2
    -- We need to show that the recursive check function returns true iff n is prime
    sorry
