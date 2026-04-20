-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsVariance
-- !benchmark @end import

-- !benchmark @start solution_aux
open Std
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def variance_imp_precond (xs : Array Float) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
def sum_func (xs : List Float) : Float :=
  xs.foldl (· + ·) 0.0

def mean_func (xs : List Float) : Float :=
  let n := xs.length.toFloat
  if n == 0.0 then 0.0 else sum_func xs / n

def variance_func (xs : List Float) : Float :=
  let n := xs.length.toFloat
  if n < 2.0 then 0.0
  else
    let mu := mean_func xs
    let ssd := xs.foldl (fun acc x => acc + (x - mu) * (x - mu)) 0.0
    ssd / (n - 1.0)
-- !benchmark @end code_aux


def variance_imp (xs : Array Float) (h_precond : variance_imp_precond (xs)) : Float :=
  -- !benchmark @start code
  Id.run do
    let n := xs.size.toFloat
    if n < 2.0 then
      return 0.0

    let mut sum_val : Float := 0.0
    for x in xs do
      sum_val := sum_val + x
    let mu := sum_val / n

    let mut ssd : Float := 0.0
    for x in xs do
      let diff := x - mu
      ssd := ssd + (diff * diff)

    return ssd / (n - 1.0)
  -- !benchmark @end code


-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux


@[reducible, simp]
def variance_imp_postcond (xs : Array Float) (result : Float) (h_precond : variance_imp_precond (xs)) :=
  -- !benchmark @start postcond
  result = variance_func xs.toList
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
-- !benchmark @end proof_aux


theorem variance_imp_spec_satisfied (xs : Array Float) (h_precond : variance_imp_precond (xs)) :
    variance_imp_postcond (xs) (variance_imp (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof