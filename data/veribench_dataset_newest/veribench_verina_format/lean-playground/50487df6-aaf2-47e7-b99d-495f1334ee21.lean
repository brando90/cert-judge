-- !benchmark @start import type=type=test
import Plausible
import Mathlib
-- !benchmark @end import

-- !benchmark @start import type=task

-- !benchmark @end import

-- !benchmark @start import type=llm_solution

-- !benchmark @end import

-- !benchmark @start task_aux

-- !benchmark @end task_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myAdd_precond (a : Nat) (b : Nat) : Prop :=
  -- !benchmark @start precond
  true
  -- !benchmark @end precond


#print "###test start###"



#print "<precond_test_decidable>0</precond_test_decidable>"

#guard decide (myAdd_precond (1) (2))

#print "<precond_test_decidable>1</precond_test_decidable>"

#guard decide (myAdd_precond (0) (0))

#print "<precond_test_decidable>2</precond_test_decidable>"

#guard decide (myAdd_precond (2) (3))

#print "<precond_test_decidable>3</precond_test_decidable>"

#guard decide (myAdd_precond (7) (0))

#print "<precond_test_decidable>4</precond_test_decidable>"

#guard decide (myAdd_precond (4) (1))
#print "###sound decidable end###"

