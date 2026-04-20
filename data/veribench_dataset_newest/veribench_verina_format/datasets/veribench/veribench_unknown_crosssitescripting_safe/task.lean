-- !benchmark @start import type=solution
import Mathlib
namespace SafeCrossSiteScripting
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def SafeCrossSiteScripting.Pre_precond : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def SafeCrossSiteScripting.Pre (h_precond : SafeCrossSiteScripting.Pre_precond) : Prop :=
  -- !benchmark @start code
  True
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def SafeCrossSiteScripting.Pre_postcond (result : Prop) (h_precond : SafeCrossSiteScripting.Pre_precond) :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem SafeCrossSiteScripting.Pre_spec_satisfied (h_precond : SafeCrossSiteScripting.Pre_precond) :
    SafeCrossSiteScripting.Pre_postcond (SafeCrossSiteScripting.Pre h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof