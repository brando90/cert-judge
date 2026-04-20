-- !benchmark @start import type=solution
import Mathlib
namespace PolynomialRoot
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Small epsilon value for float comparisons -/
def epsilon : Float := 1e-10
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
/--
Evaluates a polynomial at a given point x.

Given a list of coefficients [a₀, a₁, ..., aₙ], evaluates:
a₀ + a₁x + a₂x² + ... + aₙxⁿ
-/
def poly (xs : List Float) (x : Float) : Float :=
  let rec eval_at (i : Nat) (acc : Float) : Float :=
    match i with
    | 0 => acc
    | n + 1 =>
      match xs[n]? with
      | none => acc
      | some coeff => eval_at n (acc + coeff * (x ^ n.toFloat))
  eval_at xs.length 0
-- !benchmark @end precond_aux

@[reducible, simp]
def find_zero_precond (xs : List Float) (a : Float) (b : Float) : Prop :=
  -- !benchmark @start precond
  xs ≠ [] ∧ a < b ∧ poly xs a * poly xs b ≤ 0
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- (no extra auxiliary code)
-- !benchmark @end code_aux

def find_zero (xs : List Float) (a : Float) (b : Float) (fuel : Nat)
    (h_precond : find_zero_precond (xs) (a) (b)) : Float :=
  -- !benchmark @start code
  match fuel with
  | 0 => (a + b) / 2
  | fuel + 1 =>
    let mid := (a + b) / 2
    let f_mid := poly xs mid
    if Float.abs f_mid < epsilon then
      mid
    else if poly xs a * f_mid ≤ 0 then
      find_zero xs a mid fuel (by sorry)
    else
      find_zero xs mid b fuel (by sorry)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- (no extra postcondition auxiliary code)
-- !benchmark @end postcond_aux

@[reducible, simp]
def find_zero_postcond (xs : List Float) (a : Float) (b : Float) (fuel : Nat) (result : Float)
    (h_precond : find_zero_precond (xs) (a) (b)) : Prop :=
  -- !benchmark @start postcond
  (Float.abs (poly xs result) < epsilon) ∧
    (a ≤ result ∧ result ≤ b) ∧
    (∀ x, poly xs x = (xs.mapIdx (fun i c => c * (x ^ i.toFloat))).sum) ∧
    (result = result)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- (no extra proof auxiliary code)
-- !benchmark @end proof_aux

theorem find_zero_spec_satisfied (xs : List Float) (a : Float) (b : Float) (fuel : Nat)
    (h_precond : find_zero_precond (xs) (a) (b)) :
    find_zero_postcond (xs) (a) (b) (fuel) (find_zero (xs) (a) (b) (fuel) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof