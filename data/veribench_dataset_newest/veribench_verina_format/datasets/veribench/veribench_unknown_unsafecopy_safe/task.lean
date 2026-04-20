-- !benchmark @start import type=solution
import Mathlib
namespace SafeUnsafeCopy
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def Pre_precond : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def Pre (h_precond : Pre_precond) : Prop :=
  -- !benchmark @start code
  True
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def Pre_postcond (result : Prop) (h_precond : Pre_precond) :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem Pre_spec_satisfied (h_precond : Pre_precond) :
    Pre_postcond (Pre h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof