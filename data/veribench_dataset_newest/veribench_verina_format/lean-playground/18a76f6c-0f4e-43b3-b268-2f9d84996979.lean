-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution
-- No imports needed for this task
-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux
-- No auxiliary definitions needed for precond
-- !benchmark @end precond_aux

@[reducible, simp]
def myAdd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  -- The precondition is satisfied for all natural numbers
  True
  -- !benchmark @end precond


#print "###test start###"


#print "###sound plausible end###"


#print "###sound plausible inverse end###"


#print "###complete plausible end###"

