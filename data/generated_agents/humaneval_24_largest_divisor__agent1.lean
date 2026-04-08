```lean
import Mathlib.Tactic
import Mathlib.Data.Nat.Basic

/--
  For a given number n, find the largest number that divides n evenly, smaller than n
-/
def largest_divisor (n : Nat) : Nat :=
  match n with
  | 0 => 0  -- Handle edge case
  | 1 => 1  -- Handle edge case
  | n+1 =>
    let rec find_divisor (i : Nat) : Nat :=
      if i = 0 then
        1  -- Default to 1 if no other divisor found
      else if n % i = 0 then
        i
      else
        find_divisor (i-1)
    find_divisor n

/-- Specification: largest_divisor returns the largest divisor of n that is less than n -/
def largest_divisor_spec (n : Nat) : Nat :=
  if n ≤ 1 then
    n
  else
    Nat.find (fun d => d < n ∧ n % d = 0 ∧ ∀ k, k < n → n % k = 0 → k ≤ d)

/-- Precondition: n must be positive -/
def largest_divisor_pre (n : Nat) : Prop :=
  n > 0

/-- Postcondition: result is a divisor of n, less than n, and no larger divisor exists -/
def largest_divisor_post (n : Nat) (result : Nat) : Prop :=
  result < n ∧ n % result = 0 ∧ ∀ k, k < n → n % k = 0 → k ≤ result

theorem largest_divisor_correct (n : Nat) (h : largest_divisor_pre n) :
  largest_divisor_post n (largest_divisor n) :=
  sorry

/-- Tests for largest_divisor -/
def largest_divisor_test : IO Unit := do
  assert! (largest_divisor 3 = 1)
  assert! (largest_divisor 7 = 1)
  assert! (largest_divisor 10 = 5)
  assert! (largest_divisor 100 = 50)
  assert! (largest_divisor 49 = 7)
  IO.println "All tests passed!"
```
