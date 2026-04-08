import Std.Data.List.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Data.Int.Basic

def factorize (n : Int) : List Int :=
  if n ≤ 1 then [] else
  let rec factorizeHelper (n : Int) (i : Int) (acc : List Int) : List Int :=
    if i * i > n then
      if n > 1 then acc ++ [n] else acc
    else if n % i == 0 then
      factorizeHelper (n / i) i (acc ++ [i])
    else
      factorizeHelper n (i + 1) acc
  factorizeHelper n 2 []

-- Specification
def isPrime (n : Int) : Bool :=
  if n ≤ 1 then false else
  let rec isPrimeHelper (i : Int) : Bool :=
    if i * i > n then true
    else if n % i == 0 then false
    else isPrimeHelper (i + 1)
  isPrimeHelper 2

def product (xs : List Int) : Int :=
  xs.foldl (· * ·) 1

-- Pre-conditions
def factorizePreCond (n : Int) : Prop :=
  n > 1

-- Post-conditions
def factorizePostCond (n : Int) (result : List Int) : Prop :=
  -- All elements in the result are prime
  (∀ x ∈ result, isPrime x = true) ∧
  -- The product of all factors equals the input number
  product result = n ∧
  -- The list is sorted in non-decreasing order
  List.sorted (· ≤ ·) result

-- Correctness theorem
theorem factorizeCorrect (n : Int) :
  factorizePreCond n → factorizePostCond n (factorize n) := by
  sorry

-- Tests
#eval factorize 2 -- [2]
#eval factorize 4 -- [2, 2]
#eval factorize 8 -- [2, 2, 2]
#eval factorize (3 * 19) -- [3, 19]
#eval factorize (3 * 19 * 3 * 19) -- [3, 3, 19, 19]
#eval factorize (3 * 19 * 3 * 19 * 3 * 19) -- [3, 3, 3, 19, 19, 19]
#eval factorize (3 * 19 * 19 * 19) -- [3, 19, 19, 19]
#eval factorize (3 * 2 * 3) -- [2, 3, 3]

theorem factorize_test_1 : factorize 2 = [2] := by rfl
theorem factorize_test_2 : factorize 4 = [2, 2] := by rfl
theorem factorize_test_3 : factorize 8 = [2, 2, 2] := by rfl
theorem factorize_test_4 : factorize (3 * 19) = [3, 19] := by rfl
theorem factorize_test_5 : factorize (3 * 19 * 3 * 19) = [3, 3, 19, 19] := by rfl
theorem factorize_test_6 : factorize (3 * 19 * 3 * 19 * 3 * 19) = [3, 3, 3, 19, 19, 19] := by rfl
theorem factorize_test_7 : factorize (3 * 19 * 19 * 19) = [3, 19, 19, 19] := by rfl
theorem factorize_test_8 : factorize (3 * 2 * 3) = [2, 3, 3] := by rfl
