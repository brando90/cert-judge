```lean
import Mathlib.Tactic
import Std.Data.Nat.Basic

namespace HumanEval24

/-- 
  For a given number n, find the largest number that divides n evenly, smaller than n
-/
def largest_divisor (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 0
  | n + 1 =>
    let rec find_divisor (i : Nat) : Nat :=
      if i = 0 then 1
      else if (n + 1) % i = 0 then i
      else find_divisor (i - 1)
    find_divisor n

-- Specification
def largest_divisor_spec (n : Nat) : Nat :=
  if n ≤ 1 then 0
  else
    let rec find_largest_divisor (i : Nat) : Nat :=
      if i = 0 then 1
      else if n % i = 0 then i
      else find_largest_divisor (i - 1)
    find_largest_divisor (n - 1)

-- Tests
#eval largest_divisor 3 -- 1
#eval largest_divisor 7 -- 1
#eval largest_divisor 10 -- 5
#eval largest_divisor 100 -- 50
#eval largest_divisor 49 -- 7

theorem largest_divisor_3 : largest_divisor 3 = 1 := rfl
theorem largest_divisor_7 : largest_divisor 7 = 1 := rfl
theorem largest_divisor_10 : largest_divisor 10 = 5 := rfl
theorem largest_divisor_100 : largest_divisor 100 = 50 := rfl
theorem largest_divisor_49 : largest_divisor 49 = 7 := rfl

-- Precondition
def largest_divisor_pre (n : Nat) : Prop :=
  n > 1

-- Postcondition
def largest_divisor_post (n : Nat) (result : Nat) : Prop :=
  result < n ∧ n % result = 0 ∧ ∀ m, m < n → n % m = 0 → m ≤ result

-- Correctness theorem
theorem largest_divisor_correct (n : Nat) :
  largest_divisor_pre n → largest_divisor_post n (largest_divisor n) := by
  sorry

theorem largest_divisor_eq_spec (n : Nat) :
  largest_divisor n = largest_divisor_spec n := by
  sorry

end HumanEval24
```
