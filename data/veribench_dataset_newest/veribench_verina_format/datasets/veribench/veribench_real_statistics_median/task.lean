-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsMedian
-- !benchmark @end import

-- !benchmark @start solution_aux
open Std
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def median_imp_precond (data : Array Rat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Safe indexing for Array -/
def nthOrZeroImp (xs : Array Rat) (idx : Nat) : Rat :=
  (xs.get? idx).getD 0
-- !benchmark @end code_aux

def median_imp (data : Array Rat) (h_precond : median_imp_precond (data)) : Rat :=
  -- !benchmark @start code
  Id.run do
    if data.isEmpty then
      return 0

    let sorted := data.qsort (· ≤ ·)
    let n := sorted.size

    if n % 2 == 1 then
      return nthOrZeroImp sorted (n / 2)
    else
      let mid := n / 2
      let left := nthOrZeroImp sorted (mid - 1)
      let right := nthOrZeroImp sorted mid
      return (left + right) / 2
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def median_imp_postcond (data : Array Rat) (result : Rat) (h_precond : median_imp_precond (data)) : Prop :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem median_imp_spec_satisfied (data : Array Rat) (h_precond : median_imp_precond (data)) :
    median_imp_postcond (data) (median_imp (data) h_precond) h_precond := by
  -- !benchmark @start proof
  simp [median_imp_postcond]
  -- !benchmark @end proof