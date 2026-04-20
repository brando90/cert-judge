-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsCovariance

open Std
-- !benchmark @end import

-- !benchmark @start solution_aux
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def benchmark_covariance_precond (x : List Rat) (y : List Rat) : Prop :=
  -- !benchmark @start precond
  x.length = y.length ∧ x.length ≥ 2
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Sum for lists of rationals. -/
def sumRat (xs : List Rat) : Rat :=
  xs.foldl (· + ·) 0

/-- Mean for lists of rationals (0 on empty, guarded by `Pre` in theorems). -/
def meanRat (xs : List Rat) : Rat :=
  let n := xs.length
  if n == 0 then 0 else sumRat xs / (n : Rat)

/-- Sample covariance for lists of rationals. -/
def covariance (x y : List Rat) : Rat :=
  let n := x.length
  if y.length != n then
    0
  else if n < 2 then
    0
  else
    let xbar := sumRat x / (n : Rat)
    let ybar := sumRat y / (n : Rat)
    let sxy :=
      (x.zip y).foldl
        (fun acc (xi, yi) => acc + (xi - xbar) * (yi - ybar)) 0
    sxy / ((n - 1) : Rat)

/-- Variance helper (used in properties and tests). -/
def variance (x : List Rat) : Rat :=
  let n := x.length
  if n < 2 then
    0
  else
    let xbar := sumRat x / (n : Rat)
    let sxx := x.foldl (fun acc xi => acc + (xi - xbar) * (xi - xbar)) 0
    sxx / ((n - 1) : Rat)
-- !benchmark @end code_aux

def benchmark_covariance (x : List Rat) (y : List Rat)
    (h_precond : benchmark_covariance_precond (x) (y)) : Rat :=
  -- !benchmark @start code
  covariance x y
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def benchmark_covariance_postcond (x : List Rat) (y : List Rat) (result : Rat)
    (h_precond : benchmark_covariance_precond (x) (y)) :=
  -- !benchmark @start postcond
  (benchmark_covariance_precond x y → covariance x y = covariance y x) ∧
    (benchmark_covariance_precond x x → covariance x x = variance x) ∧
    (∀ a b, benchmark_covariance_precond x y →
      covariance (x.map (fun v => v + a)) (y.map (fun v => v + b)) = covariance x y)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Symmetry property**: covariance is symmetric in its arguments. -/
def symmetry_prop (x y : List Rat) : Prop :=
  benchmark_covariance_precond x y → covariance x y = covariance y x

/-- **Symmetry theorem**: covariance is symmetric in its arguments. -/
theorem symmetry_thm (x y : List Rat) : symmetry_prop x y := by
  sorry

/-- **Self-variance property**: covariance with self equals variance. -/
def self_variance_prop (x : List Rat) : Prop :=
  benchmark_covariance_precond x x → covariance x x = variance x

/-- **Self-variance theorem**: covariance with self equals variance. -/
theorem self_variance_thm (x : List Rat) : self_variance_prop x := by
  sorry

/-- **Shift-invariance property**: shifting inputs does not change covariance. -/
def shift_invariance_prop (x y : List Rat) (a b : Rat) : Prop :=
  benchmark_covariance_precond x y →
    covariance (x.map (fun v => v + a)) (y.map (fun v => v + b)) = covariance x y

/-- **Shift-invariance theorem**: shifting inputs does not change covariance. -/
theorem shift_invariance_thm (x y : List Rat) (a b : Rat) : shift_invariance_prop x y a b := by
  sorry
-- !benchmark @end proof_aux

theorem benchmark_covariance_spec_satisfied (x : List Rat) (y : List Rat)
    (h_precond : benchmark_covariance_precond (x) (y)) :
    benchmark_covariance_postcond (x) (y) (benchmark_covariance (x) (y) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof