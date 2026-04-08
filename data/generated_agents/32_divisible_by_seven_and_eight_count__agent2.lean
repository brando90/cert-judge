import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic
import Mathlib.Data.Int.ModEq

def isDivisibleBy (n : Int) (d : Int) : Bool :=
  n % d = 0

def isDivisibleByBoth (n : Int) (d₁ d₂ : Int) : Bool :=
  isDivisibleBy n d₁ && isDivisibleBy n d₂

/--
Count numbers divisible by both 7 and 8 in a list of integers.

Edge cases:
- Empty list returns 0.
-/
def count_div_by_7_and_8 (xs : List Int) : Nat :=
  xs.foldl (fun count x => if isDivisibleByBoth x 7 8 then count + 1 else count) 0

/-- Predicate that checks if a number is divisible by both 7 and 8 -/
def isDivisibleBy7And8 (n : Int) : Prop :=
  n % 7 = 0 ∧ n % 8 = 0

/-- Specification for count_div_by_7_and_8 -/
def count_div_by_7_and_8_spec (xs : List Int) : Nat :=
  xs.filter (fun x => isDivisibleBy7And8 x).length

theorem isDivisibleBy_iff_isDivisibleByBoth (n d₁ d₂ : Int) :
    isDivisibleByBoth n d₁ d₂ = true ↔ isDivisibleBy n d₁ = true ∧ isDivisibleBy n d₂ = true := by
  simp [isDivisibleByBoth, Bool.and_eq_true]

theorem isDivisibleBy_iff_mod_eq_zero (n d : Int) :
    isDivisibleBy n d = true ↔ n % d = 0 := by
  simp [isDivisibleBy]

theorem isDivisibleByBoth_iff_isDivisibleBy7And8 (n : Int) :
    isDivisibleByBoth n 7 8 = true ↔ isDivisibleBy7And8 n := by
  simp [isDivisibleByBoth, isDivisibleBy7And8, isDivisibleBy_iff_mod_eq_zero, Bool.and_eq_true]

/-- Correctness theorem for count_div_by_7_and_8 -/
theorem count_div_by_7_and_8_correct (xs : List Int) :
    count_div_by_7_and_8 xs = count_div_by_7_and_8_spec xs := by
  sorry

/-- Tests for count_div_by_7_and_8 -/
def test_count_div_by_7_and_8 : Bool :=
  count_div_by_7_and_8 [56, 14, 28, 112] = 2 &&
  count_div_by_7_and_8 [1, 2, 3, 4] = 0 &&
  count_div_by_7_and_8 [0, 56, 84] = 2 &&
  count_div_by_7_and_8 [] = 0

#eval test_count_div_by_7_and_8  -- Should evaluate to true
