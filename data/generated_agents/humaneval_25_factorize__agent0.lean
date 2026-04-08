import Mathlib.Data.Nat.Factors
import Mathlib.Data.Nat.Prime
import Mathlib.Tactic.Ring

namespace VeriBench.HumanEval.Problem25

/-- 
Return list of prime factors of given integer in the order from smallest to largest.
Each of the factors should be listed number of times corresponding to how many times it appears in factorization.
Input number should be equal to the product of all factors
-/
def factorize (n : Nat) : List Nat :=
  if n ≤ 1 then []
  else
    let rec loop (n : Nat) (i : Nat) (acc : List Nat) : List Nat :=
      if i * i > n then
        if n > 1 then n :: acc else acc
      else if n % i == 0 then
        loop (n / i) i (i :: acc)
      else
        loop n (i + 1) acc
    
    (loop n 2 []).reverse

/-- The product of the factors equals the original number -/
def factorize_spec (n : Nat) (result : List Nat) : Prop :=
  n > 0 → result.prod = n

/-- All elements in the result are prime numbers -/
def factorize_spec2 (result : List Nat) : Prop :=
  ∀ p ∈ result, Nat.Prime p

/-- The factors are sorted in non-decreasing order -/
def factorize_spec3 (result : List Nat) : Prop :=
  result.Sorted (· ≤ ·)

theorem factorize_correct (n : Nat) : 
  factorize_spec n (factorize n) ∧ 
  factorize_spec2 (factorize n) ∧ 
  factorize_spec3 (factorize n) := by
  sorry

/-- Test cases -/
def test_factorize : IO Unit := do
  assert! (factorize 2 = [2])
  assert! (factorize 4 = [2, 2])
  assert! (factorize 8 = [2, 2, 2])
  assert! (factorize (3 * 19) = [3, 19])
  assert! (factorize (3 * 19 * 3 * 19) = [3, 3, 19, 19])
  assert! (factorize (3 * 19 * 3 * 19 * 3 * 19) = [3, 3, 3, 19, 19, 19])
  assert! (factorize (3 * 19 * 19 * 19) = [3, 19, 19, 19])
  assert! (factorize (3 * 2 * 3) = [2, 3, 3])
  IO.println "All tests passed!"

end VeriBench.HumanEval.Problem25
