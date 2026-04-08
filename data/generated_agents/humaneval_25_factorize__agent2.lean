import Std.Data.List.Basic
import Mathlib.Data.Nat.Sqrt
import Mathlib.Tactic.Ring

/-- Return list of prime factors of given integer in the order from smallest to largest.
    Each of the factors should be listed number of times corresponding to how many times it appears in factorization.
    Input number should be equal to the product of all factors -/
def factorize (n : Nat) : List Nat :=
  let rec helper (n : Nat) (i : Nat) (acc : List Nat) : List Nat :=
    if i > n.sqrt + 1 then
      if n > 1 then n :: acc else acc
    else if n % i == 0 then
      helper (n / i) i (i :: acc)
    else
      helper n (i + 1) acc
  
  (helper n 2 []).reverse

/-- The product of all factors in the result is equal to the input number -/
def factorize_spec (n : Nat) (result : List Nat) : Prop :=
  n > 0 → result.prod = n

theorem factorize_correct (n : Nat) : factorize_spec n (factorize n) := by
  sorry

/-- Tests for factorize -/
def factorize_test : IO Unit := do
  assert! (factorize 2 == [2])
  assert! (factorize 4 == [2, 2])
  assert! (factorize 8 == [2, 2, 2])
  assert! (factorize (3 * 19) == [3, 19])
  assert! (factorize (3 * 19 * 3 * 19) == [3, 3, 19, 19])
  assert! (factorize (3 * 19 * 3 * 19 * 3 * 19) == [3, 3, 3, 19, 19, 19])
  assert! (factorize (3 * 19 * 19 * 19) == [3, 19, 19, 19])
  assert! (factorize (3 * 2 * 3) == [2, 3, 3])
  IO.println "All tests passed!"

#eval factorize_test
