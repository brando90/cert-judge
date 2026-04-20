-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsMean
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def mean_imp_precond (xs : Array Float) : Prop :=
  -- !benchmark @start precond
  xs.size ≠ 0
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def mean_imp (xs : Array Float) (h_precond : mean_imp_precond (xs)) : Float :=
  -- !benchmark @start code
  Id.run do
    let n := xs.size.toFloat
    if n == 0.0 then
      return 0.0

    let mut total : Float := 0.0
    for x in xs do
      total := total + x

    return total / n
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def mean_imp_postcond (xs : Array Float) (result : Float) (h_precond : mean_imp_precond (xs)) :=
  -- !benchmark @start postcond
  result = mean_imp (xs) h_precond
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem mean_imp_spec_satisfied (xs : Array Float) (h_precond : mean_imp_precond (xs)) :
    mean_imp_postcond (xs) (mean_imp (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  simp [mean_imp_postcond]
  -- !benchmark @end proof