/-!
# VeriBench – Prime Fibonacci Numbers

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

## Prime Fibonacci Numbers

Implements a function to find the n-th number that is both a Fibonacci number and prime.-/

namespace PrimeFib

/--
Checks if a natural number is prime.
A number is prime if it is greater than 1 and has no divisors other than 1 and itself.

## Examples

#eval isPrime 2  -- expected: true
#eval isPrime 3  -- expected: true
#eval isPrime 4  -- expected: false
#eval isPrime 1  -- expected: false
-/
def isPrime (n : Nat) : Bool :=
  if n < 2 then false
  else
    let rec checkDivisors (k : Nat) (fuel : Nat) : Bool :=
      if fuel = 0 then true
      else if k * k > n then true
      else if n % k = 0 then false
      else checkDivisors (k + 1) (fuel - 1)
    checkDivisors 2 n

/--
Computes the n-th Fibonacci number.
F(0) = 0, F(1) = 1, F(n+2) = F(n+1) + F(n)

## Examples

#eval fib 0  -- expected: 0
#eval fib 1  -- expected: 1
#eval fib 2  -- expected: 1
#eval fib 3  -- expected: 2
-/
def fib : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => fib (n + 1) + fib n

/--
**Implementation of `prime_fib`.**

`prime_fib n` returns the n-th number that is both a Fibonacci number and prime.
The sequence starts with: 2, 3, 5, 13, 89, ...

## Examples

#eval prime_fib 1  -- expected: 2
#eval prime_fib 2  -- expected: 3
#eval prime_fib 3  -- expected: 5
#eval prime_fib 4  -- expected: 13
-/
def prime_fib (n : Nat) : Nat :=
  let rec helper (count : Nat) (i : Nat) (n : Nat) (fuel : Nat) : Nat :=
    if fuel = 0 then 0
    else
      let f := fib i
      if isPrime f then
        if count + 1 = n then f
        else helper (count + 1) (i + 1) n (fuel - 1)
      else
        helper count (i + 1) n (fuel - 1)
  helper 0 3 n 1000

/-!
# Tests
-/

/-- expected: 2 -/
example : prime_fib 1 = 2 := by sorry
#eval prime_fib 1 -- expected: 2

/-- expected: 3 -/
example : prime_fib 2 = 3 := by sorry
#eval prime_fib 2 -- expected: 3

/-!
# Tests: Edge Cases
-/

/-- expected: 5 -/
example : prime_fib 3 = 5 := by sorry
#eval prime_fib 3 -- expected: 5

/-- expected: 13 -/
example : prime_fib 4 = 13 := by sorry
#eval prime_fib 4 -- expected: 13

/-- expected: 89 -/
example : prime_fib 5 = 89 := by sorry
#eval prime_fib 5 -- expected: 89

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: sequence is increasing -/
example : prime_fib 1 < prime_fib 2 := by sorry
#eval (prime_fib 1, prime_fib 2) -- expected: (2, 3)

/-- positive test: all results are prime -/
example : isPrime (prime_fib 3) = true := by sorry
#eval isPrime (prime_fib 3) -- expected: true

/-- negative test: not all primes are in the sequence -/
example : ¬ (prime_fib 3 = 7) := by sorry

/-- negative test: sequence is not dense -/
example : prime_fib 4 > prime_fib 3 + 1 := by sorry

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Input must be positive. -/
def Pre (n : Nat) : Prop := n > 0

/-!
# Property Theorems
-/

/-- **Positivity property**: Result is always positive for positive input. -/
def positivity_prop (n : Nat) : Prop :=
  n > 0 → prime_fib n > 0

/-- **Positivity theorem**: Result is always positive for positive input. -/
@[simp] theorem positivity_thm (n : Nat) : positivity_prop n := sorry

/-- **Primality property**: Result is always prime. -/
def primality_prop (n : Nat) : Prop :=
  n > 0 → isPrime (prime_fib n)

/-- **Primality theorem**: Result is always prime. -/
@[simp] theorem primality_thm (n : Nat) : primality_prop n := sorry

/-- **Fibonacci property**: Result is a Fibonacci number. -/
def fibonacci_property_prop (n : Nat) : Prop :=
  n > 0 → ∃ k, fib k = prime_fib n

/-- **Fibonacci property theorem**: Result is a Fibonacci number. -/
@[simp] theorem fibonacci_property_thm (n : Nat) : fibonacci_property_prop n := sorry

/-- **Monotonicity property**: Sequence is strictly increasing. -/
def monotonicity_prop (n : Nat) : Prop :=
  n > 0 → prime_fib n < prime_fib (n + 1)

/-- **Monotonicity theorem**: Sequence is strictly increasing. -/
@[simp] theorem monotonicity_thm (n : Nat) : monotonicity_prop n := sorry

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for prime_fib. -/
def Post_prop (n : Nat) : Prop :=
  (positivity_prop n) ∧                                  -- positivity property
  (primality_prop n) ∧                                   -- primality property
  (fibonacci_property_prop n) ∧                          -- fibonacci property
  (monotonicity_prop n)                                  -- monotonicity property

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre‑condition implies the post‑condition. -/
theorem correctness_thm (n : Nat) (hPre : Pre n) : Post_prop n := sorry

/-!
# Imperative Implementation
-/

/--
`prime_fibImp n` computes the same result using imperative style with a while loop.
-/
def prime_fibImp (n : Nat) : Nat :=
  Id.run do
    let mut count := 0
    let mut i := 3
    while count < n do
      let f := fib i
      if isPrime f then
        count := count + 1
        if count = n then
          return f
      i := i + 1
    return 0  -- Should never reach here for valid n

/-!
# Imperative Tests
-/

/-- expected: 2 -/
example : prime_fibImp 1 = 2 := by sorry
#eval prime_fibImp 1 -- expected: 2

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: 3 -/
example : prime_fibImp 2 = 3 := by sorry
#eval prime_fibImp 2 -- expected: 3

/-!
# Positive / Negative Test‑Suite
-/

/-- positive test: matches functional version -/
example : prime_fibImp 3 = 5 := by sorry
#eval prime_fibImp 3 -- expected: 5

/-- negative test: not zero for valid input -/
example : ¬ (prime_fibImp 1 = 0) := by sorry

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem prime_fib_equivalence_thm (n : Nat) :
  prime_fib n = prime_fibImp n := sorry

end PrimeFib
