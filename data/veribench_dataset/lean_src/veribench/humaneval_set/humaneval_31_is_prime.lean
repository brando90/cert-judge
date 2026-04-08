/-!

# VeriBench – Is Prime

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## Is Prime

Implements `isPrime`, which checks if a number is prime.-/

namespace PrimeCheck

/--
**Implementation of `isPrime`.**

A prime number is a natural number greater than 1 that is only divisible by 1 and itself.
Returns true if the input number is prime, false otherwise.

## Examples

#eval isPrime 2 -- expected: true
#eval isPrime 3 -- expected: true
#eval isPrime 4 -- expected: false
#eval isPrime 5 -- expected: true
-/
partial def isPrime (n : Nat) : Bool :=
  if n < 2 then
    false
  else
    let rec checkDivisors (k : Nat) : Bool :=
      if k * k > n then
        true
      else if n % k = 0 then
        false
      else
        checkDivisors (k + 1)
    checkDivisors 2

/-!
# Tests
-/

/-- expected: true -/
example : isPrime 2 = true := by sorry
#eval isPrime 2

/-- expected: true -/
example : isPrime 3 = true := by sorry
#eval isPrime 3

/-!
# Tests: Edge Cases
-/

/-- expected: false -/
example : isPrime 4 = false := by sorry
#eval isPrime 4

/-- expected: true -/
example : isPrime 5 = true := by sorry
#eval isPrime 5

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: small prime -/
example : isPrime 7 = true := by sorry
#eval isPrime 7 -- expected: true

/-- positive: larger prime -/
example : isPrime 17 = true := by sorry
#eval isPrime 17 -- expected: true

/-- negative: 1 is not prime -/
example : ¬ (isPrime 1 = true) := by sorry
#eval (decide (isPrime 1 = true)) -- expected: false

/-- negative: composite number -/
example : ¬ (isPrime 9 = true) := by sorry
#eval (decide (isPrime 9 = true)) -- expected: false

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any natural number is valid input. -/
def Pre (n : Nat) : Prop := True

/-!
# Property Theorems
-/

/-- **Small numbers property**: Numbers less than 2 are not prime. -/
def small_numbers_prop (n : Nat) : Prop := n < 2 → isPrime n = false

/-- **Small numbers theorem**: Numbers less than 2 are not prime. -/
@[simp] theorem small_numbers_thm (n : Nat) : small_numbers_prop n := sorry

/-- **Two is prime property**: 2 is prime. -/
def two_is_prime_prop : Prop := isPrime 2 = true

/-- **Two is prime theorem**: 2 is prime. -/
@[simp] theorem two_is_prime_thm : two_is_prime_prop := sorry

/-- **Composite property**: If n has a divisor between 2 and sqrt(n), it's not prime. -/
def composite_prop (n : Nat) : Prop :=
  n ≥ 2 → (∃ k, 2 ≤ k ∧ k * k ≤ n ∧ n % k = 0) → isPrime n = false

/-- **Composite theorem**: If n has a divisor between 2 and sqrt(n), it's not prime. -/
@[simp] theorem composite_thm (n : Nat) : composite_prop n := sorry

/-- **Prime definition property**: Prime numbers have exactly two divisors. -/
def prime_definition_prop (n : Nat) : Prop :=
  isPrime n = true → n > 1 ∧ ∀ k, k ∣ n → k = 1 ∨ k = n

/-- **Prime definition theorem**: Prime numbers have exactly two divisors. -/
@[simp] theorem prime_definition_thm (n : Nat) : prime_definition_prop n := sorry

/-- **Deterministic property**: isPrime always returns the same result for the same input. -/
def deterministic_prop (n : Nat) : Prop :=
  isPrime n = isPrime n

/-- **Deterministic theorem**: isPrime always returns the same result for the same input. -/
@[simp] theorem deterministic_thm (n : Nat) : deterministic_prop n := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for isPrime. -/
def Post_prop (n : Nat) : Prop :=
  (small_numbers_prop n) ∧                               -- small_numbers_prop
  (two_is_prime_prop) ∧                                  -- two_is_prime_prop
  (composite_prop n) ∧                                   -- composite_prop
  (prime_definition_prop n) ∧                            -- prime_definition_prop
  (deterministic_prop n)                                 -- deterministic_prop

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (n : Nat) (hPre : Pre n) : Post_prop n := sorry

/-!
# Imperative Implementation
-/

/--
`isPrimeImp n` computes the same result using imperative style with explicit loops.
-/
def isPrimeImp (n : Nat) : Bool :=
  Id.run do
    if n < 2 then
      return false

    let mut k := 2
    while k * k ≤ n do
      if n % k = 0 then
        return false
      k := k + 1

    return true

/-!
# Imperative Tests
-/

/-- expected: true -/
example : isPrimeImp 2 = true := by sorry
#eval isPrimeImp 2

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: true -/
example : isPrimeImp 3 = true := by sorry
#eval isPrimeImp 3

/-- expected: false -/
example : isPrimeImp 4 = false := by sorry
#eval isPrimeImp 4

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: prime number -/
example : isPrimeImp 13 = true := by sorry
#eval isPrimeImp 13 -- expected: true

/-- negative: composite number -/
example : ¬ (isPrimeImp 15 = true) := by sorry
#eval (decide (isPrimeImp 15 = true)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem isPrime_equivalence_thm (n : Nat) :
  isPrime n = isPrimeImp n := sorry

end PrimeCheck
