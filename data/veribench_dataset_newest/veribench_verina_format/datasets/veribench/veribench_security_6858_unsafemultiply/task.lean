-- !benchmark @start import type=solution
import Mathlib
namespace IntegerOverflow

open Int
-- !benchmark @end import

-- !benchmark @start solution_aux
def INT_MIN : Int := -(2 ^ 31)
def INT_MAX : Int := 2 ^ 31 - 1

/--
Safe version: returns `none` if overflow would occur, otherwise returns `some (a * b)`.
-/
def safeMultiply (a b : Int) : Option Int :=
  let prod := a * b
  if INT_MIN ≤ prod ∧ prod ≤ INT_MAX then
    some prod
  else
    none
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def unsafeMultiply_precond (a : Int) (b : Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
-- !benchmark @end code_aux


/--
Simulates 32-bit signed integer overflow by masking the result to 32 bits.
This models the C-style behavior where overflow silently wraps using 2's complement.
-/
def unsafeMultiply (a : Int) (b : Int) (h_precond : unsafeMultiply_precond (a) (b)) : Int :=
  -- !benchmark @start code
  let raw := a * b
  -- Handle negative numbers by adding 2^32 to make them positive for bitwise operations
  let adjusted := if raw < 0 then raw + 2 ^ 32 else raw
  let masked := adjusted.toNat &&& 0xFFFFFFFF
  if masked ≥ 2 ^ 31 then
    Int.ofNat masked - 2 ^ 32
  else
    Int.ofNat masked
  -- !benchmark @end code


-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux


@[reducible, simp]
def unsafeMultiply_postcond (a : Int) (b : Int) (result : Int)
    (h_precond : unsafeMultiply_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  (∀ r, safeMultiply a b = some r → INT_MIN ≤ r ∧ r ≤ INT_MAX) ∧
    ((a * b < INT_MIN ∨ a * b > INT_MAX) → safeMultiply a b = none) ∧
    (∀ r, safeMultiply a b = some r → unsafeMultiply a b (by simp) = r) ∧
    (safeMultiply a 0 = some 0 ∧ safeMultiply 0 a = some 0)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
/-- **Safe range property**: Safe multiplication returns result within range. -/
def safe_range_prop (a b : Int) : Prop :=
  ∀ result, safeMultiply a b = some result → INT_MIN ≤ result ∧ result ≤ INT_MAX

/-- **Safe range theorem**: Safe multiplication returns result within range. -/
theorem safe_range_thm (a b : Int) : safe_range_prop a b := by
  sorry

/-- **Overflow detection property**: Overflow cases return none. -/
def overflow_detection_prop (a b : Int) : Prop :=
  (a * b < INT_MIN ∨ a * b > INT_MAX) → safeMultiply a b = none

/-- **Overflow detection theorem**: Overflow cases return none. -/
theorem overflow_detection_thm (a b : Int) : overflow_detection_prop a b := by
  sorry

/-- **Safe agreement property**: When safe returns a value, it matches unsafe. -/
def safe_agreement_prop (a b : Int) : Prop :=
  ∀ result, safeMultiply a b = some result → unsafeMultiply a b (by simp) = result

/-- **Safe agreement theorem**: When safe returns a value, it matches unsafe. -/
theorem safe_agreement_thm (a b : Int) : safe_agreement_prop a b := by
  sorry

/-- **Zero property**: Multiplication by zero is always safe. -/
def zero_prop (a : Int) : Prop :=
  safeMultiply a 0 = some 0 ∧ safeMultiply 0 a = some 0

/-- **Zero theorem**: Multiplication by zero is always safe. -/
theorem zero_thm (a : Int) : zero_prop a := by
  sorry

/-
Original auxiliary theorem kept as an auxiliary property theorem.
-/
theorem unsafeMultiply_detects_overflow (a b : Int) :
  let prod := a * b
  if INT_MIN ≤ prod ∧ prod ≤ INT_MAX then
    unsafeMultiply a b (by simp) = prod
  else
    unsafeMultiply a b (by simp) ≠ prod := by
  sorry

theorem safe_agrees_with_unsafe (a b : Int) (h : safeMultiply a b = some (a * b)) :
  unsafeMultiply a b (by simp) = a * b := by
  sorry
-- !benchmark @end proof_aux


theorem unsafeMultiply_spec_satisfied (a : Int) (b : Int) (h_precond : unsafeMultiply_precond (a) (b)) :
    unsafeMultiply_postcond (a) (b) (unsafeMultiply (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof