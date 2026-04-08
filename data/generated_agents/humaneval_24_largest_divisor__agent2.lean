```lean
import Std.Data.List.Basic

/--
  For a given number n, find the largest number that divides n evenly, smaller than n
-/
def largest_divisor (n : Nat) : Nat :=
  if n ≤ 1 then
    1
  else
    let rec find_divisor (i : Nat) : Nat :=
      if i = 0 then
        1  -- Fallback, should not reach here for n > 1
      else if n % i = 0 then
        i
      else
        find_divisor (i - 1)
    find_divisor (n - 1)

/--
  Predicate specifying that the result is the largest divisor of n that is less than n
-/
def largest_divisor_spec (n : Nat) (result : Nat) : Prop :=
  result < n ∧ n % result = 0 ∧ ∀ d, d < n → n % d = 0 → d ≤ result

/--
  Theorem stating that largest_divisor satisfies its specification
-/
theorem largest_divisor_correct (n : Nat) (h : n > 0) : 
  largest_divisor_spec n (largest_divisor n) := by
  sorry

/--
  Test cases for largest_divisor
-/
def test_largest_divisor : IO Unit := do
  assert! (largest_divisor 3 = 1)
  assert! (largest_divisor 7 = 1)
  assert! (largest_divisor 10 = 5)
  assert! (largest_divisor 100 = 50)
  assert! (largest_divisor 49 = 7)
  IO.println "All tests passed!"

#eval test_largest_divisor
```
