-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsCorrelation
-- !benchmark @end import

-- !benchmark @start solution_aux
open Std

-- Using Float for calculation
abbrev Number := Float
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def correlation_imp_precond (xs : Array Number) (ys : Array Number) : Prop :=
  -- !benchmark @start precond
  xs.size = ys.size ∧ xs.size ≥ 2
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def correlation_imp (xs : Array Number) (ys : Array Number) (h_precond : correlation_imp_precond (xs) (ys)) : Number :=
  -- !benchmark @start code
  Id.run do
    let n := xs.size
    if n != ys.size || n < 2 then
      return 0.0

    let nf := n.toFloat
    let mut sum_x := 0.0
    let mut sum_y := 0.0
    let mut sum_xy := 0.0
    let mut sum_xx := 0.0
    let mut sum_yy := 0.0

    -- Single pass
    for i in [:n] do
      let x := xs[i]!
      let y := ys[i]!
      sum_x := sum_x + x
      sum_y := sum_y + y
      sum_xy := sum_xy + (x * y)
      sum_xx := sum_xx + (x * x)
      sum_yy := sum_yy + (y * y)

    -- Apply "Computational Formula" for variance/covariance
    -- Sxx = Σx² - (Σx)²/n
    let sxx := sum_xx - (sum_x * sum_x / nf)
    let syy := sum_yy - (sum_y * sum_y / nf)
    let sxy := sum_xy - (sum_x * sum_y / nf)

    let denom := Float.sqrt (sxx * syy)
    if denom == 0.0 then return 0.0

    return sxy / denom
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def correlation_imp_postcond (xs : Array Number) (ys : Array Number) (result : Number)
    (h_precond : correlation_imp_precond (xs) (ys)) : Prop :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem correlation_imp_spec_satisfied (xs : Array Number) (ys : Array Number)
    (h_precond : correlation_imp_precond (xs) (ys)) :
    correlation_imp_postcond (xs) (ys) (correlation_imp (xs) (ys) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof