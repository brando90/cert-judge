import Mathlib

/-
This file defines the `isPrime` function that determines if a number is prime.
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

/-- A snake-case alias matching the name of the Python task. -/
def is_prime (n : Nat) : Bool := isPrime n

/-- `isPrime` agrees with the standard natural-number primality predicate. -/
theorem isPrime_true_iff_prime (n : Nat) :
    isPrime n = true ↔ Nat.Prime n := by
  sorry

theorem isPrime_eq_decide_prime (n : Nat) :
    isPrime n = decide (Nat.Prime n) := by
  sorry

/-- Divisibility characterization of the result of `isPrime`. -/
theorem isPrime_spec (n : Nat) :
    isPrime n = true ↔ n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → ¬(k ∣ n) := by
  sorry

/-- Equivalent characterization using remainders. -/
theorem isPrime_mod_spec (n : Nat) :
    isPrime n = true ↔
      n ≥ 2 ∧ ∀ k, 2 ≤ k → k < n → n % k ≠ 0 := by
  sorry

theorem isPrime_false_iff_not_prime (n : Nat) :
    isPrime n = false ↔ ¬ Nat.Prime n := by
  sorry

theorem isPrime_false_iff_small_or_has_divisor (n : Nat) :
    isPrime n = false ↔
      n < 2 ∨ ∃ k, 2 ≤ k ∧ k < n ∧ n % k = 0 := by
  sorry

theorem isPrime_true_implies_ge_two (n : Nat) :
    isPrime n = true → n ≥ 2 := by
  intro h
  by_contra hge
  have hn : n < 2 := Nat.lt_of_not_ge hge
  simp [isPrime, hn] at h

theorem isPrime_product_false_of_factors_gt_one (a b : Nat)
    (ha : 1 < a) (hb : 1 < b) :
    isPrime (a * b) = false := by
  sorry

/-- Task-facing correctness statement for the snake-case alias. -/
theorem is_prime_correct (n : Nat) :
    is_prime n = decide (Nat.Prime n) := by
  simpa [is_prime] using isPrime_eq_decide_prime n

theorem isPrime_of_prime (n : Nat) (h : Nat.Prime n) :
    isPrime n = true :=
  (isPrime_true_iff_prime n).2 h

theorem isPrime_false_of_not_prime (n : Nat) (h : ¬ Nat.Prime n) :
    isPrime n = false :=
  (isPrime_false_iff_not_prime n).2 h

theorem isPrime_zero : isPrime 0 = false := by native_decide

theorem isPrime_one : isPrime 1 = false := by native_decide

theorem isPrime_two : isPrime 2 = true := by native_decide

theorem isPrime_three : isPrime 3 = true := by native_decide

theorem isPrime_four : isPrime 4 = false := by native_decide

theorem isPrime_five : isPrime 5 = true := by native_decide

theorem isPrime_six : isPrime 6 = false := by native_decide

theorem isPrime_nine : isPrime 9 = false := by native_decide

theorem isPrime_eleven : isPrime 11 = true := by native_decide

theorem isPrime_seventeen : isPrime 17 = true := by native_decide

theorem isPrime_twentyfive : isPrime 25 = false := by native_decide

theorem isPrime_61 : isPrime 61 = true := by native_decide

theorem isPrime_97 : isPrime 97 = true := by native_decide

theorem isPrime_101 : isPrime 101 = true := by native_decide

theorem isPrime_121 : isPrime 121 = false := by native_decide

theorem isPrime_13441 : isPrime 13441 = true := by native_decide

theorem isPrime_5_times_17 : isPrime (5 * 17) = false := by native_decide

theorem isPrime_11_times_7 : isPrime (11 * 7) = false := by native_decide

theorem isPrime_13441_times_19 : isPrime (13441 * 19) = false := by native_decide

/-- A finite conformance check against the standard primality predicate. -/
def isPrime_small_range_check : Bool :=
  (List.range 128).all (fun n => isPrime n == decide (Nat.Prime n))

theorem isPrime_small_range_agrees :
    isPrime_small_range_check = true := by
  native_decide

/-- Tests for the `isPrime` function. -/
def isPrime_tests : List (Nat × Bool) := [
  (0, false),
  (1, false),
  (2, true),
  (3, true),
  (4, false),
  (5, true),
  (6, false),
  (9, false),
  (11, true),
  (17, true),
  (25, false),
  (61, true),
  (97, true),
  (101, true),
  (121, false),
  (13441, true),
  (5 * 17, false),
  (11 * 7, false),
  (13441 * 19, false)
]

theorem isPrime_tests_pass :
    isPrime_tests.all (fun (input, expected) => isPrime input == expected) = true := by
  native_decide

/- Run all tests -/
#eval isPrime_tests.all (fun (input, expected) => isPrime input == expected)
